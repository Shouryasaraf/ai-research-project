"""Offline GB-region forecast replay for placement preference, not emissions."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .policies import PolicyVariant, run_policy
from .scenarios import load_scenario
from .trace_adapter import ImportedTrace, TraceKind, load_trace


def evaluate(north: ImportedTrace, london: ImportedTrace, scenario) -> dict:
    for trace in (north, london):
        if trace.kind is not TraceKind.CARBON or trace.unit != "gCO2/kWh":
            raise ValueError("two carbon-intensity traces required")
        if trace.sampling_interval_seconds != 1800 or len(trace.points) != 48:
            raise ValueError("each trace must contain one complete half-hourly UTC day")
        if trace.license != "NESO Carbon Intensity API, CC BY 4.0; attribution required":
            raise ValueError("NESO CC BY 4.0 provenance required")
    start = north.points[0].observed_utc
    if start != datetime(start.year, start.month, start.day, tzinfo=timezone.utc):
        raise ValueError("regional replay must start at UTC midnight")
    end = start + timedelta(days=1)
    for trace, region_id in ((north, 1), (london, 13)):
        expected_source = ("https://api.carbonintensity.org.uk/regional/intensity/"
                           f"{start:%Y-%m-%d}T00:00Z/{end:%Y-%m-%d}T00:00Z/regionid/{region_id}")
        if trace.source != expected_source:
            raise ValueError("unexpected NESO source region or date")
        if [point.observed_utc for point in trace.points] != [start + timedelta(minutes=30 * i) for i in range(48)]:
            raise ValueError("regional replay has missing or irregular UTC slots")
    if north.csv_sha256 == london.csv_sha256 or any(
        first.observed_utc != second.observed_utc for first, second in zip(north.points, london.points)
    ):
        raise ValueError("two distinct, aligned regional signals required")
    if not scenario.synthetic_inputs:
        raise ValueError("non-carbon scenario inputs must be marked modeled")
    base = scenario.build_run(scenario.seeds[0])
    if len(base.candidates) < 3 or not base.candidates[2].allowed is False:
        raise ValueError("expected two eligible modeled candidates and a prohibited control")
    rows = []
    for first, second in zip(north.points, london.points):
        candidates = [replace(base.candidates[0], carbon_gco2_per_kwh=first.value),
                      replace(base.candidates[1], carbon_gco2_per_kwh=second.value),
                      base.candidates[2]]
        run = replace(base, candidates=candidates)
        decisions = {}
        for variant in (PolicyVariant.FULL, PolicyVariant.CARBON_UNAWARE):
            decision = run_policy(variant, run).decision
            if decision.selected_node_id == candidates[2].node_id:
                raise AssertionError("hard-prohibited node selected")
            decisions[variant.value] = {"action": decision.action.value,
                                        "selected_node_id": decision.selected_node_id,
                                        "reason": decision.reason}
        rows.append({"timestamp_utc": first.observed_utc.isoformat(),
                     "north_scotland_forecast_gco2_per_kwh": first.value,
                     "london_forecast_gco2_per_kwh": second.value,
                     "decisions": decisions})
    different = sum(row["decisions"][PolicyVariant.FULL.value]["selected_node_id"] !=
                    row["decisions"][PolicyVariant.CARBON_UNAWARE.value]["selected_node_id"]
                    for row in rows)
    counts = {variant.value: dict(sorted(Counter(
        row["decisions"][variant.value]["selected_node_id"] or "none" for row in rows
    ).items())) for variant in (PolicyVariant.FULL, PolicyVariant.CARBON_UNAWARE)}
    return {"evidence_class": "offline placement preference with externally sourced regional carbon forecasts; no deployment or emissions measurement",
            "carbon_signal_type": "historical API regional forecast, not metered vFW power or realized grid intensity",
            "carbon_sources": {"north_scotland": north.source, "london": london.source},
            "carbon_csv_sha256": {"north_scotland": north.csv_sha256, "london": london.csv_sha256},
            "scenario_sha256": hashlib.sha256(json.dumps(scenario.payload, sort_keys=True).encode()).hexdigest(),
            "modeled_inputs": ["node capacity", "node load", "CPU/memory headroom", "latency", "risk", "benefit terms", "traffic forecast", "source capacity"],
            "opportunities": len(rows), "different_candidate_choices": different,
            "candidate_counts": counts, "hard_prohibited_choices": 0, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--north-csv", type=Path, required=True)
    parser.add_argument("--north-provenance", type=Path, required=True)
    parser.add_argument("--london-csv", type=Path, required=True)
    parser.add_argument("--london-provenance", type=Path, required=True)
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path,
                        help="optional compact, tracked JSON summary path")
    args = parser.parse_args()
    result = evaluate(load_trace(args.north_csv, args.north_provenance),
                      load_trace(args.london_csv, args.london_provenance),
                      load_scenario(args.scenario))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    if args.summary_output is not None:
        compact = {key: value for key, value in result.items() if key != "rows"}
        compact["raw_records_sha256"] = hashlib.sha256(args.output.read_bytes()).hexdigest()
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        with args.summary_output.open("x", encoding="utf-8") as handle:
            json.dump(compact, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(json.dumps({"output": str(args.output), "opportunities": result["opportunities"],
                      "different_candidate_choices": result["different_candidate_choices"],
                      "candidate_counts": result["candidate_counts"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
