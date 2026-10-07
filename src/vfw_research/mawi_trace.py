"""Stream a MAWI classic-pcap capture into an explicitly derived Mbps series.

Only pcap record headers are interpreted. Packet contents are skipped, never
decoded or written to the output. This is a workload input, not vFW telemetry.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path


MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("<", 1_000_000),
    b"\xa1\xb2\xc3\xd4": (">", 1_000_000),
    b"\x4d\x3c\xb2\xa1": ("<", 1_000_000_000),
    b"\xa1\xb2\x3c\x4d": (">", 1_000_000_000),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def aggregate_pcap(path: Path, *, interval_seconds: int = 1) -> tuple[list[tuple[int, float]], dict]:
    """Return UTC bin starts and Mbps from pcap original-length fields."""
    if interval_seconds < 1:
        raise ValueError("interval_seconds must be positive")
    opener = gzip.open if path.name.endswith(".gz") else open
    bins: dict[int, int] = {}
    count = 0
    last_ns: int | None = None
    with opener(path, "rb") as handle:
        global_header = handle.read(24)
        if len(global_header) != 24 or global_header[:4] not in MAGIC:
            raise ValueError("input must be a complete classic pcap (optionally gzip)")
        endian, precision = MAGIC[global_header[:4]]
        major, minor, _, _, snaplen, _ = struct.unpack(endian + "HHiiii", global_header[4:])
        if (major, minor) != (2, 4) or snaplen < 1:
            raise ValueError("unsupported pcap version or snaplen")
        first_ns: int | None = None
        while True:
            header = handle.read(16)
            if not header:
                break
            if len(header) != 16:
                raise ValueError("truncated pcap record header")
            seconds, fraction, captured, original = struct.unpack(endian + "IIII", header)
            if fraction >= precision or captured > snaplen or original < captured:
                raise ValueError("invalid pcap record timestamp or lengths")
            timestamp_ns = seconds * 1_000_000_000 + fraction * (1_000_000_000 // precision)
            if last_ns is not None and timestamp_ns < last_ns:
                raise ValueError("out-of-order pcap timestamps")
            remaining = captured
            while remaining:
                chunk = handle.read(min(remaining, 1024 * 1024))
                if not chunk:
                    raise ValueError("truncated pcap packet data")
                remaining -= len(chunk)
            bin_start = seconds // interval_seconds * interval_seconds
            bins[bin_start] = bins.get(bin_start, 0) + original
            first_ns = timestamp_ns if first_ns is None else first_ns
            last_ns = timestamp_ns
            count += 1
    if not count:
        raise ValueError("pcap contains no packets")
    first_bin, last_bin = min(bins), max(bins)
    series = [(second, bins.get(second, 0) * 8 / (interval_seconds * 1_000_000))
              for second in range(first_bin, last_bin + interval_seconds, interval_seconds)]
    return series, {
        "packet_count": count,
        "first_packet_utc": datetime.fromtimestamp(first_ns / 1e9, timezone.utc).isoformat(),
        "last_packet_utc": datetime.fromtimestamp(last_ns / 1e9, timezone.utc).isoformat(),
        "zero_packet_bins": sum(value == 0 for _, value in series),
        "total_original_length_bytes": sum(bins.values()),
        "capture_sha256": _sha256(path),
    }


def convert(path: Path, csv_path: Path, sidecar_path: Path, *, source: str,
            interval_seconds: int = 1) -> dict:
    if not source.startswith("https://mawi.nezu.wide.ad.jp/mawi/"):
        raise ValueError("source must be the official HTTPS MAWI capture URL")
    if csv_path.exists() or sidecar_path.exists():
        raise FileExistsError("output exists; preserve immutable provenance")
    series, capture = aggregate_pcap(path, interval_seconds=interval_seconds)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("timestamp_utc", "value"))
        for second, mbps in series:
            writer.writerow((datetime.fromtimestamp(second, timezone.utc).isoformat(), f"{mbps:.9f}"))
    metadata = {
        "kind": "traffic", "unit": "Mbps", "source": source,
        "license": "MAWI/WIDE research-only privacy guidelines; raw capture not redistributed",
        "version": path.name,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "preprocessing": "Classic pcap original-length bytes summed per UTC interval; packet content ignored; zero-packet bins filled with zero; no extrapolation for capture loss",
        "missing_data_policy": "Explicit zero for bins within first/last observed packet; no bins outside observed capture",
        "sha256": _sha256(csv_path), "sampling_interval_seconds": interval_seconds,
        "capture": capture,
    }
    with sidecar_path.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcap", type=Path, required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--interval-seconds", type=int, default=1)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    args = parser.parse_args()
    metadata = convert(args.pcap, args.csv, args.provenance, source=args.source,
                       interval_seconds=args.interval_seconds)
    print(json.dumps({"csv": str(args.csv), "provenance": str(args.provenance),
                      "capture": metadata["capture"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
