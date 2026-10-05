"""Deterministic flow-affine load assignment for active vFW instances."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FirewallInstance:
    instance_id: str
    active_flows: int
    capacity_flows: int
    healthy: bool = True
    accepting_new_flows: bool = True

    @property
    def utilization(self) -> float:
        if self.capacity_flows <= 0:
            raise ValueError("capacity_flows must be positive")
        return self.active_flows / self.capacity_flows


@dataclass(frozen=True)
class FlowAssignment:
    flow_id: str
    instance_id: str
    reused_pin: bool
    reason: str


class NoEligibleFirewall(RuntimeError):
    pass


class FlowDirector:
    def __init__(self) -> None:
        self._pins: dict[str, str] = {}

    def assign(self, flow_id: str, instances: list[FirewallInstance]) -> FlowAssignment:
        if not flow_id.strip():
            raise ValueError("flow_id is required")
        by_id = {instance.instance_id: instance for instance in instances}
        pinned_id = self._pins.get(flow_id)
        if pinned_id is not None:
            pinned = by_id.get(pinned_id)
            if pinned is not None and pinned.healthy:
                return FlowAssignment(flow_id, pinned_id, True, "existing flow pin preserved")
            raise NoEligibleFirewall(
                "established flow pin is unavailable; explicit migration/fallback is required"
            )

        eligible = [
            instance
            for instance in instances
            if instance.healthy
            and instance.accepting_new_flows
            and instance.active_flows < instance.capacity_flows
        ]
        if not eligible:
            raise NoEligibleFirewall("no healthy vFW accepts new flows with spare capacity")
        selected = min(eligible, key=lambda item: (item.utilization, item.instance_id))
        self._pins[flow_id] = selected.instance_id
        return FlowAssignment(flow_id, selected.instance_id, False, "least-utilized eligible vFW")

    def release(self, flow_id: str) -> bool:
        return self._pins.pop(flow_id, None) is not None

    def pinned_instance(self, flow_id: str) -> str | None:
        return self._pins.get(flow_id)

