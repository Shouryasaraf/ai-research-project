"""Typed telemetry snapshots with explicit freshness and unit validation."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TelemetrySnapshot:
    node_id: str
    observed_monotonic_seconds: float
    cpu_utilization_fraction: float
    memory_utilization_fraction: float
    throughput_mbps: float
    latency_ms: float
    dropped_packets: int
    active_flows: int
    state_size_bytes: int
    healthy: bool
    source: str

    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.source.strip():
            raise ValueError("telemetry node_id and source are required")
        numeric = (
            self.observed_monotonic_seconds,
            self.cpu_utilization_fraction,
            self.memory_utilization_fraction,
            self.throughput_mbps,
            self.latency_ms,
        )
        if any(not math.isfinite(value) for value in numeric):
            raise ValueError("telemetry values must be finite")
        if self.observed_monotonic_seconds < 0:
            raise ValueError("observed_monotonic_seconds cannot be negative")
        for name, value in (
            ("cpu_utilization_fraction", self.cpu_utilization_fraction),
            ("memory_utilization_fraction", self.memory_utilization_fraction),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.throughput_mbps < 0 or self.latency_ms < 0:
            raise ValueError("throughput and latency cannot be negative")
        if self.dropped_packets < 0 or self.active_flows < 0 or self.state_size_bytes < 0:
            raise ValueError("telemetry counters cannot be negative")

    def age_seconds(self, now_monotonic_seconds: float) -> float:
        if not math.isfinite(now_monotonic_seconds):
            raise ValueError("current monotonic time must be finite")
        if now_monotonic_seconds < self.observed_monotonic_seconds:
            raise ValueError("current monotonic time cannot precede observation")
        return now_monotonic_seconds - self.observed_monotonic_seconds

    def is_fresh(self, now_monotonic_seconds: float, maximum_age_seconds: float) -> bool:
        if maximum_age_seconds < 0 or not math.isfinite(maximum_age_seconds):
            raise ValueError("maximum telemetry age must be finite and non-negative")
        return self.age_seconds(now_monotonic_seconds) <= maximum_age_seconds

    def measured_metrics(self) -> dict[str, float]:
        return {
            "cpu_utilization_fraction": self.cpu_utilization_fraction,
            "memory_utilization_fraction": self.memory_utilization_fraction,
            "throughput_mbps": self.throughput_mbps,
            "latency_ms": self.latency_ms,
            "dropped_packets_count": float(self.dropped_packets),
            "active_flows_count": float(self.active_flows),
            "state_size_bytes": float(self.state_size_bytes),
            "health_boolean": 1.0 if self.healthy else 0.0,
        }


@dataclass(frozen=True)
class NetworkTelemetrySnapshot:
    """Validated network counters from the privileged namespace collector."""

    namespace: str
    observed_utc: str
    observed_monotonic_seconds: float
    source: str
    conntrack_entries: int
    firewall_table_present: bool
    interfaces: dict[str, dict[str, dict[str, int]]]

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> NetworkTelemetrySnapshot:
        if record.get("schema_version") != 1:
            raise ValueError("unsupported network telemetry schema version")
        namespace = str(record.get("namespace", ""))
        source = str(record.get("source", ""))
        timestamp = str(record.get("observed_utc", ""))
        if not namespace or not source or not timestamp.endswith("Z"):
            raise ValueError("namespace, source and UTC timestamp are required")
        observed = float(record["observed_monotonic_seconds"])
        if not math.isfinite(observed) or observed < 0:
            raise ValueError("observed monotonic time must be finite and non-negative")
        count = int(record["conntrack_entries"])
        if count < 0 or count != record["conntrack_entries"]:
            raise ValueError("conntrack count must be a non-negative integer")
        interfaces = record["interfaces"]
        if not isinstance(interfaces, dict) or not interfaces:
            raise ValueError("at least one interface is required")
        for interface, directions in interfaces.items():
            if not interface:
                raise ValueError("interface name cannot be empty")
            for direction in ("rx", "tx"):
                for field in ("bytes", "packets", "dropped", "errors"):
                    value = directions[direction][field]
                    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                        raise ValueError(f"invalid {interface}.{direction}.{field} counter")
        if record.get("firewall_table_present") is not True:
            raise ValueError("firewall table must be present")
        return cls(namespace, timestamp, observed, source, count, True, interfaces)

    def is_fresh(self, now_monotonic_seconds: float, maximum_age_seconds: float) -> bool:
        if not math.isfinite(now_monotonic_seconds) or not math.isfinite(maximum_age_seconds):
            raise ValueError("freshness inputs must be finite")
        if maximum_age_seconds < 0 or now_monotonic_seconds < self.observed_monotonic_seconds:
            raise ValueError("invalid telemetry freshness interval")
        return now_monotonic_seconds - self.observed_monotonic_seconds <= maximum_age_seconds

    def measured_metrics(self) -> dict[str, float]:
        result = {"conntrack_entries_count": float(self.conntrack_entries)}
        for name, directions in sorted(self.interfaces.items()):
            for direction in ("rx", "tx"):
                for field in ("bytes", "packets", "dropped", "errors"):
                    result[f"interface.{name}.{direction}.{field}"] = float(
                        directions[direction][field]
                    )
        return result
