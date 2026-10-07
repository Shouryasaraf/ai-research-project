"""Chronological forecast evaluation on reproducible synthetic workload traces."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from dataclasses import asdict
from pathlib import Path

from .forecasting import (
    EwmaConformalForecaster,
    RollingMeanConformalForecaster,
    evaluate_one_step,
    time_ordered_split,
)
from .workloads import WorkloadFamily, generate_workload
from .trace_adapter import ImportedTrace, TraceKind, load_trace


def evaluate_family(family: WorkloadFamily, *, seed: int, length: int = 240) -> dict:
    values = generate_workload(family, seed=seed, length=length)
    result = _evaluate_values(values, sampling_interval_seconds=60)
    return {
        **result,
        "evidence_class": "synthetic held-out one-step forecast evaluation",
        "family": family.value,
        "seed": seed,
        "synthetic_inputs": True,
    }


def evaluate_imported_trace(trace: ImportedTrace) -> dict:
    if trace.kind is not TraceKind.TRAFFIC:
        raise ValueError("forecast evaluation accepts only traffic traces in Mbps")
    result = _evaluate_values(
        tuple(point.value for point in trace.points),
        sampling_interval_seconds=trace.sampling_interval_seconds,
    )
    return {
        **result,
        "evidence_class": "imported traffic-trace forecast evaluation; authenticity not independently verified",
        "synthetic_inputs": False,
        "source_provenance": {
            "source": trace.source,
            "license": trace.license,
            "version": trace.version,
            "retrieved_utc": trace.retrieved_utc.isoformat(),
            "preprocessing": trace.preprocessing,
            "missing_data_policy": trace.missing_data_policy,
            "csv_sha256": trace.csv_sha256,
        },
    }


def _evaluate_values(values: tuple[float, ...], *, sampling_interval_seconds: int) -> dict:
    split = time_ordered_split(list(values))
    trace_bytes = json.dumps(values, separators=(",", ":")).encode("utf-8")
    results = {}
    for name, model in (
        ("rolling_mean_conformal", RollingMeanConformalForecaster(window=5, alpha=0.1)),
        ("ewma_conformal", EwmaConformalForecaster(smoothing=0.4, alpha=0.1)),
    ):
        model.fit(split.train, split.calibration)
        metrics = evaluate_one_step(
            model, split.test, horizon_seconds=sampling_interval_seconds
        )
        results[name] = {
            **asdict(metrics),
            "absolute_coverage_error": abs(metrics.interval_coverage - 0.9),
            "mean_interval_width_fraction_of_base_capacity": metrics.mean_interval_width / 100.0,
            "model_version": model.predict(60).model_version,
        }
    return {
        "sampling_interval_seconds": sampling_interval_seconds,
        "forecast_horizon_seconds": sampling_interval_seconds,
        "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
        "split_counts": {
            "train": len(split.train),
            "calibration": len(split.calibration),
            "test": len(split.test),
        },
        "evaluation_rule": "one-step forecast, observe true next value, then update point state; radius fixed from calibration",
        "nominal_coverage": 0.9,
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "models": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--family", choices=[item.value for item in WorkloadFamily])
    source.add_argument("--trace-csv", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--length", type=int, default=240)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.trace_csv:
        if args.provenance is None or args.seed is not None:
            parser.error("--trace-csv requires --provenance and must not use --seed")
        result = evaluate_imported_trace(load_trace(args.trace_csv, args.provenance))
    else:
        if args.seed is None or args.provenance is not None:
            parser.error("--family requires --seed and must not use --provenance")
        result = evaluate_family(WorkloadFamily(args.family), seed=args.seed, length=args.length)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "family": args.family, "seed": args.seed,
                      "evidence_class": result["evidence_class"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
