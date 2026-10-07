"""Transparent rolling-mean forecasting with split-conformal intervals."""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import fmean

from .models import Forecast


@dataclass(frozen=True)
class TimeSplit:
    train: tuple[float, ...]
    calibration: tuple[float, ...]
    test: tuple[float, ...]


def time_ordered_split(
    values: list[float], train_fraction: float = 0.6, calibration_fraction: float = 0.2
) -> TimeSplit:
    if len(values) < 10:
        raise ValueError("at least ten time-ordered observations are required")
    if not 0 < train_fraction < 1 or not 0 < calibration_fraction < 1:
        raise ValueError("split fractions must be between 0 and 1")
    if train_fraction + calibration_fraction >= 1:
        raise ValueError("splits must leave a test segment")
    train_end = int(len(values) * train_fraction)
    calibration_end = train_end + int(len(values) * calibration_fraction)
    return TimeSplit(
        tuple(values[:train_end]),
        tuple(values[train_end:calibration_end]),
        tuple(values[calibration_end:]),
    )


def _higher_quantile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("quantile requires observations")
    rank = max(1, math.ceil(probability * len(ordered)))
    return ordered[min(rank - 1, len(ordered) - 1)]


class RollingMeanConformalForecaster:
    def __init__(self, window: int = 5, alpha: float = 0.1) -> None:
        if window < 1 or not 0 < alpha < 1:
            raise ValueError("invalid window or alpha")
        self.window = window
        self.alpha = alpha
        self._history: list[float] = []
        self._radius: float | None = None

    def fit(self, train: tuple[float, ...], calibration: tuple[float, ...]) -> None:
        if len(train) < self.window or not calibration:
            raise ValueError("training window and calibration data are required")
        if any(value < 0 for value in (*train, *calibration)):
            raise ValueError("traffic observations must be non-negative")
        history = list(train)
        residuals: list[float] = []
        for actual in calibration:
            residuals.append(abs(actual - fmean(history[-self.window :])))
            history.append(actual)
        probability = min(
            1.0, math.ceil((len(residuals) + 1) * (1 - self.alpha)) / len(residuals)
        )
        self._radius = _higher_quantile(residuals, probability)
        self._history = history

    def predict(self, horizon_seconds: int) -> Forecast:
        if self._radius is None:
            raise RuntimeError("fit the forecaster before prediction")
        point = fmean(self._history[-self.window :])
        return Forecast(
            point,
            max(0.0, point - self._radius),
            point + self._radius,
            horizon_seconds,
            f"rolling-mean-conformal-w{self.window}-a{self.alpha:g}",
        )

    def observe(self, actual_mbps: float) -> None:
        if actual_mbps < 0:
            raise ValueError("traffic observation must be non-negative")
        self._history.append(actual_mbps)


class EwmaConformalForecaster:
    """Exponentially weighted one-step point forecast with split-conformal radius."""

    def __init__(self, smoothing: float = 0.4, alpha: float = 0.1) -> None:
        if not 0 < smoothing <= 1 or not 0 < alpha < 1:
            raise ValueError("smoothing and alpha must be in (0, 1]")
        self.smoothing = smoothing
        self.alpha = alpha
        self._level: float | None = None
        self._radius: float | None = None

    def _update(self, actual_mbps: float) -> None:
        if not math.isfinite(actual_mbps) or actual_mbps < 0:
            raise ValueError("traffic observation must be finite and non-negative")
        self._level = (
            actual_mbps
            if self._level is None
            else self.smoothing * actual_mbps + (1 - self.smoothing) * self._level
        )

    def fit(self, train: tuple[float, ...], calibration: tuple[float, ...]) -> None:
        if not train or not calibration:
            raise ValueError("training and calibration data are required")
        self._level = None
        self._radius = None
        for actual in train:
            self._update(actual)
        residuals = []
        for actual in calibration:
            assert self._level is not None
            residuals.append(abs(actual - self._level))
            self._update(actual)
        probability = min(
            1.0, math.ceil((len(residuals) + 1) * (1 - self.alpha)) / len(residuals)
        )
        self._radius = _higher_quantile(residuals, probability)

    def predict(self, horizon_seconds: int) -> Forecast:
        if self._level is None or self._radius is None:
            raise RuntimeError("fit the forecaster before prediction")
        return Forecast(
            self._level,
            max(0.0, self._level - self._radius),
            self._level + self._radius,
            horizon_seconds,
            f"ewma-conformal-s{self.smoothing:g}-a{self.alpha:g}",
        )

    def observe(self, actual_mbps: float) -> None:
        self._update(actual_mbps)


@dataclass(frozen=True)
class ForecastMetrics:
    mae: float
    rmse: float
    interval_coverage: float
    mean_interval_width: float


def evaluate_one_step(
    model: RollingMeanConformalForecaster,
    test: tuple[float, ...],
    *,
    horizon_seconds: int,
) -> ForecastMetrics:
    if not test:
        raise ValueError("test segment is required")
    absolute: list[float] = []
    squared: list[float] = []
    widths: list[float] = []
    covered = 0
    for actual in test:
        forecast = model.predict(horizon_seconds)
        error = actual - forecast.point_mbps
        absolute.append(abs(error))
        squared.append(error * error)
        widths.append(forecast.upper_mbps - forecast.lower_mbps)
        covered += int(forecast.lower_mbps <= actual <= forecast.upper_mbps)
        model.observe(actual)
    return ForecastMetrics(
        fmean(absolute),
        math.sqrt(fmean(squared)),
        covered / len(test),
        fmean(widths),
    )
