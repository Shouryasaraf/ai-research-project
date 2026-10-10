"""Stream PCAPNG packet metadata into one-second traffic rates; never export payloads.

The intended input is a selected member of the versioned Cyber4OT ZIP archive.
This parser accepts timestamped Enhanced Packet Blocks only; a timestampless
Simple Packet Block fails closed instead of silently corrupting a rate series.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import zipfile
from datetime import datetime, timezone
from pathlib import Path


SOURCE = "https://doi.org/10.5281/zenodo.13935639"
LICENSE = "CC BY-NC 4.0; cite Cyber4OT authors; raw PCAPNG not committed"
MEMBER = re.compile(r"traces/Cyber4OT_[0-9]{3}\.pcapng\Z")
SHB = b"\x0a\x0d\x0d\x0a"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _exact(stream, size: int) -> bytes:
    result = stream.read(size)
    if len(result) != size:
        raise ValueError("truncated PCAPNG block")
    return result


def _options(raw: bytes, endian: str) -> dict[int, bytes]:
    result = {}
    offset = 0
    while offset < len(raw):
        if len(raw) - offset < 4:
            raise ValueError("truncated PCAPNG option")
        code, length = struct.unpack_from(endian + "HH", raw, offset)
        offset += 4
        padded = (length + 3) & ~3
        if offset + padded > len(raw):
            raise ValueError("invalid PCAPNG option length")
        value = raw[offset:offset + length]
        offset += padded
        if code == 0:
            if length or any(raw[offset:]):
                raise ValueError("invalid PCAPNG option end")
            break
        if code in result and code in (9, 14):
            raise ValueError("duplicate timestamp option")
        result[code] = value
    return result


def aggregate(stream, *, interval_seconds: int = 1) -> tuple[list[tuple[int, float]], dict]:
    if interval_seconds < 1:
        raise ValueError("interval_seconds must be positive")
    endian = None
    interfaces: list[tuple[int, int]] = []  # timestamp ticks/second, UTC offset seconds
    bins: dict[int, int] = {}
    count = 0
    first_time: float | None = None
    last_time: float | None = None
    while header := stream.read(8):
        if len(header) != 8:
            raise ValueError("truncated PCAPNG block header")
        if header[:4] == SHB:
            bom = _exact(stream, 4)
            if bom == b"\x4d\x3c\x2b\x1a":
                endian = "<"
            elif bom == b"\x1a\x2b\x3c\x4d":
                endian = ">"
            else:
                raise ValueError("invalid PCAPNG byte-order magic")
            length = struct.unpack(endian + "I", header[4:])[0]
            if length < 28 or length % 4 or length > 1024 * 1024:
                raise ValueError("invalid PCAPNG section length")
            remainder = _exact(stream, length - 12)
            if struct.unpack(endian + "I", remainder[-4:])[0] != length:
                raise ValueError("PCAPNG section length trailer mismatch")
            major, minor = struct.unpack(endian + "HH", remainder[:4])
            if (major, minor) != (1, 0):
                raise ValueError("unsupported PCAPNG version")
            interfaces = []
            continue
        if endian is None:
            raise ValueError("PCAPNG section header required first")
        block_type, length = struct.unpack(endian + "II", header)
        if length < 12 or length % 4 or length > 1024 * 1024:
            raise ValueError("invalid PCAPNG block length")
        remainder = _exact(stream, length - 8)
        if struct.unpack(endian + "I", remainder[-4:])[0] != length:
            raise ValueError("PCAPNG block length trailer mismatch")
        body = remainder[:-4]
        if block_type == 1:  # Interface Description Block
            if len(body) < 8:
                raise ValueError("truncated interface block")
            options = _options(body[8:], endian)
            resolution = options.get(9, b"\x06")
            if len(resolution) != 1:
                raise ValueError("invalid interface timestamp resolution")
            exponent = resolution[0] & 0x7f
            if exponent > 18:
                raise ValueError("unsupported timestamp resolution")
            ticks_per_second = ((2 if resolution[0] & 0x80 else 10) ** exponent)
            offset = options.get(14, b"\x00" * 8)
            if len(offset) != 8:
                raise ValueError("invalid interface timestamp offset")
            interfaces.append((ticks_per_second, struct.unpack(endian + "q", offset)[0]))
        elif block_type == 6:  # Enhanced Packet Block
            if len(body) < 20:
                raise ValueError("truncated enhanced packet block")
            interface_id, high, low, captured, original = struct.unpack_from(endian + "IIIII", body)
            if interface_id >= len(interfaces) or original < captured:
                raise ValueError("invalid enhanced packet interface or lengths")
            if 20 + ((captured + 3) & ~3) > len(body):
                raise ValueError("truncated enhanced packet contents")
            ticks_per_second, offset = interfaces[interface_id]
            ticks = (high << 32) | low
            second = ticks // ticks_per_second + offset
            timestamp = ticks / ticks_per_second + offset
            if last_time is not None and timestamp < last_time:
                raise ValueError("out-of-order PCAPNG timestamps")
            bin_start = second // interval_seconds * interval_seconds
            bins[bin_start] = bins.get(bin_start, 0) + original
            first_time = timestamp if first_time is None else first_time
            last_time = timestamp
            count += 1
        elif block_type == 3:
            raise ValueError("timestampless simple packet block unsupported")
    if not count:
        raise ValueError("PCAPNG contains no timestamped packets")
    first_bin, last_bin = min(bins), max(bins)
    if last_bin - first_bin > 24 * 3600:
        raise ValueError("capture span exceeds one-day safety bound")
    series = [(second, bins.get(second, 0) * 8 / (interval_seconds * 1_000_000))
              for second in range(first_bin, last_bin + interval_seconds, interval_seconds)]
    return series, {
        "packet_count": count,
        "first_packet_utc": datetime.fromtimestamp(first_time, timezone.utc).isoformat(),
        "last_packet_utc": datetime.fromtimestamp(last_time, timezone.utc).isoformat(),
        "zero_packet_bins": sum(value == 0 for _, value in series),
        "total_original_length_bytes": sum(bins.values()),
    }


def convert(archive: Path, member: str, csv_path: Path, sidecar_path: Path,
            *, interval_seconds: int = 1) -> dict:
    if not MEMBER.fullmatch(member):
        raise ValueError("expected a named Cyber4OT PCAPNG member")
    if csv_path.exists() or sidecar_path.exists():
        raise FileExistsError("output exists; preserve immutable provenance")
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError("damaged dataset ZIP")
        if member not in zipped.namelist():
            raise ValueError("selected member absent from dataset ZIP")
        with zipped.open(member) as stream:
            series, capture = aggregate(stream, interval_seconds=interval_seconds)
        member_sha256 = hashlib.sha256(zipped.read(member)).hexdigest()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("timestamp_utc", "value"))
        for second, mbps in series:
            writer.writerow((datetime.fromtimestamp(second, timezone.utc).isoformat(), f"{mbps:.9f}"))
    metadata = {
        "kind": "traffic", "unit": "Mbps", "source": SOURCE,
        "license": LICENSE, "version": "Cyber4OT 1.0.0 / " + member,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "preprocessing": "PCAPNG enhanced-packet original lengths summed per UTC interval; packet contents ignored; internal empty bins zero-filled",
        "missing_data_policy": "Explicit zero within first/last observed packet; no extrapolation beyond capture",
        "sha256": _sha256(csv_path), "sampling_interval_seconds": interval_seconds,
        "archive_sha256": _sha256(archive), "member_sha256": member_sha256,
        "capture": capture,
    }
    with sidecar_path.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--member", required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    args = parser.parse_args()
    result = convert(args.archive, args.member, args.csv, args.provenance)
    print(json.dumps({"csv": str(args.csv), "provenance": str(args.provenance),
                      "capture": result["capture"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
