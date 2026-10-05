"""Hard-constrained, explainable candidate placement."""

from __future__ import annotations

from dataclasses import dataclass

from .models import Forecast, NodeCandidate, PlacementPolicy, PlacementResult


@dataclass(frozen=True)
class RejectedNode:
    node_id: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class PlacementEvaluation:
    ranked: tuple[PlacementResult, ...]
    rejected: tuple[RejectedNode, ...]


def _constraint_failures(
    node: NodeCandidate, forecast: Forecast, policy: PlacementPolicy
) -> tuple[str, ...]:
    failures: list[str] = []
    if not node.allowed:
        failures.append("node_not_allowed")
    if not node.healthy:
        failures.append("node_unhealthy")
    if node.security_risk > policy.max_security_risk:
        failures.append("security_risk_above_limit")
    if node.available_cpu_fraction < policy.minimum_cpu_fraction:
        failures.append("insufficient_cpu")
    if node.available_memory_fraction < policy.minimum_memory_fraction:
        failures.append("insufficient_memory")
    if node.latency_ms > policy.max_latency_ms:
        failures.append("latency_above_limit")
    if node.spare_capacity_mbps < forecast.upper_mbps:
        failures.append("insufficient_uncertainty_headroom")
    return tuple(failures)


def evaluate_placement(
    nodes: list[NodeCandidate], forecast: Forecast, policy: PlacementPolicy
) -> PlacementEvaluation:
    if not nodes:
        raise ValueError("at least one candidate node is required")

    ranked: list[PlacementResult] = []
    rejected: list[RejectedNode] = []
    max_carbon = max(node.carbon_gco2_per_kwh for node in nodes) or 1.0

    for node in nodes:
        failures = _constraint_failures(node, forecast, policy)
        if failures:
            rejected.append(RejectedNode(node.node_id, failures))
            continue

        residual_after_forecast = node.spare_capacity_mbps - forecast.point_mbps
        capacity_component = min(1.0, max(0.0, residual_after_forecast / node.capacity_mbps))
        latency_component = 1.0 - min(1.0, node.latency_ms / policy.max_latency_ms)
        carbon_component = 1.0 - min(1.0, node.carbon_gco2_per_kwh / max_carbon)
        risk_component = 1.0 - node.security_risk
        uncertainty_headroom = min(
            1.0, max(0.0, (node.spare_capacity_mbps - forecast.upper_mbps) / node.capacity_mbps)
        )
        components = {
            "capacity": capacity_component,
            "latency": latency_component,
            "carbon": carbon_component,
            "security_risk": risk_component,
            "uncertainty_headroom": uncertainty_headroom,
        }
        weights = policy.weights
        score = (
            capacity_component * weights.capacity
            + latency_component * weights.latency
            + carbon_component * weights.carbon
            + risk_component * weights.security_risk
            + uncertainty_headroom * weights.uncertainty_headroom
        )
        ranked.append(PlacementResult(node.node_id, score, components))

    ranked.sort(key=lambda item: (-item.score, item.node_id))
    rejected.sort(key=lambda item: item.node_id)
    return PlacementEvaluation(tuple(ranked), tuple(rejected))

