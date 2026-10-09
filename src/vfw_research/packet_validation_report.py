"""Recompute and report isolated packet-capture method controls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from .recovery_report import verify_capture


def verify_source(batch: Path, first: dict) -> None:
    path = batch / "executed-source.zip"
    if hashlib.sha256(path.read_bytes()).hexdigest() != first["executed_source_sha256"]:
        raise ValueError("executed source archive hash mismatch")
    digest = hashlib.sha256()
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("executed source archive damaged")
        for name in archive.namelist():
            digest.update(name.encode())
            digest.update(archive.read(name))
    if digest.hexdigest() != first["code_sha256"]:
        raise ValueError("executed source fingerprint mismatch")


def build_report(batch: Path, output: Path) -> dict:
    records = sorted(batch.glob("r*-*/record.json"))
    if not records:
        raise ValueError("no capture control records")
    names = {path.parent.name for path in records}
    if len(names) != len(records):
        raise ValueError("duplicate control identity")
    repetitions = sorted({int(name.split("-")[0][1:]) for name in names})
    if repetitions != list(range(len(repetitions))) or names != {
        f"r{number}-{mode}" for number in repetitions for mode in ("ordinary", "forced_drop")
    }:
        raise ValueError("paired controls are incomplete")
    rows = []
    source_record = json.loads(records[0].read_text(encoding="utf-8"))
    verify_source(batch, source_record)
    for path in records:
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") != "completed" or record.get("leftover_namespaces"):
            raise ValueError("incomplete or contaminated control")
        if record.get("mode") != path.parent.name.split("-", 1)[1]:
            raise ValueError("control mode mismatch")
        if any(record.get(key) != source_record[key] for key in ("code_sha256", "executed_source_sha256")):
            raise ValueError("source changed between paired controls")
        if record.get("scope") != "three persistent TCP echo flows; isolated paired endpoint capture control":
            raise ValueError("capture scope not attested")
        observation = verify_capture(path.parent, record["packet_observation"])
        if not observation["comparison_valid"] or observation["capture_kernel_drops"]:
            raise ValueError("invalid paired capture")
        if record["traffic"]["failures"] or record["traffic"]["requests"] < 1:
            raise ValueError("application traffic control failed")
        missing = observation["directions"][0]["missing_receiver_instances"]
        if record["mode"] == "ordinary" and (missing or observation["directions"][1]["missing_receiver_instances"]):
            raise ValueError("ordinary control has endpoint deficits")
        if record["mode"] == "forced_drop":
            if missing <= 0 or not record.get("drop_injection") or record["drop_injection"]["duration_seconds"] <= 0:
                raise ValueError("forced-drop control lacks observed effect")
        rows.append({"trial": path.parent.name, "mode": record["mode"],
                     "requests": record["traffic"]["requests"],
                     "forward_missing": missing,
                     "forward_sent": observation["directions"][0]["sent_packet_instances"],
                     "reverse_missing": observation["directions"][1]["missing_receiver_instances"],
                     "reverse_sent": observation["directions"][1]["sent_packet_instances"],
                     "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    report = {"scope": "isolated capture-method controls; not a migration or production-loss benchmark",
              "source_snapshot_verified": True, "repetitions": len(repetitions), "trials": rows,
              "interpretation": "ordinary observations had no matched endpoint deficits; deliberate forwarding drops were detected; TCP application requests may recover through retransmission"}
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Paired endpoint capture controls", "", report["scope"], "",
             "| Trial | Mode | Forward missing/sent | Reverse missing/sent | Completed requests |",
             "|---|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f'| {row["trial"]} | {row["mode"]} | {row["forward_missing"]}/{row["forward_sent"]} | '
                     f'{row["reverse_missing"]}/{row["reverse_sent"]} | {row["requests"]} |')
    lines.extend(["", "All captures had zero capture-kernel drops and no unmatched receiver-only packet instances.",
                  "All application requests completed; TCP retransmission can mask packet drops at the request level.",
                  "The counters are matched packet-instance deficits between two isolated capture points. They do not establish exact migration loss or service downtime.",
                  "Raw record, capture and executed-source SHA-256 values are verified; raw record hashes appear in summary.json.", ""])
    (output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps({"repetitions": build_report(args.batch, args.output)["repetitions"]}))
