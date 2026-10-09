"""Measured application metrics and paired descriptive live-pilot summaries."""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import hashlib
from pathlib import Path
import zipfile

from .analysis import _bootstrap_mean_ci


def percentile(values: list[float], fraction: float) -> float | None:
    return sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)] if values else None


def qdisc_drop_delta(record: dict) -> int | None:
    """Root source/target output queue drops, NOT end-to-end packet loss."""
    snapshots = record.get("network", [])
    if len(snapshots) < 2:
        return None
    total = 0
    for node in ("source_qdisc", "target_qdisc"):
        before = [item for item in snapshots[0].get(node, []) if item.get("root")]
        after = [item for item in snapshots[-1].get(node, []) if item.get("root")]
        if len(before) != 1 or len(after) != 1:
            return None
        first, last = before[0], after[0]
        if any(first.get(key) != last.get(key) for key in ("kind", "handle")):
            return None
        a, b = first.get("drops"), last.get("drops")
        if type(a) is not int or type(b) is not int or a < 0 or b < a:
            return None
        total += b - a
    return total


def trial_metrics(record: dict) -> dict:
    if record["status"] != "completed" or record.get("leftover_namespaces"):
        raise ValueError("only completed, cleaned-up trials have valid outcome metrics")
    events = record["traffic_events"]
    elapsed = record["traffic_finished_monotonic"] - record["traffic_started_monotonic"]
    if elapsed <= 0 or not events:
        raise ValueError("invalid traffic observation interval")
    completed = [event for event in events if event["success"]]
    observation = record.get("packet_observation")
    if observation is not None and not observation.get("comparison_valid"):
        raise ValueError("invalid endpoint capture cannot support outcome metrics")
    directions = observation["directions"] if observation is not None else None
    latencies = [event["rtt_ms"] for event in completed]
    gaps = []
    for flow in sorted({event["flow_id"] for event in events}):
        finished = sorted(e["finished_monotonic"] for e in completed if e["flow_id"] == flow)
        gaps.extend(b - a for a, b in zip(finished, finished[1:]))
    return {
        "goodput_mbps": sum(e["payload_bytes"] for e in completed) * 8 / 1e6 / elapsed,
        "requests": len(events), "successful_requests": len(completed),
        "request_failure_fraction": (len(events) - len(completed)) / len(events),
        "disrupted_flows": len({e["flow_id"] for e in events if not e["success"]}),
        "rtt_p50_ms": percentile(latencies, .5), "rtt_p95_ms": percentile(latencies, .95),
        "rtt_p99_ms": percentile(latencies, .99),
        "maximum_success_gap_seconds_including_pacing": max(gaps, default=0.0),
        "route_commits": sum(t.get("route_committed", False) for t in record["transitions"]),
        "state_sync_seconds": sum(t.get("state_sync", {}).get("duration_seconds", 0) for t in record["transitions"]),
        "state_snapshot_serialized_bytes": sum(t.get("state_sync", {}).get("serialized_source_bytes", 0) for t in record["transitions"]),
        "controller_cpu_seconds": record["controller_cpu_seconds"],
        "controller_maxrss_kib": record["controller_maxrss_kib"],
        "packet_loss_fraction": None,
        "observed_forward_packet_deficit_fraction": (directions[0]["observed_packet_deficit_fraction"]
                                                     if directions else None),
        "observed_reverse_packet_deficit_fraction": (directions[1]["observed_packet_deficit_fraction"]
                                                     if directions else None),
        "observed_forward_missing_instances": directions[0]["missing_receiver_instances"] if directions else None,
        "observed_forward_sent_instances": directions[0]["sent_packet_instances"] if directions else None,
        "observed_reverse_missing_instances": directions[1]["missing_receiver_instances"] if directions else None,
        "observed_reverse_sent_instances": directions[1]["sent_packet_instances"] if directions else None,
        "observed_output_queue_drops": qdisc_drop_delta(record),
        "migration_interruption_seconds": None,
    }


def summarize(records: list[dict]) -> dict:
    keys = [(row["policy"], row["seed"]) for row in records]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate policy/seed record")
    metrics = [{"policy": row["policy"], "seed": row["seed"], **trial_metrics(row)}
               for row in records if row["status"] == "completed" and not row.get("leftover_namespaces")]
    policies = []
    for name in sorted({row["policy"] for row in records}):
        rows = [row for row in metrics if row["policy"] == name]
        policies.append({"policy": name, "completed": len(rows),
            "failed": sum(row["policy"] == name for row in records) - len(rows),
            "metrics": {field: {"mean": statistics.fmean(row[field] for row in rows),
                                "median": statistics.median(row[field] for row in rows),
                                "sample_standard_deviation": statistics.stdev(row[field] for row in rows) if len(rows) > 1 else None}
                        for field in ("goodput_mbps", "request_failure_fraction", "rtt_p95_ms", "route_commits")
                        if rows and all(row[field] is not None for row in rows)}})
    paired = []
    full = {row["seed"]: row for row in metrics if row["policy"] == "full_proposed_controller"}
    all_seeds = {row["seed"] for row in records}
    plans = {}
    for row in records:
        seed = row["seed"]
        if seed in plans and plans[seed] != row["plan_sha256"]:
            raise ValueError("paired policies have different traffic plans")
        plans[seed] = row["plan_sha256"]
    for name in sorted({row["policy"] for row in records} - {"full_proposed_controller"}):
        baseline = {row["seed"]: row for row in metrics if row["policy"] == name}
        shared = sorted(full.keys() & baseline.keys())
        if not shared:
            continue
        differences = [full[seed]["goodput_mbps"] - baseline[seed]["goodput_mbps"] for seed in shared]
        paired.append({"baseline": name, "paired_trials": len(shared),
                       "excluded_or_missing_pairs": len(all_seeds - set(shared)),
                       "goodput_difference_full_minus_baseline_mbps": statistics.fmean(differences),
                       "descriptive_paired_bootstrap_ci95": list(_bootstrap_mean_ci(differences))
                       if len(shared) > 1 else None})
    has_capture = any(row.get("packet_observation") is not None for row in records)
    return {"evidence_class": "descriptive single-host live pilot; application-level measurements",
            "policies": policies, "paired_goodput": paired, "trials": metrics,
            "limitations": ["Observed packet-instance deficits are between two lab capture points, not a universal loss rate."
                            if has_capture else "No packet capture: packet loss is unmeasured.",
                            "Response gaps include intentional pacing and are not downtime.",
                            "One alternate target cannot isolate placement-quality effects.",
                            "Carbon/risk are modeled and not physical observations."]}


