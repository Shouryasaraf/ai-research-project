"""Explainable defensive node-risk model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class RiskInputs:
    vulnerability: float
    exposure: float
    anomaly_signal: float
    trust_deficit: float
    staleness: float


@dataclass(frozen=True)
class RiskWeights:
    vulnerability: float
    exposure: float
    anomaly_signal: float
    trust_deficit: float
    staleness: float

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(not math.isfinite(value) or value < 0 for value in values.values()) or abs(sum(values.values()) - 1) > 1e-9:
            raise ValueError("risk weights must be non-negative and sum to 1")


@dataclass(frozen=True)
class RiskScore:
    total: float
    contributions: dict[str, float]


def calculate_risk(inputs: RiskInputs, weights: RiskWeights) -> RiskScore:
    input_values = asdict(inputs)
    if any(not 0 <= value <= 1 for value in input_values.values()):
        raise ValueError("normalized risk inputs must be between 0 and 1")
    weight_values = asdict(weights)
    contributions = {name: input_values[name] * weight_values[name] for name in input_values}
    return RiskScore(sum(contributions.values()), contributions)
