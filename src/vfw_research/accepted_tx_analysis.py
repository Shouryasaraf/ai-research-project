"""Validate and summarize the frozen static-path transmit-signal diagnostic."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Sequence

from .recovery_report import verify_capture
from .tcp_wire_diagnostic import _source_archive_matches

FAMILIES = ("step", "steady", "bursts", "trend", "flash")
SEEDS = (173, 179)
POLICY = "static_no_migration"
TRIGGER_MBPS = 0.8
SOURCE_CAPACITY_MBPS = 1.0


def classify(rows: list[dict], field: str) -> dict:
    counts = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}
    for row in rows:
        planned = row["scheduled_mbps"] > SOURCE_CAPACITY_MBPS
        hit = row[field] >= TRIGGER_MBPS
        counts[("T" if planned == hit else "F") + ("P" if hit else "N")] += 1
    return counts


def _trial_rows(record: dict, family: str) -> list[dict]:
    if (record["status"] != "completed" or record.get("leftover_namespaces")
            or record["policy"] != POLICY or record["seed"] not in SEEDS
            or record["source"] != {"kind": "seeded synthetic demand", "family": family,
                                     "seed": record["seed"]}
            or len(record["samples"]) != 12 or record["transitions"]):
        raise ValueError("trial identity, lifecycle or sample count invalid")
    events = record["traffic_events"]
    if not events or any(not event["success"] for event in events):
        raise ValueError("sensor diagnostic requires zero application errors")
    start = record["traffic_started_monotonic"]
    result = []
    for step, sample in enumerate(record["samples"]):
        end = sample["observed_monotonic"]
        if sample["step"] != step or end <= start or sample["errors"]:
            raise ValueError("invalid sample interval")
        accepted = sum(event["payload_bytes"] for event in events
                       if event["accepted_by_socket_monotonic"] is not None
                       and start <= event["accepted_by_socket_monotonic"] < end)
        completed = [event for event in events if start <= event["finished_monotonic"] < end]
        if (accepted != sample["accepted_tx_payload_bytes"]
                or len(completed) != sample["completed_requests"]
                or not math.isclose(sample["duration_seconds"], end - start, abs_tol=1e-5)
                or not math.isclose(sample["accepted_tx_mbps"], accepted * 8 / 1e6 / (end-start), abs_tol=1e-8)
                or not math.isclose(sample["goodput_mbps"], sum(event["payload_bytes"] for event in completed) * 8 / 1e6 / (end-start), abs_tol=1e-8)):
            raise ValueError("sample telemetry does not reproduce from final events")
        result.append({"family": family, "seed": record["seed"], "step": step,
                       "scheduled_mbps": sample["scheduled_mbps"],
                       "accepted_tx_mbps": sample["accepted_tx_mbps"],
                       "goodput_mbps": sample["goodput_mbps"],
                       "planned_overload": sample["scheduled_mbps"] > SOURCE_CAPACITY_MBPS})
        start = end
    return result


def analyze(batches: list[Path]) -> dict:
    if len(batches) != len(FAMILIES):
        raise ValueError("exactly five family batches required")
    all_rows = []
    evidence = []
    for family, batch in zip(FAMILIES, batches):
        manifest_path = batch / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (manifest["family"] != family or manifest["seeds"] != list(SEEDS)
                or manifest["policies"] != [POLICY] or manifest["steps"] != 12
                or manifest["flows"] != 3 or not manifest["capture"]
                or manifest["trace_sha256"] is not None):
            raise ValueError("batch differs from frozen protocol")
        _source_archive_matches(batch, manifest["code_sha256"])
        paths = sorted(batch.glob("*/record.json"))
        expected = {f"s{seed}-{POLICY}" for seed in SEEDS}
        if len(paths) != 2 or {path.parent.name for path in paths} != expected:
            raise ValueError("missing or extra trial")
        trial_hashes = {}
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            if (record["code_sha256"] != manifest["code_sha256"]
                    or path.parent.name != f's{record["seed"]}-{record["policy"]}'):
                raise ValueError("trial source or identity mismatch")
            if not verify_capture(path.parent, record["packet_observation"])["comparison_valid"]:
                raise ValueError("endpoint captures invalid")
            all_rows.extend(_trial_rows(record, family))
            trial_hashes[path.parent.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        evidence.append({"family": family, "batch": batch.name,
                         "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                         "source_sha256": manifest["code_sha256"],
                         "trial_record_sha256": trial_hashes})
    if len(all_rows) != 120:
        raise ValueError("expected all 120 samples")
    groups = [("all", all_rows)] + [(family, [row for row in all_rows if row["family"] == family])
                                   for family in FAMILIES]
    summary = []
    for name, rows in groups:
        planned = [row for row in rows if row["planned_overload"]]
        normal = [row for row in rows if not row["planned_overload"]]
        summary.append({"group": name, "samples": len(rows), "planned_overload_samples": len(planned),
                        "accepted_trigger": classify(rows, "accepted_tx_mbps"),
                        "completed_trigger": classify(rows, "goodput_mbps"),
                        "mean_absolute_planned_minus_accepted_mbps": statistics.fmean(abs(row["scheduled_mbps"] - row["accepted_tx_mbps"]) for row in rows),
                        "mean_absolute_planned_minus_completed_mbps": statistics.fmean(abs(row["scheduled_mbps"] - row["goodput_mbps"]) for row in rows),
                        "mean_accepted_minus_completed_planned_overload_mbps": statistics.fmean(row["accepted_tx_mbps"] - row["goodput_mbps"] for row in planned) if planned else None,
                        "mean_accepted_minus_completed_planned_nonoverload_mbps": statistics.fmean(row["accepted_tx_mbps"] - row["goodput_mbps"] for row in normal) if normal else None})
    return {"evidence_class": "captured single-host synthetic sensor diagnostic; not a controller comparison",
            "threshold_mbps": TRIGGER_MBPS, "planned_capacity_mbps": SOURCE_CAPACITY_MBPS,
            "boundary": "Scheduled load is an exogenous intended-rate label, not measured offered wire traffic. Socket acceptance and completed goodput are response-gated.",
            "evidence": evidence, "summary": summary, "rows": all_rows}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batches", type=Path, nargs=5, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    result = analyze(args.batches)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (args.output / "samples.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["rows"][0]))
        writer.writeheader()
        writer.writerows(result["rows"])
    print(json.dumps({"output": str(args.output), "samples": len(result["rows"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
