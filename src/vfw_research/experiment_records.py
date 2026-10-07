"""Immutable, schema-checked experiment records with evidence separation."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class RunStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class ExperimentRecord:
    run_id: str
    scenario_id: str
    policy_id: str
    seed: int
    synthetic_inputs: bool
    status: RunStatus
    started_utc: str
    finished_utc: str
    config_sha256: str
    environment: dict[str, str]
    measured_metrics: dict[str, float]
    modeled_metrics: dict[str, float]
    notes: tuple[str, ...] = ()
    decision: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        for name, value in (
            ("run_id", self.run_id),
            ("scenario_id", self.scenario_id),
            ("policy_id", self.policy_id),
            ("started_utc", self.started_utc),
            ("finished_utc", self.finished_utc),
            ("config_sha256", self.config_sha256),
        ):
            if not value.strip():
                raise ValueError(f"{name} is required")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        for group_name, metrics in (
            ("measured_metrics", self.measured_metrics),
            ("modeled_metrics", self.modeled_metrics),
        ):
            if any(not math.isfinite(value) for value in metrics.values()):
                raise ValueError(f"{group_name} contains a non-finite value")
        overlap = set(self.measured_metrics) & set(self.modeled_metrics)
        if overlap:
            raise ValueError(
                "measured_metrics and modeled_metrics must use distinct names: "
                + ", ".join(sorted(overlap))
            )
        if self.decision and not str(self.decision.get("action", "")).strip():
            raise ValueError("decision.action is required when a decision is recorded")


def configuration_digest(configuration: dict[str, Any]) -> str:
    encoded = json.dumps(configuration, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_immutable_record(directory: Path, record: ExperimentRecord) -> Path:
    record.validate()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{record.run_id}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(asdict(record), handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path
