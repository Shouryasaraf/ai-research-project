"""Security invariant validation; failures cannot be offset by a score."""

from __future__ import annotations

from .models import SecuritySnapshot


def validate_security_invariants(snapshot: SecuritySnapshot) -> tuple[str, ...]:
    violations: list[str] = []
    if snapshot.source_policy_hash != snapshot.expected_policy_hash:
        violations.append("source_policy_mismatch")
    if snapshot.target_policy_hash != snapshot.expected_policy_hash:
        violations.append("target_policy_mismatch")
    if not snapshot.traffic_path_enforced:
        violations.append("firewall_path_not_enforced")
    if not snapshot.default_deny_enabled:
        violations.append("default_deny_disabled")
    if not snapshot.target_allowed:
        violations.append("target_not_allowed")
    if not snapshot.target_healthy:
        violations.append("target_unhealthy")
    if not snapshot.capacity_sufficient:
        violations.append("target_capacity_insufficient")
    if snapshot.state_mismatch_fraction > snapshot.maximum_state_mismatch_fraction:
        violations.append("state_mismatch_above_tolerance")
    if not snapshot.audit_available:
        violations.append("audit_unavailable")
    return tuple(violations)

