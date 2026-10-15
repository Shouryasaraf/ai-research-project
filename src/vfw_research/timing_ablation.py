"""Predeclared fixed-delay reactive arm for migration-timing decomposition.

This is an experimental control, not the submitted controller. It preserves
reactive safety/placement checks but schedules warm sync at decision step 2
and route commit no earlier than step 3 after any reactive overload trigger.
"""
from dataclasses import replace

from .models import ControllerDecision, GateAction


POLICY_NAME = "reactive_fixed_timing_warm_experimental"


def scheduled_reactive_decision(
    baseline: ControllerDecision, *, step: int, triggered: bool, synced: bool
) -> ControllerDecision:
    if baseline.action is GateAction.FALLBACK or baseline.selected_node_id is None:
        return baseline
    if step < 2 or not triggered:
        return replace(baseline, action=GateAction.WAIT,
                       reason="fixed-timing reactive control: waiting for scheduled sync")
    if step == 2:
        return replace(baseline, action=GateAction.SYNC,
                       reason="fixed-timing reactive control: scheduled warm sync")
    if synced:
        return replace(baseline, action=GateAction.COMMIT,
                       reason="fixed-timing reactive control: scheduled route commit")
    return replace(baseline, action=GateAction.WAIT,
                   reason="fixed-timing reactive control: sync prerequisite absent")
