"""Small line-oriented backend and flow-affine TCP proxy for integration tests."""

from __future__ import annotations

import argparse
import itertools
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vfw_research.load_balancing import FirewallInstance, FlowDirector

from guarded_selection import policy_is_approved


def replace_with_short_retry(source: Path, target: Path) -> None:
    """Tolerate brief Windows/OneDrive sharing locks without losing atomicity."""
    for attempt in range(3):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(0.02)


def relay(source: socket.socket, destination: socket.socket) -> None:
    try:
        while data := source.recv(65536):
            destination.sendall(data)
    except (ConnectionError, OSError):
        pass
    finally:
        try:
            destination.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def backend_connection(connection: socket.socket, backend_id: str) -> None:
    with connection:
        buffer = b""
        while chunk := connection.recv(4096):
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                connection.sendall(backend_id.encode() + b":" + line + b"\n")


def run_backend(listen_ip: str, port: int, backend_id: str) -> None:
    with socket.create_server((listen_ip, port), reuse_port=False) as server:
        while True:
            connection, _ = server.accept()
            threading.Thread(
                target=backend_connection, args=(connection, backend_id), daemon=True
            ).start()


class ProxyState:
    def __init__(self, metrics_file: Path) -> None:
        self.metrics_file = metrics_file
        self.lock = threading.Lock()
        self.director = FlowDirector()
        self.counts = {"source": 0, "target": 0}
        self.fallback_count = 0
        self._write_metrics()

    def _write_metrics(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=self.metrics_file.parent,
            prefix="vfwlab2-metrics-", delete=False,
        ) as handle:
            path = Path(handle.name)
            json.dump(
                {"active_flows": self.counts, "automatic_new_flow_fallbacks": self.fallback_count},
                handle, sort_keys=True,
            )
            handle.write("\n")
        replace_with_short_retry(path, self.metrics_file)

    def assign(self, flow_id: str, selection: str) -> str:
        with self.lock:
            if selection == "balanced":
                instances = [
                    FirewallInstance(name, self.counts[name], capacity_flows=100)
                    for name in ("source", "target")
                ]
                backend = self.director.assign(flow_id, instances).instance_id
            elif selection in {"source", "target"}:
                backend = selection
            else:
                raise ValueError("invalid backend selection")
            self.counts[backend] += 1
            self._write_metrics()
            return backend

    def release(self, flow_id: str, backend: str) -> None:
        with self.lock:
            self.counts[backend] -= 1
            self.director.release(flow_id)
            self._write_metrics()

    def record_fallback(self) -> None:
        with self.lock:
            self.fallback_count += 1
            self._write_metrics()


def restore_source_selection(control_file: Path) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=control_file.parent,
        prefix="vfwlab2-fallback-", delete=False,
    ) as handle:
        path = Path(handle.name)
        handle.write("source\n")
    replace_with_short_retry(path, control_file)


def source_policy_is_approved_now() -> bool:
    """Fail closed if the source path has drifted since its last validation."""
    try:
        output = subprocess.run(
            ["ip", "netns", "exec", "vfwlab2-fw-source", "nft", "-j", "list",
             "table", "inet", "vfw"],
            check=True, capture_output=True, text=True, timeout=2,
        ).stdout
        return policy_is_approved(json.loads(output))
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
        return False


def proxy_connection(
    client: socket.socket, control_file: Path, source_backend: str, target_backend: str,
    port: int, state: ProxyState, flow_id: str,
) -> None:
    with client:
        selection = control_file.read_text(encoding="utf-8").strip()
        if selection not in {"source", "target", "balanced"}:
            return
        backend_id = state.assign(flow_id, selection)
        try:
            backend_ip = source_backend if backend_id == "source" else target_backend
            try:
                backend = socket.create_connection((backend_ip, port), timeout=3)
            except OSError:
                if backend_id != "target":
                    raise
                if not source_policy_is_approved_now():
                    raise RuntimeError("validated source policy unavailable; fail closed")
                restore_source_selection(control_file)
                state.record_fallback()
                state.release(flow_id, "target")
                backend_id = state.assign(flow_id, "source")
                backend = socket.create_connection((source_backend, port), timeout=3)
            with backend:
                backend.settimeout(None)
                client.settimeout(None)
                upstream = threading.Thread(target=relay, args=(client, backend), daemon=True)
                upstream.start()
                relay(backend, client)
                upstream.join(timeout=1)
        finally:
            state.release(flow_id, backend_id)


def run_proxy(
    listen_ip: str, port: int, control_file: Path, source_backend: str, target_backend: str,
    metrics_file: Path,
) -> None:
    state = ProxyState(metrics_file)
    flow_ids = itertools.count()
    with socket.create_server((listen_ip, port), reuse_port=False) as server:
        while True:
            client, _ = server.accept()
            threading.Thread(
                target=proxy_connection,
                args=(client, control_file, source_backend, target_backend, port,
                      state, f"proxy-flow-{next(flow_ids)}"),
                daemon=True,
            ).start()


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    backend = subparsers.add_parser("backend")
    backend.add_argument("--listen", required=True)
    backend.add_argument("--port", type=int, default=9000)
    backend.add_argument("--id", required=True)
    proxy = subparsers.add_parser("proxy")
    proxy.add_argument("--listen", required=True)
    proxy.add_argument("--port", type=int, default=9000)
    proxy.add_argument("--control-file", type=Path, required=True)
    proxy.add_argument("--source-backend", required=True)
    proxy.add_argument("--target-backend", required=True)
    proxy.add_argument("--metrics-file", type=Path, required=True)
    args = parser.parse_args()
    if args.mode == "backend":
        run_backend(args.listen, args.port, args.id)
    else:
        run_proxy(
            args.listen,
            args.port,
            args.control_file,
            args.source_backend,
            args.target_backend,
            args.metrics_file,
        )


if __name__ == "__main__":
    main()
