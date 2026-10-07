import unittest

from vfw_research.forecasting import (
    AdaptiveEwmaResidualForecaster,
    EwmaConformalForecaster,
    RollingMeanConformalForecaster,
    evaluate_one_step,
    time_ordered_split,
)
from vfw_research.forecast_evaluation import evaluate_family
from vfw_research.workloads import WorkloadFamily, generate_workload


class ForecastingTests(unittest.TestCase):
    def test_split_preserves_time_order(self):
        split = time_ordered_split(list(range(20)))
        self.assertEqual(split.train, tuple(range(12)))
        self.assertEqual(split.calibration, tuple(range(12, 16)))
        self.assertEqual(split.test, tuple(range(16, 20)))

    def test_interval_contains_point(self):
        model = RollingMeanConformalForecaster(window=3, alpha=0.2)
        model.fit((10, 10, 11, 10, 9), (10, 12, 11, 10, 9))
        forecast = model.predict(60)
        self.assertGreaterEqual(forecast.lower_mbps, 0)
        self.assertLessEqual(forecast.lower_mbps, forecast.point_mbps)
        self.assertGreaterEqual(forecast.upper_mbps, forecast.point_mbps)

    def test_accuracy_and_calibration_are_separate(self):
        model = RollingMeanConformalForecaster(window=3, alpha=0.2)
        model.fit((10, 10, 10, 10, 10), (9, 10, 11, 10, 10))
        metrics = evaluate_one_step(model, (10, 11, 9, 10), horizon_seconds=60)
        self.assertGreaterEqual(metrics.mae, 0)
        self.assertGreaterEqual(metrics.rmse, 0)
        self.assertTrue(0 <= metrics.interval_coverage <= 1)
        self.assertGreaterEqual(metrics.mean_interval_width, 0)

    def test_ewma_uses_chronological_calibration_and_observations(self):
        model = EwmaConformalForecaster(smoothing=0.5, alpha=0.1)
        model.fit((10, 10, 10), (10, 12, 10, 12, 10))
        before = model.predict(60)
        model.observe(30)
        after = model.predict(60)
        self.assertGreater(after.point_mbps, before.point_mbps)
        self.assertEqual(after.upper_mbps - after.point_mbps, before.upper_mbps - before.point_mbps)

    def test_adaptive_residual_radius_uses_observed_error_after_prediction(self):
        model = AdaptiveEwmaResidualForecaster(smoothing=0.5, alpha=0.1, residual_window=5)
        model.fit((10, 10, 10), (10, 10, 10, 10, 10))
        before = model.predict(1)
        self.assertEqual(before.upper_mbps, 10)
        model.observe(30)
        after = model.predict(1)
        self.assertGreater(after.upper_mbps - after.point_mbps, 0)
        self.assertEqual(before.model_version, after.model_version)

    def test_synthetic_trace_is_seeded_and_shift_is_held_out(self):
        first = generate_workload(WorkloadFamily.SHIFT, seed=5)
        second = generate_workload(WorkloadFamily.SHIFT, seed=5)
        self.assertEqual(first, second)
        split = time_ordered_split(list(first))
        self.assertGreater(sum(split.test) / len(split.test), sum(split.train) / len(split.train) + 30)

    def test_forecast_evaluation_records_held_out_calibration_metrics(self):
        result = evaluate_family(WorkloadFamily.PERIODIC, seed=9)
        self.assertEqual(result["split_counts"], {"train": 144, "calibration": 48, "test": 48})
        self.assertEqual(set(result["models"]), {
            "rolling_mean_conformal", "ewma_conformal", "adaptive_ewma_residual_exploratory"
        })
        for metrics in result["models"].values():
            self.assertTrue(0 <= metrics["interval_coverage"] <= 1)
            self.assertGreaterEqual(metrics["mae"], 0)
            self.assertGreaterEqual(metrics["absolute_coverage_error"], 0)


if __name__ == "__main__":
    unittest.main()
