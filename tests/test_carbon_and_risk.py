import unittest

from vfw_research.carbon import CarbonObservation, CarbonTrace, estimate_emissions_grams
from vfw_research.security_risk import RiskInputs, RiskWeights, calculate_risk


class CarbonAndRiskTests(unittest.TestCase):
    def test_emissions_units(self):
        grams = estimate_emissions_grams(
            average_power_watts=1000, duration_seconds=3600, intensity_gco2_per_kwh=400
        )
        self.assertEqual(grams, 400)

    def test_trace_replays_latest_past_value(self):
        trace = CarbonTrace(
            [
                CarbonObservation(0, "n1", 400, "synthetic fixture", True),
                CarbonObservation(60, "n1", 200, "synthetic fixture", True),
            ]
        )
        self.assertEqual(trace.at("n1", 59).intensity_gco2_per_kwh, 400)
        self.assertEqual(trace.at("n1", 60).intensity_gco2_per_kwh, 200)

    def test_risk_score_exposes_contributions(self):
        score = calculate_risk(
            RiskInputs(1, 0.5, 0, 0.25, 0.5),
            RiskWeights(0.3, 0.2, 0.2, 0.2, 0.1),
        )
        self.assertAlmostEqual(score.total, 0.5)
        self.assertAlmostEqual(sum(score.contributions.values()), score.total)


if __name__ == "__main__":
    unittest.main()

