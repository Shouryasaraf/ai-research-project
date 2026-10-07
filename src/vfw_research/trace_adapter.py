"""Strict, offline CSV adapter for externally sourced research time series.

This module does not download data or imply that any external dataset is
already present. A provenance sidecar is mandatory for each imported trace.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path


class TraceKind(str, Enum):
    TRAFFIC = "traffic"
    CARBON = "carbon"
    RISK = "risk"


UNITS = {
    TraceKind.TRAFFIC: "Mbps",
    TraceKind.CARBON: "gCO2/kWh",
    TraceKind.RISK: "score_0_1",
}


@dataclass(frozen=True)
class TracePoint:
    observed_utc: datetime
    value: float


@dataclass(frozen=True)
class ImportedTrace:
    kind: TraceKind
    unit: str
    source: str
    license: str
    version: str
    retrieved_utc: datetime
    preprocessing: str
    missing_data_policy: str
    csv_sha256: str
    sampling_interval_seconds: int
    points: tuple[TracePoint, ...]


def _parse_utc(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"invalid ISO-8601 timestamp: {value}") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("all timestamps must explicitly use UTC")
    return parsed.astimezone(timezone.utc)


def load_trace(csv_path: Path, sidecar_path: Path) -> ImportedTrace:
    """Load exact `timestamp_utc,value` data after metadata and SHA-256 checks."""
    metadata = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if not isinstance(metadata, dict):
        raise ValueError("provenance sidecar must be a JSON object")
    required = ("kind", "unit", "source", "license", "version", "sha256",
                "retrieved_utc", "preprocessing", "missing_data_policy",
                "sampling_interval_seconds")
    missing = [name for name in required if not metadata.get(name)]
    if missing:
        raise ValueError("missing trace provenance: " + ", ".join(missing))
    try:
        kind = TraceKind(metadata["kind"])
    except ValueError as error:
        raise ValueError("unknown trace kind") from error
    if metadata["unit"] != UNITS[kind]:
        raise ValueError(f"{kind.value} trace unit must be {UNITS[kind]}")
    text_fields = ("source", "license", "version", "sha256", "retrieved_utc",
                   "preprocessing", "missing_data_policy")
    if not all(isinstance(metadata[name], str) and metadata[name].strip()
               for name in text_fields):
        raise ValueError("all provenance text fields must be non-empty strings")
    if not metadata["source"].startswith(("https://", "http://", "doi:")):
        raise ValueError("external trace source must be a stable URL or DOI")
    retrieved = _parse_utc(metadata["retrieved_utc"])
    interval = metadata["sampling_interval_seconds"]
    if isinstance(interval, bool) or not isinstance(interval, int) or interval <= 0:
        raise ValueError("sampling_interval_seconds must be a positive integer")
    raw = csv_path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != metadata["sha256"]:
        raise ValueError("trace checksum does not match provenance sidecar")
    rows = csv.DictReader(raw.decode("utf-8-sig").splitlines())
    if rows.fieldnames != ["timestamp_utc", "value"]:
        raise ValueError("CSV header must be exactly timestamp_utc,value")
    points = []
    previous: datetime | None = None
    for number, row in enumerate(rows, start=2):
        if None in row or set(row) != {"timestamp_utc", "value"}:
            raise ValueError(f"malformed CSV row {number}")
        timestamp = _parse_utc(row["timestamp_utc"])
        try:
            value = float(row["value"])
        except (TypeError, ValueError) as error:
            raise ValueError(f"non-numeric value at row {number}") from error
        if not math.isfinite(value) or value < 0 or (kind is TraceKind.RISK and value > 1):
            raise ValueError(f"out-of-range value at row {number}")
        if previous is not None and timestamp - previous != timedelta(seconds=interval):
            raise ValueError(f"missing, duplicate, or irregular timestamp at row {number}")
        points.append(TracePoint(timestamp, value))
        previous = timestamp
    if not points:
        raise ValueError("trace must contain at least one observation")
    return ImportedTrace(
        kind, metadata["unit"], metadata["source"], metadata["license"],
        metadata["version"], retrieved, metadata["preprocessing"],
        metadata["missing_data_policy"], digest, interval, tuple(points),
    )
