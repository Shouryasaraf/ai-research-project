"""Small line-oriented backend and flow-affine TCP proxy for integration tests."""

from __future__ import annotations

import argparse
import socket
import threading
from pathlib import Path


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


def proxy_connection(
    client: socket.socket, control_file: Path, source_backend: str, target_backend: str, port: int
) -> None:
    with client:
        selection = control_file.read_text(encoding="utf-8").strip()
        if selection not in {"source", "target"}:
            return
        backend_ip = source_backend if selection == "source" else target_backend
        with socket.create_connection((backend_ip, port), timeout=3) as backend:
            backend.settimeout(None)
            client.settimeout(None)
            upstream = threading.Thread(target=relay, args=(client, backend), daemon=True)
            upstream.start()
            relay(backend, client)
            upstream.join(timeout=1)


def run_proxy(
    listen_ip: str, port: int, control_file: Path, source_backend: str, target_backend: str
) -> None:
    with socket.create_server((listen_ip, port), reuse_port=False) as server:
        while True:
            client, _ = server.accept()
            threading.Thread(
                target=proxy_connection,
                args=(client, control_file, source_backend, target_backend, port),
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
        )


if __name__ == "__main__":
    main()

