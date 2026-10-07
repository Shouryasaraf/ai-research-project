"""Common interface for proposed, baseline, and ablation decision policies."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from .benefit import calculate_benefit
from .controller import decide
from .invariants import validate_security_invariants
from .models import (
    ControllerDecision,
    DecisionInput,
    GateAction,
    NodeCandidate,
    PlacementPolicy,
    PlacementWeights,
    ThresholdPolicy,
)
from .placement import evaluate_placement


class PolicyVariant(str, Enum):
    STATIC = "static_no_migration"
    REACTIVE = "reactive_threshold"
    PREDICTION_ONLY = "prediction_only"
    UNCERTAINTY_NO_CARBON_RISK = "uncertainty_without_carbon_or_risk"
    RISK_UNAWARE = "risk_unaware"
    CARBON_UNAWARE = "carbon_unaware"
    COLD_MIGRATION = "cold_migration"
    FIXED_THRESHOLD = "fixed_benefit_threshold"
    FULL = "full_proposed_controller"


@dataclass(frozen=True)
class PolicyRunInput:
    current_utilization: float
    decision_input: DecisionInput
    candidates: list[NodeCandidate]
    placement_policy: PlacementPolicy
    threshold_policy: ThresholdPolicy
    overload_trigger_fraction: float
    max_commit_interval_width_fraction: float
    fixed_threshold: float = 0.25


@dataclass(frozen=True)
class PolicyOutcome:
    variant: PolicyVariant
    decision: ControllerDecision
    migration_mode: str


def _simple_decision(
    run: PolicyRunInput, *, use_prediction: bool, variant: PolicyVariant
) -> ControllerDecision:
    placement = evaluate_placement(run.candidates, run.decision_input.forecast, run.placement_policy)
    selected = placement.ranked[0] if placement.ranked else None
    violations = list(validate_security_invariants(run.decision_input.invariants))
    if not run.decision_input.telemetry_fresh:
        violations.append("telemetry_stale")
    violations_tuple = tuple(violations)
    signal = (
        run.decision_input.forecast.point_mbps / run.decision_input.source_capacity_mbps
        if use_prediction
        else run.current_utilization
    )
    benefit = calculate_benefit(run.decision_input.benefit_terms).net_benefit
    action = GateAction.WAIT
    reason = f"{variant.value}: trigger not reached"
    if violations_tuple:
        action = GateAction.FALLBACK
        reason = f"{variant.value}: security invariant or telemetry freshness failure"
    elif selected is None:
        reason = f"{variant.value}: no feasible candidate"
    elif signal >= run.overload_trigger_fraction:
        action = GateAction.COMMIT
        reason = f"{variant.value}: threshold reached"
    return ControllerDecision(
        action,
        reason,
        selected.node_id if selected else None,
        benefit,
        0.0,
        violations_tuple,
        selected.components if selected else {},
        run.decision_input.forecast.model_version,
    )


def _weights_without(*excluded: str) -> PlacementWeights:
    base = {
        "capacity": 0.30,
        "latency": 0.15,
        "carbon": 0.20,
        "security_risk": 0.25,
        "uncertainty_headroom": 0.10,
    }
    for name in excluded:
        base[name] = 0.0
    total = sum(base.values())
    normalized = {name: value / total for name, value in base.items()}
    return PlacementWeights(**normalized)


def run_policy(variant: PolicyVariant, run: PolicyRunInput) -> PolicyOutcome:
    if not 0 <= run.current_utilization <= 1:
        raise ValueError("current utilization must be between 0 and 1")
    if variant is PolicyVariant.STATIC:
        decision = ControllerDecision(
            GateAction.WAIT,
            "static baseline never migrates",
            None,
            0.0,
            0.0,
            (),
            {},
            run.decision_input.forecast.model_version,
        )
        return PolicyOutcome(variant, decision, "none")
    if variant is PolicyVariant.REACTIVE:
        return PolicyOutcome(variant, _simple_decision(run, use_prediction=False, variant=variant), "warm")
    if variant is PolicyVariant.PREDICTION_ONLY:
        return PolicyOutcome(variant, _simple_decision(run, use_prediction=True, variant=variant), "warm")

    placement = run.placement_policy
    threshold = run.threshold_policy
    migration_mode = "warm"
    if variant is PolicyVariant.UNCERTAINTY_NO_CARBON_RISK:
        placement = replace(
            placement,
            max_security_risk=1.0,
            weights=_weights_without("carbon", "security_risk"),
        )
    elif variant is PolicyVariant.RISK_UNAWARE:
        placement = replace(
            placement, max_security_risk=1.0, weights=_weights_without("security_risk")
        )
    elif variant is PolicyVariant.CARBON_UNAWARE:
        placement = replace(placement, weights=_weights_without("carbon"))
    elif variant is PolicyVariant.COLD_MIGRATION:
        migration_mode = "cold"
    elif variant is PolicyVariant.FIXED_THRESHOLD:
        threshold = ThresholdPolicy(
            run.fixed_threshold, 0, 0, 0, 0, 0, 0, 0, run.fixed_threshold, run.fixed_threshold
        )

    decision = decide(
        run.decision_input,
        run.candidates,
        placement,
        threshold,
        overload_trigger_fraction=run.overload_trigger_fraction,
        max_commit_interval_width_fraction=run.max_commit_interval_width_fraction,
    )
    return PolicyOutcome(variant, decision, migration_mode)


def run_all_policies(run: PolicyRunInput) -> tuple[PolicyOutcome, ...]:
    return tuple(run_policy(variant, run) for variant in PolicyVariant)
