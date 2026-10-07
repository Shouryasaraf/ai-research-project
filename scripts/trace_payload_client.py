"""Send two bounded, trace-sized messages on one TCP socket in an isolated lab."""

from __future__ import annotations

import argparse
import json
import math
import socket
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vfw_research.forecasting import time_ordered_split
from vfw_research.trace_adapter import TraceKind, load_trace


def payload_bytes(mbps: float, interval_seconds: int, *, scale: float = 0.01,
                  maximum: int = 65_536) -> int:
    if not math.isfinite(mbps) or mbps < 0 or interval_seconds < 1:
        raise ValueError("invalid traffic rate or interval")
    if not 0 < scale <= 1 or maximum < 1:
        raise ValueError("invalid scale or maximum")
    return min(maximum, max(1, round(mbps * 1_000_000 / 8 * interval_seconds * scale)))


def first_two_test_rates(csv_path: Path, sidecar_path: Path) -> tuple[str, tuple[float, float], int]:
    trace = load_trace(csv_path, sidecar_path)
    if trace.kind is not TraceKind.TRAFFIC:
        raise ValueError("traffic trace required")
    split = time_ordered_split([point.value for point in trace.points])
    if len(split.test) < 2:
        raise ValueError("at least two held-out samples required")
    return trace.csv_sha256, (split.test[0], split.test[1]), trace.sampling_interval_seconds


def receive_line(connection: socket.socket) -> bytes:
    chunks = []
    while True:
        chunk = connection.recv(65_536)
        if not chunk:
            raise ConnectionError("server closed before full response")
        chunks.append(chunk)
        if b"\n" in chunk:
            data = b"".join(chunks)
            if data.count(b"\n") != 1 or not data.endswith(b"\n"):
                raise ValueError("unexpected server response framing")
            return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--trace-csv", type=Path, required=True)
    parser.add_argument("--provenance", type=Path, required=True)
    parser.add_argument("--delay", type=float, default=3.0)
    args = parser.parse_args()
    if args.delay < 0:
        parser.error("delay must be non-negative")
    digest, rates, interval = first_two_test_rates(args.trace_csv, args.provenance)
    with socket.create_connection((args.host, args.port), timeout=5) as connection:
        connection.settimeout(5)
        for index, rate in enumerate(rates):
            size = payload_bytes(rate, interval)
            payload = f"sample-{index}:".encode() + b"x" * size
            start = time.monotonic_ns()
            connection.sendall(payload + b"\n")
            received = receive_line(connection)
            elapsed_ms = (time.monotonic_ns() - start) / 1_000_000
            if received != b"server:" + payload + b"\n":
                raise ValueError(f"response mismatch at sample {index}")
            print(json.dumps({
                "sample_index": index,
                "traffic_rate_mbps": rate,
                "scaled_payload_bytes": size,
                "response_verified": True,
                "round_trip_ms": elapsed_ms,
                "trace_csv_sha256": digest,
            }, sort_keys=True), flush=True)
            if index == 0:
                time.sleep(args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
