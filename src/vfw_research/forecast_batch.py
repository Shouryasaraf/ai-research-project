"""Immutable multi-family synthetic forecast pilot and paired summary."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Sequence

from .analysis import _bootstrap_mean_ci
from .forecast_evaluation import evaluate_family
from .workloads import WorkloadFamily


def summarize_forecasts(records: Sequence[dict]) -> dict:
    if not records:
        raise ValueError("no forecast records")
    groups: dict[str, list[dict]] = {}
    seen: set[tuple[str, int]] = set()
    for row in records:
        if row.get("evidence_class") != "synthetic held-out one-step forecast evaluation":
            raise ValueError("mixed evidence class in forecast batch")
        key = (str(row["family"]), int(row["seed"]))
        if key in seen:
            raise ValueError(f"duplicate family/seed: {key}")
        seen.add(key)
        groups.setdefault(key[0], []).append(row)
    families = []
    for family in sorted(groups):
        rows = sorted(groups[family], key=lambda row: row["seed"])
        model_names = set(rows[0]["models"])
        if any(set(row["models"]) != model_names for row in rows):
            raise ValueError(f"inconsistent models for {family}")
        models = {}
        for name in sorted(model_names):
            mae = [float(row["models"][name]["mae"]) for row in rows]
            coverage = [float(row["models"][name]["interval_coverage"]) for row in rows]
            width = [float(row["models"][name]["mean_interval_width"]) for row in rows]
            models[name] = {
                "mean_mae_mbps": statistics.fmean(mae),
                "mean_interval_coverage": statistics.fmean(coverage),
                "minimum_seed_coverage": min(coverage),
                "mean_interval_width_mbps": statistics.fmean(width),
                "mae_bootstrap_ci95": list(_bootstrap_mean_ci(mae)),
            }
        paired = {}
        if {"ewma_conformal", "rolling_mean_conformal"} <= model_names:
            differences = [
                float(row["models"]["ewma_conformal"]["mae"])
                - float(row["models"]["rolling_mean_conformal"]["mae"])
                for row in rows
            ]
            paired = {
                "mean_mae_difference_ewma_minus_rolling_mbps": statistics.fmean(differences),
                "paired_bootstrap_ci95": list(_bootstrap_mean_ci(differences)),
            }
        families.append({
            "family": family,
            "seeds": [int(row["seed"]) for row in rows],
            "models": models,
            "paired_comparison": paired,
        })
    return {
        "evidence_class": "synthetic held-out forecast pilot; no measured network traffic",
        "record_count": len(records),
        "nominal_coverage": 0.9,
        "families": families,
        "interpretation": "Descriptive pilot only; bootstrap resamples seeds within each family.",
    }


def run_batch(output_directory: Path, *, seeds: Sequence[int], length: int = 240) -> Path:
    if not seeds or len(set(seeds)) != len(seeds) or any(seed < 0 for seed in seeds):
        raise ValueError("seeds must be distinct non-negative integers")
    output_directory.mkdir(parents=True, exist_ok=False)
    records = []
    for family in WorkloadFamily:
        for seed in seeds:
            row = evaluate_family(family, seed=seed, length=length)
            path = output_directory / f"{family.value}-seed-{seed}.json"
            with path.open("x", encoding="utf-8") as handle:
                json.dump(row, handle, indent=2, sort_keys=True)
                handle.write("\n")
            records.append(row)
    summary_path = output_directory / "summary.json"
    with summary_path.open("x", encoding="utf-8") as handle:
        json.dump(summarize_forecasts(records), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=list(range(10)))
    parser.add_argument("--length", type=int, default=240)
    args = parser.parse_args()
    path = run_batch(args.output_directory, seeds=args.seeds, length=args.length)
    print(json.dumps({"summary": str(path), "seeds": args.seeds}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
