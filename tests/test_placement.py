import unittest

from vfw_research.models import Forecast, NodeCandidate, PlacementPolicy, PlacementWeights
from vfw_research.placement import evaluate_placement


class PlacementTests(unittest.TestCase):
    def setUp(self):
        self.forecast = Forecast(50, 45, 60, 60, "test-v1")
        self.policy = PlacementPolicy(0.6, 0.1, 0.1, 100, PlacementWeights(0.3, 0.15, 0.2, 0.25, 0.1))

    def test_risky_node_is_rejected_even_if_green_and_large(self):
        nodes = [
            NodeCandidate("safe", 150, 10, 0.8, 0.8, 20, 300, 0.2),
            NodeCandidate("risky", 500, 0, 1, 1, 1, 1, 0.95),
        ]
        result = evaluate_placement(nodes, self.forecast, self.policy)
        self.assertEqual(result.ranked[0].node_id, "safe")
        self.assertEqual(result.rejected[0].reasons, ("security_risk_above_limit",))

    def test_upper_forecast_bound_drives_capacity_constraint(self):
        node = NodeCandidate("tight", 100, 45, 0.8, 0.8, 10, 100, 0.1)
        result = evaluate_placement([node], self.forecast, self.policy)
        self.assertFalse(result.ranked)
        self.assertIn("insufficient_uncertainty_headroom", result.rejected[0].reasons)


if __name__ == "__main__":
    unittest.main()

