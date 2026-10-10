"""Wire-visible TCP reset/repeated-payload audit of validated lab captures.

No inference about complete kernel TCP/conntrack window or sequence state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from collections import Counter
from pathlib import Path

from .packet_observation import packets
from .recovery_report import verify_capture


def sender_stats(frames: list[dict], source: str) -> dict:
    sent = [row for row in frames if row["source"] == source]
    payloads = Counter(row["payload_key"] for row in sent if row["payload_bytes"])
    return {"sent_packet_instances": len(sent),
            "sender_rst_instances": sum(bool(row["flags"] & 0x04) for row in sent),
            "sender_syn_instances": sum(bool(row["flags"] & 0x02) for row in sent),
            "sender_fin_instances": sum(bool(row["flags"] & 0x01) for row in sent),
            "repeated_payload_sequence_instances": sum(count - 1 for count in payloads.values()),
            "zero_window_advertisements": sum(row["window"] == 0 for row in sent)}


def _source_archive_matches(batch: Path, digest: str) -> None:
    with zipfile.ZipFile(batch / "executed-source.zip") as archive:
        if archive.testzip() is not None:
            raise ValueError("executed source archive damaged")
        calculated = hashlib.sha256()
        for name in archive.namelist():
            calculated.update(name.encode())
            calculated.update(archive.read(name))
    if calculated.hexdigest() != digest:
        raise ValueError("executed source archive fingerprint mismatch")


def analyze_batch(batch: Path) -> dict:
    manifest = json.loads((batch / "manifest.json").read_text(encoding="utf-8"))
    if not manifest.get("capture"):
        raise ValueError("batch was not captured")
    _source_archive_matches(batch, manifest["code_sha256"])
    expected = {f's{seed}-{policy}' for seed in manifest["seeds"] for policy in manifest["policies"]}
    paths = sorted(batch.glob("*/record.json"))
    if {path.parent.name for path in paths} != expected or len(paths) != len(expected):
        raise ValueError("incomplete captured batch")
    rows = []
    for path in paths:
        record = json.loads(path.read_text(encoding="utf-8"))
        if (record.get("status") != "completed" or record.get("leftover_namespaces")
                or record.get("code_sha256") != manifest["code_sha256"]
                or path.parent.name != f's{record["seed"]}-{record["policy"]}'):
            raise ValueError("captured trial identity/status/fingerprint invalid")
        if not verify_capture(path.parent, record["packet_observation"])["comparison_valid"]:
            raise ValueError("captured trial comparison invalid")
        client, server = packets(path.parent / "client.pcap"), packets(path.parent / "server.pcap")
        rows.append({"policy": record["policy"], "seed": record["seed"],
                     "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "forward": sender_stats(client, "10.50.0.2"),
                     "reverse": sender_stats(server, "10.50.5.2")})
    return {"evidence_class": "wire-visible TCP flags and payload repetition in validated isolated lab captures",
            "batch": batch.name, "manifest_sha256": hashlib.sha256((batch / "manifest.json").read_bytes()).hexdigest(),
            "boundary": "RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss",
            "trials": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = analyze_batch(args.batch)
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = ["# Validated TCP wire-visible diagnostic", "", report["boundary"], "",
             "| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |",
             "|---|---:|---:|---:|"]
    for row in report["trials"]:
        a, b = row["forward"], row["reverse"]
        lines.append(f'| {row["policy"]} / {row["seed"]} | '
                     f'{a["sender_rst_instances"]}/{b["sender_rst_instances"]} | '
                     f'{a["repeated_payload_sequence_instances"]}/{b["repeated_payload_sequence_instances"]} | '
                     f'{a["zero_window_advertisements"]}/{b["zero_window_advertisements"]} |')
    lines.extend(["", "Only packets generated in the isolated lab are examined. Source archives, record hashes, "
                  "endpoint PCAP hashes and packet-instance matching are checked before this summary. "
                  "A repeated payload sequence is an indicator, not a transport diagnosis. "
                  "No kernel TCP sequence/window equivalence is claimed.", ""])
    (args.output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"trials": len(report["trials"]), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
