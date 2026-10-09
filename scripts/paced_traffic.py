"""Bounded request/echo traffic for the isolated vfwlab3 topology."""
from __future__ import annotations

import argparse
import json
import socket
import threading
import time
from pathlib import Path


def receive(connection: socket.socket, expected: bytes) -> None:
    data = bytearray()
    while len(data) < len(expected):
        chunk = connection.recv(min(65536, len(expected) - len(data)))
        if not chunk:
            raise ConnectionError("connection closed during response")
        data.extend(chunk)
    if data != expected:
        raise ValueError("echo content mismatch")


def run(plan: dict) -> None:
    rates = plan["rates_mbps"]
    interval = float(plan["interval_seconds"])
    flows = int(plan["flows"])
    if not rates or any(not 0 < rate <= 10 for rate in rates) or not 0.25 <= interval <= 5:
        raise ValueError("rate/interval outside isolated experiment bounds")
    if not 1 <= flows <= 16:
        raise ValueError("flows must be in [1, 16]")
    connections = []
    for _ in range(flows):
        conn = socket.create_connection(("10.50.5.2", 9000), timeout=2)
        conn.sendall(b"ready\n")
        receive(conn, b"server:ready\n")
        connections.append(conn)
    events: list[dict] = []
    lock = threading.Lock()
    started = time.monotonic()
    stop = started + len(rates) * interval

    def worker(flow_id: int, connection: socket.socket) -> None:
        with connection:
            while time.monotonic() < stop:
                sent = time.monotonic()
                step = min(len(rates) - 1, int((sent - started) / interval))
                size = max(1, min(32768, round(rates[step] * 1e6 / 8 / 20 / flows)))
                payload = b"x" * size
                error = None
                try:
                    connection.sendall(payload + b"\n")
                    receive(connection, b"server:" + payload + b"\n")
                except (OSError, ValueError) as exc:
                    error = type(exc).__name__ + ": " + str(exc)
                finished = time.monotonic()
                event = {"flow_id": flow_id, "offered_step": step, "sent_monotonic": sent,
                         "finished_monotonic": finished, "payload_bytes": size,
                         "success": error is None, "error": error,
                         "rtt_ms": (finished - sent) * 1000}
                with lock:
                    events.append(event)
                if error is not None:
                    break
                time.sleep(max(0.0, 0.05 - (time.monotonic() - sent)))

    print(json.dumps({"type": "ready", "started_monotonic": started, "flows": flows}), flush=True)
    threads = [threading.Thread(target=worker, args=(i, conn))
               for i, conn in enumerate(connections)]
    for thread in threads:
        thread.start()
    previous = started
    for step in range(len(rates)):
        time.sleep(max(0.0, started + (step + 1) * interval - time.monotonic()))
        now = time.monotonic()
        with lock:
            sample = [event for event in events if previous <= event["finished_monotonic"] < now]
        print(json.dumps({"type": "sample", "step": step, "observed_monotonic": now,
                          "duration_seconds": now - previous,
                          "scheduled_mbps": rates[step],
                          "goodput_mbps": sum(e["payload_bytes"] for e in sample if e["success"]) * 8 / 1e6 / (now - previous),
                          "completed_requests": len(sample),
                          "errors": sum(not e["success"] for e in sample)}), flush=True)
        previous = now
    for thread in threads:
        thread.join(timeout=3)
    if any(thread.is_alive() for thread in threads):
        raise TimeoutError("traffic thread did not stop")
    print(json.dumps({"type": "complete", "events": events,
                      "finished_monotonic": time.monotonic()}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    run(json.loads(args.plan.read_text(encoding="utf-8")))
