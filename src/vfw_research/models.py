"""Typed domain models shared by controller components."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class GateAction(str, Enum):
    WAIT = "WAIT"
    PREWARM = "PREWARM"
    SYNC = "SYNC"
    COMMIT = "COMMIT"
    FALLBACK = "FALLBACK"


class MigrationState(str, Enum):
    OBSERVE = "OBSERVE"
    WAIT = "WAIT"
    PREWARM = "PREWARM"
    SYNC = "SYNC"
    VALIDATE = "VALIDATE"
    COMMIT = "COMMIT"
    DRAIN = "DRAIN"
    COMPLETE = "COMPLETE"
    ABORT = "ABORT"
    FALLBACK = "FALLBACK"


@dataclass(frozen=True)
class Forecast:
    point_mbps: float
    lower_mbps: float
    upper_mbps: float
    horizon_seconds: int
    model_version: str

    def __post_init__(self) -> None:
        if self.lower_mbps < 0 or self.point_mbps < 0 or self.upper_mbps < 0:
            raise ValueError("forecast values must be non-negative")
        if not self.lower_mbps <= self.point_mbps <= self.upper_mbps:
            raise ValueError("forecast must satisfy lower <= point <= upper")
        if self.horizon_seconds <= 0:
            raise ValueError("forecast horizon must be positive")

    def width_fraction(self, capacity_mbps: float) -> float:
        if capacity_mbps <= 0:
            raise ValueError("capacity must be positive")
        return (self.upper_mbps - self.lower_mbps) / capacity_mbps


@dataclass(frozen=True)
class NodeCandidate:
    node_id: str
    capacity_mbps: float
    current_load_mbps: float
    available_cpu_fraction: float
    available_memory_fraction: float
    latency_ms: float
    carbon_gco2_per_kwh: float
    security_risk: float
    healthy: bool = True
    allowed: bool = True

    def __post_init__(self) -> None:
        if self.capacity_mbps <= 0:
            raise ValueError("capacity_mbps must be positive")
        if self.current_load_mbps < 0:
            raise ValueError("current_load_mbps cannot be negative")
        for name, value in (
            ("available_cpu_fraction", self.available_cpu_fraction),
            ("available_memory_fraction", self.available_memory_fraction),
            ("security_risk", self.security_risk),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")

    @property
    def spare_capacity_mbps(self) -> float:
        return max(0.0, self.capacity_mbps - self.current_load_mbps)


@dataclass(frozen=True)
class PlacementWeights:
    capacity: float
    latency: float
    carbon: float
    security_risk: float
    uncertainty_headroom: float

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(value < 0 for value in values.values()):
            raise ValueError("placement weights cannot be negative")
        if abs(sum(values.values()) - 1.0) > 1e-9:
            raise ValueError("placement weights must sum to 1")


@dataclass(frozen=True)
class PlacementPolicy:
    max_security_risk: float
    minimum_cpu_fraction: float
    minimum_memory_fraction: float
    max_latency_ms: float
    weights: PlacementWeights


@dataclass(frozen=True)
class PlacementResult:
    node_id: str
    score: float
    components: dict[str, float]


@dataclass(frozen=True)
class BenefitTerms:
    operational_benefit: float
    carbon_benefit: float
    risk_reduction_benefit: float
    migration_cost: float
    disruption_penalty: float
    uncertainty_penalty: float
    operational_overhead: float


@dataclass(frozen=True)
class BenefitBreakdown:
    terms: BenefitTerms
    net_benefit: float


@dataclass(frozen=True)
class ThresholdContext:
    state_size_mb: float
    active_flows: int
    uncertainty_fraction: float
    recent_failures: int
    sla_criticality: float
    cooldown_active: bool
    target_headroom_fraction: float


@dataclass(frozen=True)
class ThresholdPolicy:
    base: float
    state_size_per_mb: float
    active_flow_weight: float
    uncertainty_weight: float
    recent_failure_weight: float
    sla_criticality_weight: float
    cooldown_penalty: float
    headroom_relief_weight: float
    minimum: float
    maximum: float


@dataclass(frozen=True)
class SecuritySnapshot:
    source_policy_hash: str
    target_policy_hash: str
    expected_policy_hash: str
    traffic_path_enforced: bool
    default_deny_enabled: bool
    target_allowed: bool
    target_healthy: bool
    capacity_sufficient: bool
    state_mismatch_fraction: float
    maximum_state_mismatch_fraction: float
    audit_available: bool


@dataclass(frozen=True)
class DecisionInput:
    source_capacity_mbps: float
    forecast: Forecast
    target_warm: bool
    state_synchronized: bool
    invariants: SecuritySnapshot
    benefit_terms: BenefitTerms
    threshold_context: ThresholdContext


@dataclass(frozen=True)
class ControllerDecision:
    action: GateAction
    reason: str
    selected_node_id: str | None
    net_benefit: float
    adaptive_threshold: float
    invariant_violations: tuple[str, ...]
    placement_components: dict[str, float]
    model_version: str

    def as_record(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "reason": self.reason,
            "selected_node_id": self.selected_node_id,
            "net_benefit": self.net_benefit,
            "adaptive_threshold": self.adaptive_threshold,
            "invariant_violations": list(self.invariant_violations),
            "placement_components": self.placement_components,
            "model_version": self.model_version,
        }

