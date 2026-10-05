"""Dynamic vFW scaling with hysteresis, consecutive evidence, and cooldown."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ScalingAction(str, Enum):
    HOLD = "HOLD"
    SCALE_OUT = "SCALE_OUT"
    SCALE_IN = "SCALE_IN"


@dataclass(frozen=True)
class ScalingPolicy:
    minimum_instances: int
    maximum_instances: int
    scale_out_utilization: float
    scale_in_utilization: float
    scale_out_observations: int
    scale_in_observations: int
    cooldown_seconds: float

    def __post_init__(self) -> None:
        if self.minimum_instances < 1 or self.maximum_instances < self.minimum_instances:
            raise ValueError("invalid instance bounds")
        if not 0 <= self.scale_in_utilization < self.scale_out_utilization <= 1:
            raise ValueError("scaling thresholds must provide hysteresis within [0, 1]")
        if self.scale_out_observations < 1 or self.scale_in_observations < 1:
            raise ValueError("observation counts must be positive")
        if self.cooldown_seconds < 0:
            raise ValueError("cooldown cannot be negative")


@dataclass(frozen=True)
class ScalingDecision:
    action: ScalingAction
    desired_instances: int
    reason: str


class ScalingManager:
    def __init__(self, policy: ScalingPolicy) -> None:
        self.policy = policy
        self._high_count = 0
        self._low_count = 0
        self._last_scale_time: float | None = None

    def observe(
        self,
        utilization: float,
        active_instances: int,
        timestamp_seconds: float,
        *,
        all_instances_healthy: bool = True,
    ) -> ScalingDecision:
        if not 0 <= utilization <= 1:
            raise ValueError("utilization must be between 0 and 1")
        if not self.policy.minimum_instances <= active_instances <= self.policy.maximum_instances:
            raise ValueError("active instance count is outside policy bounds")

        cooldown = (
            self._last_scale_time is not None
            and timestamp_seconds - self._last_scale_time < self.policy.cooldown_seconds
        )
        if not all_instances_healthy:
            self._high_count = 0
            self._low_count = 0
            return ScalingDecision(ScalingAction.HOLD, active_instances, "health gate failed")
        if cooldown:
            return ScalingDecision(ScalingAction.HOLD, active_instances, "cooldown active")

        if utilization >= self.policy.scale_out_utilization:
            self._high_count += 1
            self._low_count = 0
        elif utilization <= self.policy.scale_in_utilization:
            self._low_count += 1
            self._high_count = 0
        else:
            self._high_count = 0
            self._low_count = 0

        if (
            self._high_count >= self.policy.scale_out_observations
            and active_instances < self.policy.maximum_instances
        ):
            self._high_count = 0
            self._last_scale_time = timestamp_seconds
            return ScalingDecision(
                ScalingAction.SCALE_OUT, active_instances + 1, "sustained high utilization"
            )
        if (
            self._low_count >= self.policy.scale_in_observations
            and active_instances > self.policy.minimum_instances
        ):
            self._low_count = 0
            self._last_scale_time = timestamp_seconds
            return ScalingDecision(
                ScalingAction.SCALE_IN, active_instances - 1, "sustained low utilization"
            )
        return ScalingDecision(ScalingAction.HOLD, active_instances, "insufficient sustained evidence")

