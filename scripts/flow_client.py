"""Client that keeps one TCP connection open across a target switch."""

from __future__ import annotations

import argparse
import socket
import time


def receive_line(connection: socket.socket) -> str:
    data = b""
    while not data.endswith(b"\n"):
        chunk = connection.recv(4096)
        if not chunk:
            raise ConnectionError("connection closed before newline")
        data += chunk
    return data.decode().strip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("host")
    parser.add_argument("--port", type=int, default=9000)
    parser.add_argument("--delay", type=float, default=0)
    parser.add_argument("messages", nargs="+")
    args = parser.parse_args()
    with socket.create_connection((args.host, args.port), timeout=3) as connection:
        for index, message in enumerate(args.messages):
            connection.sendall(message.encode() + b"\n")
            print(receive_line(connection), flush=True)
            if index + 1 < len(args.messages):
                time.sleep(args.delay)


if __name__ == "__main__":
    main()

