import math
import unittest

from vfw_research.carbon import estimate_emissions_grams
from vfw_research.models import (
    BenefitTerms, Forecast, NodeCandidate, PlacementWeights, ThresholdPolicy,
)
from vfw_research.security_risk import RiskWeights


class NumericValidationTests(unittest.TestCase):
    def test_nonfinite_forecast_and_placement_weights_rejected(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            Forecast(math.nan, 0, 10, 60, "m")
        with self.assertRaises(ValueError):
            PlacementWeights(math.nan, 0.15, 0.2, 0.25, 0.1)

    def test_negative_carbon_or_latency_and_nonfinite_risk_weights_rejected(self):
        with self.assertRaisesRegex(ValueError, "carbon"):
            NodeCandidate("n", 100, 0, 0.5, 0.5, 1, -1, 0.2)
        with self.assertRaisesRegex(ValueError, "latency"):
            NodeCandidate("n", 100, 0, 0.5, 0.5, -1, 10, 0.2)
        with self.assertRaises(ValueError):
            RiskWeights(math.nan, 0.25, 0.25, 0.25, 0.25)

    def test_nonfinite_benefit_threshold_or_emissions_rejected(self):
        with self.assertRaisesRegex(ValueError, "benefit"):
            BenefitTerms(0, 0, 0, math.inf, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "threshold"):
            ThresholdPolicy(math.nan, 0, 0, 0, 0, 0, 0, 0, 0, 1)
        with self.assertRaisesRegex(ValueError, "carbon"):
            estimate_emissions_grams(
                average_power_watts=100, duration_seconds=60,
                intensity_gco2_per_kwh=math.inf,
            )
