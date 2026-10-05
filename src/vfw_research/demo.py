"""Deterministic Stage 1 smoke scenario; this is not a network experiment."""

from __future__ import annotations

import json
from pathlib import Path

from .audit import JsonlAuditLog
from .controller import decide
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


def build_smoke_decision():
    forecast = Forecast(86.0, 82.0, 90.0, 60, "deterministic-smoke-v1")
    candidates = [
        NodeCandidate("node-green", 200, 20, 0.8, 0.75, 18, 120, 0.18),
        NodeCandidate("node-risky", 250, 10, 0.9, 0.9, 12, 80, 0.90),
    ]
    placement_policy = PlacementPolicy(
        max_security_risk=0.65,
        minimum_cpu_fraction=0.15,
        minimum_memory_fraction=0.15,
        max_latency_ms=100,
        weights=PlacementWeights(0.30, 0.15, 0.20, 0.25, 0.10),
    )
    threshold_policy = ThresholdPolicy(
        base=0.20,
        state_size_per_mb=0.0005,
        active_flow_weight=0.0002,
        uncertainty_weight=0.30,
        recent_failure_weight=0.10,
        sla_criticality_weight=0.20,
        cooldown_penalty=0.50,
        headroom_relief_weight=0.10,
        minimum=0.05,
        maximum=2.00,
    )
    decision_input = DecisionInput(
        source_capacity_mbps=100,
        forecast=forecast,
        target_warm=True,
        state_synchronized=True,
        invariants=SecuritySnapshot(
            source_policy_hash="policy-v1",
            target_policy_hash="policy-v1",
            expected_policy_hash="policy-v1",
            traffic_path_enforced=True,
            default_deny_enabled=True,
            target_allowed=True,
            target_healthy=True,
            capacity_sufficient=True,
            state_mismatch_fraction=0.0,
            maximum_state_mismatch_fraction=0.01,
            audit_available=True,
        ),
        benefit_terms=BenefitTerms(0.75, 0.12, 0.20, 0.15, 0.08, 0.04, 0.04),
        threshold_context=ThresholdContext(20, 80, 0.08, 0, 0.5, False, 0.45),
    )
    return decide(
        decision_input,
        candidates,
        placement_policy,
        threshold_policy,
        overload_trigger_fraction=0.80,
        max_commit_interval_width_fraction=0.20,
    )


def main() -> None:
    decision = build_smoke_decision()
    audit_path = Path("artifacts/raw/stage1-smoke-events.jsonl")
    JsonlAuditLog(audit_path).append("controller_decision", decision.as_record())
    print(json.dumps(decision.as_record(), indent=2, sort_keys=True))
    print(f"audit_path={audit_path}")


if __name__ == "__main__":
    main()

