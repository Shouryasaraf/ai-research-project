import unittest

from vfw_research.forecasting import (
    RollingMeanConformalForecaster,
    evaluate_one_step,
    time_ordered_split,
)


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


if __name__ == "__main__":
    unittest.main()

