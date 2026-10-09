"""Deterministic modeled decision grid; never a packet-path performance claim."""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import asdict, replace
import hashlib
from itertools import product
import json
from pathlib import Path
from .models import Forecast
from .policies import PolicyVariant, run_policy
from .scenarios import load_scenario

AXES = {"width_fraction": [0.02, 0.2, 0.6], "state_size_mb": [1, 100, 1000],
        "operational_benefit": [0.3, 0.8, 1.5], "candidate_carbon": [40, 300, 600],
        "candidate_risk": [0.05, 0.4, 0.9]}


def evaluate(base, axes=None):
    axes = AXES if axes is None else axes
    if set(axes) != set(AXES) or any(not values for values in axes.values()):
        raise ValueError("all non-empty sensitivity axes required")
    rows = []
    for values in product(*(axes[key] for key in AXES)):
        context = dict(zip(AXES, values))
        width = context["width_fraction"]
        original = base.decision_input
        point = original.forecast.point_mbps
        half = width * original.source_capacity_mbps / 2
        forecast = Forecast(point, max(0, point-half), point+half,
                            original.forecast.horizon_seconds, "modeled-sensitivity-v1")
        inp = replace(original, forecast=forecast,
                      benefit_terms=replace(original.benefit_terms, operational_benefit=context["operational_benefit"]),
                      threshold_context=replace(original.threshold_context, uncertainty_fraction=width,
                                                state_size_mb=context["state_size_mb"]))
        candidates = [replace(base.candidates[0], carbon_gco2_per_kwh=context["candidate_carbon"],
                              security_risk=context["candidate_risk"]), *base.candidates[1:]]
        run = replace(base, decision_input=inp, candidates=candidates)
        input_hash = hashlib.sha256(json.dumps(asdict(run), sort_keys=True).encode()).hexdigest()
        for policy in PolicyVariant:
            decision = run_policy(policy, run).decision
            selected = next((node for node in candidates if node.node_id == decision.selected_node_id), None)
            unsafe = selected is not None and (not selected.allowed or selected.security_risk > run.placement_policy.max_security_risk)
            if unsafe:
                raise AssertionError("policy selected a hard-prohibited candidate")
            rows.append({"inputs": context, "input_sha256": input_hash, "policy": policy.value,
                         "decision": decision.as_record(),
                         "selected_modeled_carbon": selected.carbon_gco2_per_kwh if selected else None,
                         "selected_modeled_risk": selected.security_risk if selected else None})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    scenario = load_scenario(args.scenario)
    rows = evaluate(scenario.build_run(scenario.seeds[0]))
    args.output.mkdir(parents=True, exist_ok=False)
    record = {"evidence_class": "deterministic modeled sensitivity; independent ready-target opportunities",
              "axes": AXES, "scenario_sha256": hashlib.sha256(args.scenario.read_bytes()).hexdigest(),
              "rows": rows}
    raw = json.dumps(record, indent=2, sort_keys=True)
    (args.output / "records.json").write_text(raw, encoding="utf-8")
    lines = ["# Modeled sensitivity audit", "", "No traffic, power or attack outcomes are measured.", "",
             "| Policy | Opportunities | COMMIT | WAIT | PREWARM | Other |", "|---|---:|---:|---:|---:|---:|"]
    for policy in PolicyVariant:
        counts = Counter(row["decision"]["action"] for row in rows if row["policy"] == policy.value)
        other = sum(value for key, value in counts.items() if key not in {"COMMIT", "WAIT", "PREWARM"})
        lines.append(f'| {policy.value} | {sum(counts.values())} | {counts["COMMIT"]} | {counts["WAIT"]} | {counts["PREWARM"]} | {other} |')
    lines.extend(["", "All policies retained the same hard risk ceiling and quarantine constraints.",
                  "These are decision counts, not migration frequency in a time-evolving system.",
                  "Carbon/risk candidate scores vary; benefit credits remain independently modeled inputs.",
                  "Raw records SHA-256: " + hashlib.sha256(raw.encode()).hexdigest(), ""])
    (args.output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"records": len(rows), "hard_constraint_violations": 0}))


if __name__ == "__main__":
    main()
