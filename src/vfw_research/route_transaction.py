"""Durable route intent and conservative restart containment.

This is not an atomic two-router commit. An uncertain transaction is blocked,
not silently restored using potentially stale connection state. Callers serialize
access and supply fresh, externally verified state/policy evidence for recovery.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable


class RouteTransaction:
    def __init__(self, directory: Path, apply_route: Callable[[str, str], None],
                 verify_route: Callable[[str, str], bool]):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.apply_route = apply_route
        self.verify_route = verify_route

    def events(self) -> list[dict]:
        paths = sorted(self.directory.glob("*.json"))
        events = []
        for index, path in enumerate(paths):
            if path.name != f"{index:06d}.json":
                raise ValueError("non-contiguous route journal")
            event = json.loads(path.read_text(encoding="utf-8"))
            if event.get("sequence") != index:
                raise ValueError("invalid route journal sequence")
            events.append(event)
        return events

    def record(self, state: str, **details: object) -> None:
        index = len(self.events())
        # Exclusive files preserve previous intent. A torn final record triggers
        # fail-closed recovery, never a guessed successful transaction.
        path = self.directory / f"{index:06d}.json"
        with path.open("x", encoding="utf-8") as handle:
            json.dump({"sequence": index, "state": state, **details}, handle)
            handle.flush()
            os.fsync(handle.fileno())
        if os.name == "posix":
            descriptor = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)

    def block(self) -> None:
        errors = []
        # Attempt both directions even if the first operation fails.
        for side in ("ingress", "egress"):
            try:
                self.apply_route(side, "blocked")
                if not self.verify_route(side, "blocked"):
                    raise RuntimeError("route readback mismatch")
            except Exception as error:
                errors.append(f"{side}: {error}")
        if errors:
            raise RuntimeError("containment incomplete: " + "; ".join(errors))

    def commit(self, validate: Callable[[], bool]) -> None:
        if self.events():
            raise ValueError("transaction journal already used")
        if not validate():
            self.record("REFUSED", reason="precommit validation failed")
            return
        self.record("PREPARED", destination="target")
        try:
            for side in ("ingress", "egress"):
                if not validate():
                    raise RuntimeError("commit-time validation failed")
                self.record("APPLYING", side=side, destination="target")
                self.apply_route(side, "target")
                if not self.verify_route(side, "target"):
                    raise RuntimeError("route readback mismatch")
            if not validate():
                raise RuntimeError("postcommit validation failed")
            self.record("COMMITTED", destination="target")
        except Exception:
            self.block()
            self.record("BLOCKED", reason="commit failure")
            raise

    def recover(self, source_ready: Callable[[], bool]) -> str:
        # Block BEFORE reading a possibly torn journal or trusting a checkpoint.
        self.block()
        try:
            events = self.events()
        except (ValueError, OSError):
            return "BLOCKED_CORRUPT_JOURNAL"
        if not events or not source_ready():
            self.record("BLOCKED", reason="fresh source state/policy not verified")
            return "BLOCKED"
        self.record("RECOVERING", destination="source")
        try:
            for side in ("ingress", "egress"):
                if not source_ready():
                    raise RuntimeError("recovery validation failed")
                self.apply_route(side, "source")
                if not self.verify_route(side, "source"):
                    raise RuntimeError("recovery route readback mismatch")
            if not source_ready():
                raise RuntimeError("post-recovery validation failed")
            self.record("RECOVERED", destination="source")
            return "RECOVERED"
        except Exception:
            self.block()
            self.record("BLOCKED", reason="recovery failure")
            raise
