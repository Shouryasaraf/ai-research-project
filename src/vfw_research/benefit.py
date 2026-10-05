"""Auditable migration benefit and adaptive-threshold calculations."""

from __future__ import annotations

from .models import BenefitBreakdown, BenefitTerms, ThresholdContext, ThresholdPolicy


def calculate_benefit(terms: BenefitTerms) -> BenefitBreakdown:
    """Return net benefit in normalized utility points without hiding its terms."""
    positive = (
        terms.operational_benefit
        + terms.carbon_benefit
        + terms.risk_reduction_benefit
    )
    negative = (
        terms.migration_cost
        + terms.disruption_penalty
        + terms.uncertainty_penalty
        + terms.operational_overhead
    )
    return BenefitBreakdown(terms=terms, net_benefit=positive - negative)


def adaptive_threshold(context: ThresholdContext, policy: ThresholdPolicy) -> float:
    """Calculate the contextual commit margin in normalized utility points."""
    if context.state_size_mb < 0 or context.active_flows < 0 or context.recent_failures < 0:
        raise ValueError("threshold context counts and state size must be non-negative")
    for name, value in (
        ("uncertainty_fraction", context.uncertainty_fraction),
        ("sla_criticality", context.sla_criticality),
        ("target_headroom_fraction", context.target_headroom_fraction),
    ):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")

    threshold = (
        policy.base
        + context.state_size_mb * policy.state_size_per_mb
        + context.active_flows * policy.active_flow_weight
        + context.uncertainty_fraction * policy.uncertainty_weight
        + context.recent_failures * policy.recent_failure_weight
        + context.sla_criticality * policy.sla_criticality_weight
        + (policy.cooldown_penalty if context.cooldown_active else 0.0)
        - context.target_headroom_fraction * policy.headroom_relief_weight
    )
    return min(policy.maximum, max(policy.minimum, threshold))