def write_summary(batch: Path, output: Path) -> dict:
    paths = sorted(batch.glob("*/record.json"))
    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    if not records:
        raise ValueError("no live trial records")
    manifest = json.loads((batch / "manifest.json").read_text(encoding="utf-8"))
    expected = {(policy, seed) for policy in manifest["policies"] for seed in manifest["seeds"]}
    actual = {(row["policy"], row["seed"]) for row in records}
    if actual != expected:
        raise ValueError("incomplete or unexpected batch records; do not summarize as a complete batch")
    if any(row["code_sha256"] != manifest["code_sha256"] for row in records):
        raise ValueError("record code digest differs from batch manifest")
    if manifest.get("capture"):
        from .recovery_report import verify_capture
        archive_path = batch / "executed-source.zip"
        digest = hashlib.sha256()
        with zipfile.ZipFile(archive_path) as archive:
            if archive.testzip() is not None:
                raise ValueError("executed source archive damaged")
            for name in archive.namelist():
                digest.update(name.encode())
                digest.update(archive.read(name))
        if digest.hexdigest() != manifest["code_sha256"]:
            raise ValueError("executed source archive does not match batch fingerprint")
        for path, record in zip(paths, records):
            if "packet_observation" not in record:
                raise ValueError("captured batch record lacks packet observation")
            observation = verify_capture(path.parent, record["packet_observation"])
            if not observation["comparison_valid"]:
                raise ValueError("captured batch has invalid paired observation")
    summary = summarize(records)
    summary["provenance"] = {"manifest": manifest,
        "raw_record_sha256": {str(path.relative_to(batch)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in paths}}
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    with (output / "trial_metrics.csv").open("x", newline="", encoding="utf-8") as handle:
        if summary["trials"]:
            writer = csv.DictWriter(handle, fieldnames=list(summary["trials"][0]))
            writer.writeheader()
            writer.writerows(summary["trials"])
    (output / "results.md").write_text(render_report(summary), encoding="utf-8")
    return summary


def render_report(summary: dict) -> str:
    lines = ["# Live pilot results", "", "Generated from immutable trial records; not a confirmatory study.", "",
             "| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |",
             "|---|---:|---:|---:|---:|---:|"]
    for row in summary["policies"]:
        metrics = row["metrics"]
        cells = [f'{metrics[key]["mean"]:.6f}' if key in metrics else "unmeasured"
                 for key in ("goodput_mbps", "request_failure_fraction", "rtt_p95_ms")]
        lines.append(f'| {row["policy"]} | {row["completed"]} | {row["failed"]} | ' + " | ".join(cells) + " |")
    lines.extend(["", "## Paired goodput differences", "",
                  "Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.", ""])
    for pair in summary["paired_goodput"]:
        lines.append(f'- Versus {pair["baseline"]}: {pair["goodput_difference_full_minus_baseline_mbps"]:.6f} Mbps '
                     f'(n={pair["paired_trials"]}; interval={pair["descriptive_paired_bootstrap_ci95"]}).')
    if any(row["observed_forward_packet_deficit_fraction"] is not None for row in summary["trials"]):
        lines.extend(["", "## Captured endpoint packet-instance deficits", "",
                      "| Policy / seed | Forward missing/sent | Reverse missing/sent |",
                      "|---|---:|---:|"])
        for row in summary["trials"]:
            forward = row["observed_forward_packet_deficit_fraction"]
            reverse = row["observed_reverse_packet_deficit_fraction"]
            lines.append(f'| {row["policy"]} / {row["seed"]} | '
                         f'{row["observed_forward_missing_instances"]}/{row["observed_forward_sent_instances"]} | '
                         f'{row["observed_reverse_missing_instances"]}/{row["observed_reverse_sent_instances"]} |'
                         if forward is not None and reverse is not None
                         else f'| {row["policy"]} / {row["seed"]} | unmeasured | unmeasured |')
    lines.extend(["", "## Limits", "", *["- " + item for item in summary["limitations"]],
                  "- RTT summarizes successful requests only; failures must be read alongside it.",
                  "- Repeated external-trace trials reuse one trace segment and are not independent workloads.", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_summary(args.batch, args.output)["policies"], indent=2))
