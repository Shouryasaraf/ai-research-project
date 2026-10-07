import unittest
from dataclasses import replace

from vfw_research.controller import decide
from vfw_research.models import (
    BenefitTerms,
    DecisionInput,
    Forecast,
    GateAction,
    NodeCandidate,
    PlacementPolicy,
    PlacementWeights,
    SecuritySnapshot,
    ThresholdContext,
    ThresholdPolicy,
)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.forecast = Forecast(85, 80, 90, 60, "test-model")
        self.nodes = [NodeCandidate("target", 200, 20, 0.8, 0.8, 10, 100, 0.1)]
        self.placement = PlacementPolicy(0.6, 0.1, 0.1, 100, PlacementWeights(0.3, 0.15, 0.2, 0.25, 0.1))
        self.threshold = ThresholdPolicy(0.1, 0, 0, 0.1, 0.1, 0.1, 0.5, 0.1, 0.05, 2)
        self.security = SecuritySnapshot("p", "p", "p", True, True, True, True, True, 0, 0.01, True)
        self.input = DecisionInput(
            100,
            self.forecast,
            True,
            True,
            self.security,
            BenefitTerms(0.8, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05),
            ThresholdContext(1, 1, 0.1, 0, 0.5, False, 0.5),
        )

    def run_decision(self, value):
        return decide(value, self.nodes, self.placement, self.threshold, overload_trigger_fraction=0.8, max_commit_interval_width_fraction=0.2)

    def test_all_gates_pass_to_commit(self):
        decision = self.run_decision(self.input)
        self.assertEqual(decision.action, GateAction.COMMIT)
        self.assertEqual(decision.selected_node_id, "target")

    def test_invariant_failure_forces_fallback(self):
        bad_security = replace(self.security, target_policy_hash="bad")
        decision = self.run_decision(replace(self.input, invariants=bad_security))
        self.assertEqual(decision.action, GateAction.FALLBACK)
        self.assertIn("target_policy_mismatch", decision.invariant_violations)

    def test_wide_uncertainty_waits_if_warm_and_prewarms_if_cold(self):
        wide = Forecast(75, 30, 95, 60, "wide")
        decision = self.run_decision(replace(self.input, forecast=wide))
        self.assertEqual(decision.action, GateAction.WAIT)
        cold = self.run_decision(replace(self.input, forecast=wide, target_warm=False))
        self.assertEqual(cold.action, GateAction.PREWARM)

    def test_unsynchronized_target_requests_sync(self):
        decision = self.run_decision(replace(self.input, state_synchronized=False))
        self.assertEqual(decision.action, GateAction.SYNC)

    def test_low_benefit_waits(self):
        low = BenefitTerms(0.05, 0, 0, 0.1, 0.1, 0.1, 0.1)
        decision = self.run_decision(replace(self.input, benefit_terms=low))
        self.assertEqual(decision.action, GateAction.WAIT)


if __name__ == "__main__":
    unittest.main()
