"""Validated JSON scenarios for paired, deterministic policy experiments."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import (
    BenefitTerms,
    DecisionInput,
    Forecast,
    NodeCandidate,
    PlacementPolicy,
    PlacementWeights,
    SecuritySnapshot,
    ThresholdContext,
    ThresholdPolicy,
)
from .policies import PolicyRunInput


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    synthetic_inputs: bool
    seeds: tuple[int, ...]
    payload: dict[str, Any]

    def build_run(self, seed: int) -> PolicyRunInput:
        if seed not in self.seeds:
            raise ValueError(f"seed {seed} is not declared by scenario {self.scenario_id}")
        data = self.payload
        forecast_data = data["forecast"]
        jitter = float(forecast_data.get("jitter_fraction", 0.0))
        factor = 1.0 + random.Random(seed).uniform(-jitter, jitter)
        forecast = Forecast(
            float(forecast_data["point_mbps"]) * factor,
            float(forecast_data["lower_mbps"]) * factor,
            float(forecast_data["upper_mbps"]) * factor,
            int(forecast_data["horizon_seconds"]),
            str(forecast_data["model_version"]),
        )
        invariant_data = data["invariants"]
        benefit_data = data["benefit_terms"]
        context_data = data["threshold_context"]
        decision_input = DecisionInput(
            source_capacity_mbps=float(data["source_capacity_mbps"]),
            forecast=forecast,
            target_warm=bool(data["target_warm"]),
            state_synchronized=bool(data["state_synchronized"]),
            invariants=SecuritySnapshot(**invariant_data),
            benefit_terms=BenefitTerms(**benefit_data),
            threshold_context=ThresholdContext(**context_data),
            telemetry_fresh=bool(data.get("telemetry_fresh", True)),
        )
        candidates = [NodeCandidate(**candidate) for candidate in data["candidates"]]
        placement_data = data["placement_policy"]
        placement = PlacementPolicy(
            max_security_risk=float(placement_data["max_security_risk"]),
            minimum_cpu_fraction=float(placement_data["minimum_cpu_fraction"]),
            minimum_memory_fraction=float(placement_data["minimum_memory_fraction"]),
            max_latency_ms=float(placement_data["max_latency_ms"]),
            weights=PlacementWeights(**placement_data["weights"]),
        )
        return PolicyRunInput(
            current_utilization=float(data["current_utilization"]),
            decision_input=decision_input,
            candidates=candidates,
            placement_policy=placement,
            threshold_policy=ThresholdPolicy(**data["threshold_policy"]),
            overload_trigger_fraction=float(data["overload_trigger_fraction"]),
            max_commit_interval_width_fraction=float(
                data["max_commit_interval_width_fraction"]
            ),
            fixed_threshold=float(data.get("fixed_threshold", 0.25)),
        )


def load_scenario(path: Path) -> ScenarioDefinition:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("scenario root must be a JSON object")
    scenario_id = str(payload.get("scenario_id", "")).strip()
    if not scenario_id:
        raise ValueError("scenario_id is required")
    seeds_raw = payload.get("seeds")
    if not isinstance(seeds_raw, list) or not seeds_raw:
        raise ValueError("seeds must be a non-empty list")
    seeds = tuple(int(seed) for seed in seeds_raw)
    if any(seed < 0 for seed in seeds) or len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique non-negative integers")
    if not payload.get("candidates"):
        raise ValueError("at least one candidate is required")
    scenario = ScenarioDefinition(
        scenario_id=scenario_id,
        synthetic_inputs=bool(payload.get("synthetic_inputs", True)),
        seeds=seeds,
        payload=payload,
    )
    for seed in seeds:
        scenario.build_run(seed)
    return scenario
