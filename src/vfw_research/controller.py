"""Integrated deterministic placement and uncertainty-gated decision core."""

from __future__ import annotations

from .benefit import adaptive_threshold, calculate_benefit
from .invariants import validate_security_invariants
from .models import (
    ControllerDecision,
    DecisionInput,
    GateAction,
    NodeCandidate,
    PlacementPolicy,
    ThresholdPolicy,
)
from .placement import evaluate_placement


def decide(
    decision_input: DecisionInput,
    candidates: list[NodeCandidate],
    placement_policy: PlacementPolicy,
    threshold_policy: ThresholdPolicy,
    *,
    overload_trigger_fraction: float,
    max_commit_interval_width_fraction: float,
) -> ControllerDecision:
    if not 0 < overload_trigger_fraction <= 1:
        raise ValueError("overload_trigger_fraction must be in (0, 1]")
    if not 0 <= max_commit_interval_width_fraction <= 1:
        raise ValueError("max commit interval width must be between 0 and 1")

    placement = evaluate_placement(candidates, decision_input.forecast, placement_policy)
    selected = placement.ranked[0] if placement.ranked else None
    benefit = calculate_benefit(decision_input.benefit_terms)
    threshold = adaptive_threshold(decision_input.threshold_context, threshold_policy)
    violations = validate_security_invariants(decision_input.invariants)
    forecast = decision_input.forecast
    upper_utilization = forecast.upper_mbps / decision_input.source_capacity_mbps
    point_utilization = forecast.point_mbps / decision_input.source_capacity_mbps
    width_fraction = forecast.width_fraction(decision_input.source_capacity_mbps)

    common = {
        "selected_node_id": selected.node_id if selected else None,
        "net_benefit": benefit.net_benefit,
        "adaptive_threshold": threshold,
        "invariant_violations": violations,
        "placement_components": selected.components if selected else {},
        "model_version": forecast.model_version,
    }

    if violations:
        return ControllerDecision(
            action=GateAction.FALLBACK,
            reason="security invariant validation failed",
            **common,
        )
    if selected is None:
        return ControllerDecision(
            action=GateAction.WAIT,
            reason="no candidate satisfies hard placement constraints",
            **common,
        )
    if upper_utilization < overload_trigger_fraction:
        return ControllerDecision(
            action=GateAction.WAIT,
            reason="forecast upper bound remains below overload trigger",
            **common,
        )
    if width_fraction > max_commit_interval_width_fraction:
        return ControllerDecision(
            action=GateAction.PREWARM,
            reason="overload is plausible but forecast interval is too wide to commit",
            **common,
        )
    if not decision_input.target_warm:
        return ControllerDecision(
            action=GateAction.PREWARM,
            reason="target must be warmed before state synchronization",
            **common,
        )
    if not decision_input.state_synchronized:
        return ControllerDecision(
            action=GateAction.SYNC,
            reason="target is warm and requires state synchronization",
            **common,
        )
    if point_utilization < overload_trigger_fraction and benefit.net_benefit <= threshold:
        return ControllerDecision(
            action=GateAction.WAIT,
            reason="point forecast is below trigger and net benefit does not clear threshold",
            **common,
        )
    if benefit.net_benefit <= threshold:
        return ControllerDecision(
            action=GateAction.WAIT,
            reason="expected net benefit does not exceed adaptive threshold",
            **common,
        )
    return ControllerDecision(
        action=GateAction.COMMIT,
        reason="forecast, readiness, benefit, placement, and security gates passed",
        **common,
    )

