"""Stateful, counterfactual replay of previously frozen one-step forecasts.

This is an offline *model*: no traffic is routed and utility is not observed.
Each policy owns its placement, readiness, and cooldown state. Forecast rows are
shared across policies and were produced before the corresponding observation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Sequence

from .experiment_records import configuration_digest
from .models import Forecast, GateAction
from .policies import PolicyVariant, run_policy
from .scenarios import ScenarioDefinition, load_scenario

EVIDENCE_CLASS = "offline stateful counterfactual replay; no packet routing or measured cost"
INPUT_CLASS = "offline trace-driven controller decision pilot; no packet replay or migration"


def _forecast(row: dict, horizon: int) -> Forecast:
    return Forecast(
        float(row["forecast_point_mbps"]),
        float(row["forecast_lower_mbps"]),
        float(row["forecast_upper_mbps"]),
        horizon,
        str(row["model"]),
    )


def _validate_and_group(record: dict, scenario: ScenarioDefinition) -> dict[str, list[dict]]:
    if record.get("evidence_class") != INPUT_CLASS:
        raise ValueError("expected an immutable offline trace decision record")
    if record.get("scenario_config_sha256") != configuration_digest(scenario.payload):
        raise ValueError("scenario digest differs from original decision study")
    if record.get("scenario_seed_for_modeled_inputs") not in scenario.seeds:
        raise ValueError("scenario seed differs from original decision study")
    count = record.get("split_counts", {}).get("test")
    interval = record.get("sampling_interval_seconds")
    capacity = record.get("assumed_source_capacity_mbps")
    if type(count) is not int or count < 1 or type(interval) is not int or interval < 1:
        raise ValueError("invalid test count or sampling interval")
    if not isinstance(capacity, (int, float)) or not math.isfinite(capacity) or capacity <= 0:
        raise ValueError("invalid assumed source capacity")
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in record.get("decisions", []):
        grouped[row["model"], row["policy"]].append(row)
    models = {model for model, _ in grouped}
    if not models:
        raise ValueError("missing forecast models")
    result = {}
    for model in sorted(models):
        reference = None
        for variant in PolicyVariant:
            rows = sorted(grouped.get((model, variant.value), []), key=lambda row: row["test_index"])
            if [row["test_index"] for row in rows] != list(range(count)):
                raise ValueError("missing or duplicate model/policy observations")
            shared = [(
                row["timestamp_utc"], row["prior_observed_mbps"],
                row["forecast_point_mbps"], row["forecast_lower_mbps"],
                row["forecast_upper_mbps"], row["actual_next_mbps"],
            ) for row in rows]
            if reference is None:
                reference = shared
                result[model] = rows
            elif shared != reference:
                raise ValueError("paired policy forecasts or observations disagree")
    return result


def replay(record: dict, scenario: ScenarioDefinition, *, cooldown_slots: int = 2) -> dict:
    """Replay each model/policy once; capacity and action costs are explicitly modeled."""
    if type(cooldown_slots) is not int or cooldown_slots < 0:
        raise ValueError("cooldown_slots must be a non-negative integer")
    models = _validate_and_group(record, scenario)
    interval = record["sampling_interval_seconds"]
    source_capacity = float(record["assumed_source_capacity_mbps"])
    base = scenario.build_run(record["scenario_seed_for_modeled_inputs"])
    nodes = {node.node_id: node for node in base.candidates}
    if len(nodes) != len(base.candidates):
        raise ValueError("candidate node identifiers must be unique")
    if not scenario.synthetic_inputs:
        raise ValueError("nontraffic inputs must be declared modeled/synthetic")
    terms = base.decision_input.benefit_terms
    rows_out = []
    summaries = []
    for model, rows in models.items():
        for variant in PolicyVariant:
            current = "modeled-source"
            capacity = source_capacity
            warm: set[str] = set()
            synced: set[str] = set()
            next_eligible = 0
            migrations = prewarms = syncs = cooldown_waits = 0
            overload_mbps_seconds = served_mbit = migration_cost_utility = 0.0
            for index, row in enumerate(rows):
                forecast = _forecast(row, interval)
                actual = float(row["actual_next_mbps"])
                previous = float(row["prior_observed_mbps"])
                if not math.isfinite(actual) or actual < 0 or not math.isfinite(previous) or previous < 0:
                    raise ValueError("traffic values must be finite and non-negative")
                source_before = current
                capacity_before = capacity
                cooldown_before = max(0, next_eligible - index)
                candidates = [node for node in base.candidates if node.node_id != current]
                action = GateAction.WAIT
                reason = "no alternative candidate"
                selected = None
                mode = "none"
                if index < next_eligible:
                    reason = "replay cooldown: no migration action permitted"
                    cooldown_waits += 1
                elif candidates:
                    width = min(1.0, forecast.width_fraction(capacity))
                    decision_input = replace(
                        base.decision_input,
                        source_capacity_mbps=capacity,
                        forecast=forecast,
                        target_warm=False,
                        state_synchronized=False,
                        threshold_context=replace(
                            base.decision_input.threshold_context,
                            uncertainty_fraction=width,
                            cooldown_active=False,
                        ),
                    )
                    run = replace(base, current_utilization=min(1.0, previous / capacity),
                                  decision_input=decision_input, candidates=candidates)
                    # A side-effect-free probe identifies the variant's own selected target.
                    probe = run_policy(variant, run)
                    selected = probe.decision.selected_node_id
                    ready_run = replace(run, decision_input=replace(
                        decision_input, target_warm=selected in warm,
                        state_synchronized=selected in synced,
                    ))
                    outcome = run_policy(variant, ready_run)
                    action, reason, mode = outcome.decision.action, outcome.decision.reason, outcome.migration_mode
                    if action in (GateAction.PREWARM, GateAction.SYNC, GateAction.COMMIT) and selected is None:
                        raise ValueError("controller requested migration action without target")
                    if action is GateAction.PREWARM:
                        warm.add(selected)
                        prewarms += 1
                        migration_cost_utility += terms.operational_overhead
                    elif action is GateAction.SYNC:
                        if selected not in warm:
                            raise ValueError("synchronization without a warm target")
                        synced.add(selected)
                        syncs += 1
                        migration_cost_utility += terms.operational_overhead
                    elif action is GateAction.COMMIT:
                        if variant not in (PolicyVariant.REACTIVE, PolicyVariant.PREDICTION_ONLY):
                            if selected not in warm or selected not in synced:
                                raise ValueError("warm migration committed without readiness")
                        current = selected
                        capacity = nodes[selected].spare_capacity_mbps
                        if capacity <= 0:
                            raise ValueError("selected target has no spare capacity")
                        synced.clear()  # Sync is invalid after any route/state transition.
                        migrations += 1
                        next_eligible = index + cooldown_slots + 1
                        migration_cost_utility += (
                            terms.migration_cost + terms.disruption_penalty + terms.operational_overhead
                        )
                # Decision precedes observation. Commit is modeled as effective in this slot;
                # this optimistic convention is disclosed and is not packet-path throughput.
                excess = max(0.0, actual - capacity) * interval
                overload_mbps_seconds += excess
                served_mbit += min(actual, capacity) * interval
                rows_out.append({
                    "model": model, "policy": variant.value, "test_index": index,
                    "timestamp_utc": row["timestamp_utc"],
                    "source_before": source_before, "source_after": current,
                    "capacity_before_mbps": capacity_before, "capacity_after_mbps": capacity,
                    "selected_node_id": selected, "action": action.value, "reason": reason,
                    "migration_mode": mode, "cooldown_remaining_before": cooldown_before,
                    "actual_next_mbps": actual, "modeled_excess_mbps_seconds": excess,
                })
            summaries.append({
                "model": model, "policy": variant.value, "opportunities": len(rows),
                "simulated_migrations": migrations, "simulated_prewarms": prewarms,
                "simulated_syncs": syncs, "cooldown_wait_slots": cooldown_waits,
                "modeled_excess_mbps_seconds": overload_mbps_seconds,
                "modeled_capacity_limited_served_mbit": served_mbit,
                "modeled_action_cost_utility": migration_cost_utility,
                "final_placement": current,
            })
    return {
        "evidence_class": EVIDENCE_CLASS,
        "traffic_source": record["traffic_source"],
        "traffic_csv_sha256": record["traffic_csv_sha256"],
        "scenario_id": scenario.scenario_id,
        "scenario_config_sha256": configuration_digest(scenario.payload),
        "sampling_interval_seconds": interval,
        "forecast_models": sorted(models),
        "assumed_initial_capacity_mbps": source_capacity,
        "cooldown_slots": cooldown_slots,
        "assumptions": [
            "All nontraffic inputs and the initial source capacity are modeled, not measured.",
            "Targets start cold and unsynchronized; PREWARM and SYNC each consume one observation slot.",
            "Simple reactive/prediction-only baselines commit without readiness gates; cold-migration ablation still follows controller readiness gates.",
            "A commit changes modeled capacity before that slot's observed load; this is optimistic and not measured throughput.",
            "Candidate load, risk, carbon, health and benefit terms stay fixed; no measured energy or attack reduction is inferred.",
            "Action-cost utility sums scenario migration, disruption and per-action overhead terms; units are not currency or measured cost.",
            "The initial modeled source is not an eligible return target; alternate targets are static scenario candidates.",
        ],
        "summary": summaries,
        "steps": rows_out,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decision-record", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cooldown-slots", type=int, default=2)
    args = parser.parse_args(argv)
    raw = args.decision_record.read_bytes()
    result = replay(json.loads(raw), load_scenario(args.scenario), cooldown_slots=args.cooldown_slots)
    result["decision_record_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"output": str(args.output), "steps": len(result["steps"]),
                      "evidence_class": result["evidence_class"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
