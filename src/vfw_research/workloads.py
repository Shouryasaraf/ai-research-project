"""Reproducible synthetic traffic-rate traces for forecast pipeline tests."""

from __future__ import annotations

import math
import random
from enum import Enum


class WorkloadFamily(str, Enum):
    STEADY = "steady"
    PERIODIC = "periodic_bursts"
    TREND = "gradual_trend"
    FLASH = "flash_crowd"
    SHIFT = "held_out_shift"


def generate_workload(
    family: WorkloadFamily,
    *,
    seed: int,
    length: int = 240,
    base_mbps: float = 60.0,
) -> tuple[float, ...]:
    if not isinstance(family, WorkloadFamily):
        raise ValueError("workload family must be a declared WorkloadFamily")
    if seed < 0 or length < 30 or not math.isfinite(base_mbps) or base_mbps <= 0:
        raise ValueError("seed, length or base traffic rate is invalid")
    generator = random.Random(seed)
    values: list[float] = []
    for index in range(length):
        value = base_mbps + generator.gauss(0, 2.0)
        if family is WorkloadFamily.PERIODIC and index % 40 in range(8, 16):
            value += 35.0
        elif family is WorkloadFamily.TREND:
            value += 0.12 * index
        elif family is WorkloadFamily.FLASH and length // 2 <= index < length // 2 + 12:
            value += 70.0
        elif family is WorkloadFamily.SHIFT and index >= int(0.8 * length):
            value += 40.0
        values.append(max(0.0, value))
    return tuple(values)
