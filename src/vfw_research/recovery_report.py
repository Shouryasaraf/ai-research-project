"""Recompute recovery/capture evidence and retain complete attempt histories."""
import argparse
import hashlib
import json
from pathlib import Path
from .packet_observation import packets, compare_endpoints
from .recovery_metrics import summarize_recovery


def verify_capture(directory: Path, observation: dict) -> dict:
    for node in ("client", "server"):
        path = directory / f"{node}.pcap"
        if hashlib.sha256(path.read_bytes()).hexdigest() != observation["capture_sha256"][node]:
            raise ValueError("capture checksum mismatch")
    result = compare_endpoints(packets(directory / "client.pcap"), packets(directory / "server.pcap"),
                               capture_drops=observation["capture_kernel_drops"])
    for field in ("comparison_valid", "directions"):
        if result[field] != observation[field]:
            raise ValueError("capture result does not reproduce")
    return result


def build_report(batches: list[Path], output: Path) -> dict:
    if len({p.resolve() for p in batches}) != len(batches):
        raise ValueError("duplicate batch")
    attempts = []
    rows = []
    hashes = {}
    expected = {f"r{r}-{f}" for r in range(3) for f in ("controller_exit", "target_state_loss")}
    for batch in batches:
        paths = sorted(batch.glob("*/record.json"))
        if not paths:
            raise ValueError("no attempt records")
        names = {p.parent.name for p in paths}
        if not names <= expected:
            raise ValueError("unexpected trial identity")
        failed = 0
        code_hashes = set()
        for path in paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            code_hashes.add(record["code_sha256"])
            hashes[batch.name + "/" + path.parent.name] = hashlib.sha256(path.read_bytes()).hexdigest()
            completed = record["status"] == "completed" and not record.get("leftover_namespaces")
            failed += not completed
            row = {"batch": batch.name, "trial": path.parent.name, "status": record["status"],
                   "error": record.get("error") or record.get("packet_observation_error")}
            if completed and ("events" not in record or "blocked_monotonic" not in record):
                raise ValueError("completed recovery record lacks raw outcome evidence")
            if "events" in record and "blocked_monotonic" in record:
                row["metrics"] = summarize_recovery(record)
                if completed and not row["metrics"]["acceptance_passed"]:
                    raise ValueError("completed record fails recomputed acceptance")
            if "packet_observation" in record:
                row["packet_observation"] = verify_capture(path.parent, record["packet_observation"])
                if completed and not row["packet_observation"]["comparison_valid"]:
                    raise ValueError("completed record has invalid capture comparison")
            rows.append(row)
        attempts.append({"batch": batch.name, "planned": 6, "recorded": len(paths), "failed": failed,
                         "not_executed": len(expected - names), "source_fingerprints": sorted(code_hashes),
                         "all_six_completed": len(paths) == 6 and failed == 0})
    report = {"scope": "exploratory repeated supervised fault probes; not independent confirmatory evidence",
              "attempts": attempts, "trials": rows, "raw_record_sha256": hashes}
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Recovery and packet-observation evidence", "", report["scope"], "",
             "## All attempts", "", "| Batch | Recorded | Failed | Not executed | All six completed |",
             "|---|---:|---:|---:|---|"]
    for attempt in attempts:
        lines.append(f'| {attempt["batch"]} | {attempt["recorded"]} | {attempt["failed"]} | {attempt["not_executed"]} | {attempt["all_six_completed"]} |')
    lines.extend(["", "## Trial evidence", "",
                  "Routes-restored time includes supervisor operations, not exact downtime. Packet deficits count missing matched instances at the receiver.", "",
                  "| Batch / trial | Status | Resumed original flows | Disrupted flows | Fault to routes restored (s) | Forward missing/sent | Reverse missing/sent | Capture valid |",
                  "|---|---|---:|---:|---:|---|---|---|"])
    for row in rows:
        metrics = row.get("metrics", {})
        capture = row.get("packet_observation", {})
        deficits = [f'{d["missing_receiver_instances"]}/{d["sent_packet_instances"]}'
                    for d in capture.get("directions", [])] if capture.get("comparison_valid") else []
        deficits = deficits or ["unverified", "unverified"]
        seconds = metrics.get("fault_to_routes_restored_seconds")
        timing = f"{seconds:.6f}" if seconds is not None else "not restored"
        lines.append(f'| {row["batch"]} / {row["trial"]} | {row["status"]} | {metrics.get("resumed_original_flows", "n/a")} | '
                     f'{metrics.get("disrupted_flows", "n/a")} | {timing} | {deficits[0]} | {deficits[1]} | {capture.get("comparison_valid", False)} |')
    lines.extend(["", "Target-state-loss containment deliberately sacrifices availability. Surviving target state is required for the tested failback.",
                  "No reconnects are used. Capture verification checks raw PCAP hashes and recomputes packet matching.",
                  "These probes do not prove full TCP-state equivalence, general host-crash recovery, or exact service downtime.", ""])
    (output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batches", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build_report(args.batches, args.output)["attempts"], indent=2))
