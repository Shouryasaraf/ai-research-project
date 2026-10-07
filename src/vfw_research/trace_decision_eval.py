"""Offline, leakage-safe controller decision study driven by a traffic trace.

Every policy sees the same one-step forecast and prior observed traffic. Each
opportunity starts from the same ready target; no migration is executed here.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from .experiment_records import configuration_digest
from .forecasting import (
    AdaptiveEwmaResidualForecaster,
    EwmaConformalForecaster,
    RollingMeanConformalForecaster,
    time_ordered_split,
)
from .policies import PolicyVariant, run_policy
from .scenarios import ScenarioDefinition, load_scenario
from .trace_adapter import ImportedTrace, TraceKind, load_trace


def _train_quantile(values: tuple[float, ...], fraction: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1)]


def evaluate_trace_decisions(trace: ImportedTrace, scenario: ScenarioDefinition) -> dict:
    if trace.kind is not TraceKind.TRAFFIC:
        raise ValueError("decision evaluation requires a traffic trace")
    if not scenario.synthetic_inputs:
        raise ValueError("non-traffic scenario inputs must be explicitly modeled/synthetic")
    values = tuple(point.value for point in trace.points)
    split = time_ordered_split(list(values))
    capacity = _train_quantile(split.train, 0.9)
    if capacity <= 0:
        raise ValueError("training-derived source capacity must be positive")
    base_run = scenario.build_run(scenario.seeds[0])
    if not base_run.decision_input.target_warm or not base_run.decision_input.state_synchronized:
        raise ValueError("offline independent-opportunity study requires a ready, synchronized target")
    rows = []
    summaries = []
    for name, model in (
        ("rolling_mean_conformal", RollingMeanConformalForecaster(window=5, alpha=0.1)),
        ("ewma_conformal", EwmaConformalForecaster(smoothing=0.4, alpha=0.1)),
        ("adaptive_ewma_residual_exploratory", AdaptiveEwmaResidualForecaster(
            smoothing=0.4, alpha=0.1, residual_window=30
        )),
    ):
        model.fit(split.train, split.calibration)
        last_observed = split.calibration[-1]
        model_rows = []
        test_start = len(split.train) + len(split.calibration)
        for offset, actual in enumerate(split.test):
            forecast = model.predict(trace.sampling_interval_seconds)
            width_fraction = min(1.0, forecast.width_fraction(capacity))
            decision_input = replace(
                base_run.decision_input,
                source_capacity_mbps=capacity,
                forecast=forecast,
                threshold_context=replace(
                    base_run.decision_input.threshold_context,
                    uncertainty_fraction=width_fraction,
                ),
            )
            run = replace(
                base_run,
                current_utilization=min(1.0, last_observed / capacity),
                decision_input=decision_input,
            )
            timestamp = trace.points[test_start + offset].observed_utc.isoformat()
            for variant in PolicyVariant:
                decision = run_policy(variant, run).decision
                model_rows.append({
                    "test_index": offset,
                    "timestamp_utc": timestamp,
                    "model": name,
                    "policy": variant.value,
                    "prior_observed_mbps": last_observed,
                    "forecast_point_mbps": forecast.point_mbps,
                    "forecast_lower_mbps": forecast.lower_mbps,
                    "forecast_upper_mbps": forecast.upper_mbps,
                    "actual_next_mbps": actual,
                    "actual_exceeds_assumed_source_capacity": actual > capacity,
                    "action": decision.action.value,
                    "reason": decision.reason,
                    "selected_node_id": decision.selected_node_id,
                    "net_benefit_utility": decision.net_benefit,
                    "threshold_utility": decision.adaptive_threshold,
                    "invariant_violations": list(decision.invariant_violations),
                })
            # Reveal the held-out observation only after every policy has decided.
            model.observe(actual)
            last_observed = actual
        rows.extend(model_rows)
        for variant in PolicyVariant:
            selected = [row for row in model_rows if row["policy"] == variant.value]
            actions = Counter(row["action"] for row in selected)
            summaries.append({
                "model": name,
                "policy": variant.value,
                "opportunities": len(selected),
                "action_counts": dict(sorted(actions.items())),
                "commit_rate": actions["COMMIT"] / len(selected),
                "commits_without_same_step_capacity_exceedance": sum(
                    row["action"] == "COMMIT" and not row["actual_exceeds_assumed_source_capacity"]
                    for row in selected
                ),
                "capacity_exceedances_without_same_step_commit": sum(
                    row["action"] != "COMMIT" and row["actual_exceeds_assumed_source_capacity"]
                    for row in selected
                ),
            })
    return {
        "evidence_class": "offline trace-driven controller decision pilot; no packet replay or migration",
        "traffic_source": trace.source,
        "traffic_csv_sha256": trace.csv_sha256,
        "traffic_provenance": {
            "license": trace.license,
            "version": trace.version,
            "retrieved_utc": trace.retrieved_utc.isoformat(),
            "preprocessing": trace.preprocessing,
            "missing_data_policy": trace.missing_data_policy,
        },
        "scenario_id": scenario.scenario_id,
        "scenario_seed_for_modeled_inputs": scenario.seeds[0],
        "scenario_config_sha256": configuration_digest(scenario.payload),
        "modeled_nontraffic_inputs": True,
        "synthetic_traffic_inputs": False,
        "sampling_interval_seconds": trace.sampling_interval_seconds,
        "forecast_horizon_seconds": trace.sampling_interval_seconds,
        "split_counts": {
            "train": len(split.train), "calibration": len(split.calibration), "test": len(split.test)
        },
        "assumed_source_capacity_mbps": capacity,
        "capacity_rule": "90th percentile of training traffic only; hypothetical stress-test capacity",
        "readiness_rule": "independent decisions with a ready, synchronized modeled target; no state transitions",
        "causality_rule": "predict and decide for each next test sample before observing it; update model afterward",
        "summary": summaries,
        "decisions": rows,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = evaluate_trace_decisions(
        load_trace(args.trace_csv, args.provenance), load_scenario(args.scenario)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "decisions": len(result["decisions"]),
                      "evidence_class": result["evidence_class"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
