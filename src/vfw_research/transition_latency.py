"""Validate captured trials and describe RTT before/after a route commit.

The comparison is descriptive. Windows exclude in-flight requests and are not
causal estimates of migration downtime or a counterfactual no-migration RTT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from .live_analysis import percentile
from .recovery_report import verify_capture
from .tcp_wire_diagnostic import _source_archive_matches


def stratify(record: dict) -> dict:
    if record.get("status") != "completed" or record.get("leftover_namespaces"):
        raise ValueError("only completed, cleaned trials can be stratified")
    transitions = [row for row in record.get("transitions", []) if row.get("route_committed")]
    if len(transitions) > 1:
        raise ValueError("multiple commits require a separate phase definition")
    if not transitions:
        return {"route_commits": 0, "before": None, "after": None,
                "excluded_in_flight_successes": 0}
    start, end = transitions[0]["started_monotonic"], transitions[0]["finished_monotonic"]
    if (not all(type(value) in (int, float) and math.isfinite(value) for value in (start, end))
            or end < start):
        raise ValueError("invalid route-transition timestamps")
    before, after = [], []
    excluded = 0
    for event in record.get("traffic_events", []):
        if not event["success"]:
            continue
        sent, finished, rtt = (event["sent_monotonic"], event["finished_monotonic"],
                               event["rtt_ms"])
        if (not all(type(value) in (int, float) and math.isfinite(value)
                    for value in (sent, finished, rtt)) or sent > finished or rtt < 0):
            raise ValueError("invalid successful request timing")
        if finished < start:
            before.append(rtt)
        elif sent > end:
            after.append(rtt)
        else:
            excluded += 1
    return {"route_commits": 1,
            "transition_duration_seconds_including_sync_or_route_work": end - start,
            "before": {"successes": len(before), "rtt_p95_ms": percentile(before, .95)},
            "after": {"successes": len(after), "rtt_p95_ms": percentile(after, .95)},
            "excluded_in_flight_successes": excluded}


def analyze_batch(batch: Path) -> dict:
    manifest_path = batch / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest.get("capture"):
        raise ValueError("batch must have endpoint captures")
    _source_archive_matches(batch, manifest["code_sha256"])
    expected = {f's{seed}-{policy}' for seed in manifest["seeds"]
                for policy in manifest["policies"]}
    paths = sorted(batch.glob("*/record.json"))
    if {path.parent.name for path in paths} != expected or len(paths) != len(expected):
        raise ValueError("incomplete or unexpected batch")
    rows = []
    for path in paths:
        raw = path.read_bytes()
        record = json.loads(raw)
        if (record.get("code_sha256") != manifest["code_sha256"]
                or path.parent.name != f's{record["seed"]}-{record["policy"]}'):
            raise ValueError("record identity or source fingerprint mismatch")
        if not verify_capture(path.parent, record["packet_observation"])["comparison_valid"]:
            raise ValueError("invalid endpoint packet capture")
        rows.append({"policy": record["policy"], "seed": record["seed"],
                     "record_sha256": hashlib.sha256(raw).hexdigest(), **stratify(record)})
    return {"evidence_class": "validated descriptive pre/post request-RTT diagnostic; not outage or causal effect",
            "batch": batch.name,
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "boundary": "Before: request finishes before transition start. After: request starts after transition end. In-flight successes excluded. No-commit trials have no phase split.",
            "trials": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze_batch(args.batch)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"trials": len(report["trials"]), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
