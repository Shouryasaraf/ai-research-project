"""Convert the preselected Zero-SWARM normal classic-PCAP to rate-only CSV.

Packet bytes are skipped by the shared strict PCAP parser. The publisher's MD5
is checked for download integrity; a local SHA-256 is retained for provenance.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .mawi_trace import aggregate_pcap

SOURCE = "https://doi.org/10.5281/zenodo.15082260"
FILENAME = "ZeroSWARM Normal data_v2b.pcap"
PUBLISHER_MD5 = "9f8235fcdbfcacb32e7a70db14fc6c74"


def _digest(path: Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def convert(path: Path, csv_path: Path, sidecar_path: Path,
            *, expected_md5: str = PUBLISHER_MD5) -> dict:
    if path.name != FILENAME:
        raise ValueError("input must be the preselected Zero-SWARM normal PCAP")
    if csv_path.exists() or sidecar_path.exists():
        raise FileExistsError("output exists; preserve immutable provenance")
    if _digest(path, "md5") != expected_md5:
        raise ValueError("PCAP checksum differs from publisher metadata")
    series, capture = aggregate_pcap(path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("x", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("timestamp_utc", "value"))
        for second, mbps in series:
            writer.writerow((datetime.fromtimestamp(second, timezone.utc).isoformat(), f"{mbps:.9f}"))
    metadata = {
        "kind": "traffic", "unit": "Mbps", "source": SOURCE,
        "license": "CC BY 4.0; cite Zero-SWARM dataset creators; raw PCAP not committed",
        "version": "Zenodo record 15082260 / " + FILENAME,
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "preprocessing": "Classic PCAP original lengths summed into one-second UTC bins; packet contents skipped; internal empty bins zero-filled",
        "missing_data_policy": "Explicit zero within first/last observed packet; no extrapolation beyond capture",
        "sha256": _digest(csv_path, "sha256"), "sampling_interval_seconds": 1,
        "pcap_md5": expected_md5, "capture": capture,
    }
    with sidecar_path.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return metadata


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcap", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    args = parser.parse_args(argv)
    metadata = convert(args.pcap, args.csv, args.provenance)
    print(json.dumps({"csv": str(args.csv), "provenance": str(args.provenance),
                      "capture": metadata["capture"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
