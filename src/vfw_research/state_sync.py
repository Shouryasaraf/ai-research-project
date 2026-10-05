"""Reference flow-state adapter; not evidence of kernel conntrack transfer."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True, order=True)
class FlowKey:
    protocol: str
    source_ip: str
    source_port: int
    destination_ip: str
    destination_port: int


@dataclass(frozen=True)
class FlowRecord:
    key: FlowKey
    lifecycle: str
    policy_hash: str
    packets_forward: int
    packets_reverse: int
    expires_at_monotonic: float


@dataclass(frozen=True)
class SyncReport:
    source_count: int
    target_count: int
    transferred_count: int
    approximate_bytes: int
    source_digest: str
    target_digest: str
    missing_keys: tuple[FlowKey, ...]
    mismatched_keys: tuple[FlowKey, ...]

    @property
    def mismatch_fraction(self) -> float:
        if self.source_count == 0:
            return 0.0 if not self.missing_keys and not self.mismatched_keys else 1.0
        return (len(self.missing_keys) + len(self.mismatched_keys)) / self.source_count

    @property
    def consistent(self) -> bool:
        return self.source_digest == self.target_digest and self.mismatch_fraction == 0


def _serialized(records: dict[FlowKey, FlowRecord]) -> bytes:
    rows = [asdict(records[key]) for key in sorted(records)]
    return json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _eligible(
    records: dict[FlowKey, FlowRecord], expected_policy_hash: str
) -> dict[FlowKey, FlowRecord]:
    return {
        key: record
        for key, record in records.items()
        if record.lifecycle == "ESTABLISHED" and record.policy_hash == expected_policy_hash
    }


def _report(
    source: dict[FlowKey, FlowRecord], target: dict[FlowKey, FlowRecord], transferred: int
) -> SyncReport:
    target_view = {key: target[key] for key in source if key in target}
    missing = tuple(sorted(key for key in source if key not in target))
    mismatched = tuple(
        sorted(key for key, record in source.items() if key in target and target[key] != record)
    )
    source_bytes = _serialized(source)
    target_bytes = _serialized(target_view)
    return SyncReport(
        len(source),
        len(target_view),
        transferred,
        len(source_bytes),
        hashlib.sha256(source_bytes).hexdigest(),
        hashlib.sha256(target_bytes).hexdigest(),
        missing,
        mismatched,
    )


def synchronize_state(
    source: dict[FlowKey, FlowRecord],
    target: dict[FlowKey, FlowRecord],
    *,
    expected_policy_hash: str,
) -> SyncReport:
    eligible = _eligible(source, expected_policy_hash)
    transferred = 0
    for key, record in eligible.items():
        if target.get(key) != record:
            target[key] = record
            transferred += 1
    return _report(eligible, target, transferred)


def validate_state(
    source: dict[FlowKey, FlowRecord],
    target: dict[FlowKey, FlowRecord],
    *,
    expected_policy_hash: str,
) -> SyncReport:
    return _report(_eligible(source, expected_policy_hash), target, 0)

