"""Experimental bounded liveness escape for the fixed-width uncertainty gate.

This is a distinct research policy, not a silent change to the original full
controller. It uses only already observed utilization and prior baseline waits.
It does not bypass security invariants, target feasibility, readiness or the
benefit threshold. Its three-slot setting is an engineering pilot value, not a
calibrated or independently validated optimum.
"""

from __future__ import annotations

from dataclasses import replace

from .models import GateAction
from .policies import PolicyOutcome, PolicyRunInput, PolicyVariant, run_policy

POLICY_NAME = "full_liveness_guarded_experimental"
MIN_OBSERVED_OVERLOAD_SLOTS = 3
MIN_UNCERTAIN_WAIT_SLOTS = 3
UNCERTAINTY_WAIT_REASON = "target is warm; wait for lower uncertainty before commit"


def is_uncertainty_wait(outcome: PolicyOutcome) -> bool:
    return (outcome.decision.action is GateAction.WAIT
            and outcome.decision.reason == UNCERTAINTY_WAIT_REASON)


def suppress_after_route(outcome: PolicyOutcome) -> PolicyOutcome:
    """Do not report a second migration toward the already active target.

    A security FALLBACK remains visible; this helper is only action accounting,
    not a replacement for a production route-failback controller.
    """
    if outcome.decision.action is GateAction.FALLBACK:
        return outcome
    return replace(outcome, decision=replace(
        outcome.decision, action=GateAction.WAIT,
        reason="already routed through the selected target",
    ))


def run_liveness_guarded(
    run: PolicyRunInput,
    *,
    observed_overload_streak: int,
    uncertainty_wait_streak: int,
    baseline: PolicyOutcome | None = None,
) -> PolicyOutcome:
    if min(observed_overload_streak, uncertainty_wait_streak) < 0:
        raise ValueError("streak counts must be non-negative")
    original = baseline if baseline is not None else run_policy(PolicyVariant.FULL, run)
    if original.variant is not PolicyVariant.FULL:
        raise ValueError("liveness guard requires the full controller baseline")
    decision = original.decision
    if not is_uncertainty_wait(original):
        return original
    if (observed_overload_streak < MIN_OBSERVED_OVERLOAD_SLOTS
            or uncertainty_wait_streak < MIN_UNCERTAIN_WAIT_SLOTS):
        return original
    if (decision.invariant_violations or decision.selected_node_id is None
            or decision.net_benefit <= decision.adaptive_threshold
            or not run.decision_input.telemetry_fresh):
        return original
    if run.decision_input.forecast.width_fraction(run.decision_input.source_capacity_mbps) <= run.max_commit_interval_width_fraction:
        return original
    # The original decision has already established the hard placement and
    # invariant gates. Only the width gate is bypassed after observed overload.
    action = GateAction.SYNC if not run.decision_input.state_synchronized else GateAction.COMMIT
    return replace(original, decision=replace(
        decision, action=action,
        reason=("liveness escape after sustained observed overload and uncertainty wait; "
                "security, benefit and readiness gates retained"),
    ))
