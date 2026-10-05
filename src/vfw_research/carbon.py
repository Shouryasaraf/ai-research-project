"""Carbon trace replay and explicitly modeled emissions estimates."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CarbonObservation:
    timestamp_seconds: int
    node_id: str
    intensity_gco2_per_kwh: float
    provenance: str
    synthetic: bool


def estimate_emissions_grams(
    *, average_power_watts: float, duration_seconds: float, intensity_gco2_per_kwh: float
) -> float:
    if min(average_power_watts, duration_seconds, intensity_gco2_per_kwh) < 0:
        raise ValueError("carbon estimate inputs cannot be negative")
    return (average_power_watts / 1000) * (duration_seconds / 3600) * intensity_gco2_per_kwh


class CarbonTrace:
    def __init__(self, observations: list[CarbonObservation]) -> None:
        if not observations:
            raise ValueError("carbon trace requires observations")
        self._by_node: dict[str, list[CarbonObservation]] = {}
        for observation in observations:
            if observation.intensity_gco2_per_kwh < 0:
                raise ValueError("carbon intensity cannot be negative")
            self._by_node.setdefault(observation.node_id, []).append(observation)
        for values in self._by_node.values():
            values.sort(key=lambda item: item.timestamp_seconds)

    def at(self, node_id: str, timestamp_seconds: int) -> CarbonObservation:
        values = self._by_node.get(node_id)
        if not values:
            raise KeyError(f"no carbon trace for node {node_id}")
        eligible = [value for value in values if value.timestamp_seconds <= timestamp_seconds]
        if not eligible:
            raise LookupError("no carbon observation exists at or before requested time")
        return eligible[-1]

