import unittest
from dataclasses import replace

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
from vfw_research.policies import PolicyRunInput, PolicyVariant, run_all_policies, run_policy


class PolicyInterfaceTests(unittest.TestCase):
    def build_run(self):
        forecast = Forecast(90, 85, 95, 60, "fixture")
        return PolicyRunInput(
            current_utilization=0.85,
            decision_input=DecisionInput(
                100,
                forecast,
                True,
                True,
                SecuritySnapshot("p", "p", "p", True, True, True, True, True, 0, 0.01, True),
                BenefitTerms(0.8, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05),
                ThresholdContext(1, 1, 0.1, 0, 0.5, False, 0.5),
            ),
            candidates=[NodeCandidate("target", 200, 10, 0.8, 0.8, 10, 100, 0.1)],
            placement_policy=PlacementPolicy(
                0.6, 0.1, 0.1, 100, PlacementWeights(0.3, 0.15, 0.2, 0.25, 0.1)
            ),
            threshold_policy=ThresholdPolicy(0.1, 0, 0, 0.1, 0.1, 0.1, 0.5, 0.1, 0.05, 2),
            overload_trigger_fraction=0.8,
            max_commit_interval_width_fraction=0.2,
        )

    def test_all_declared_variants_use_common_interface(self):
        outcomes = run_all_policies(self.build_run())
        self.assertEqual({outcome.variant for outcome in outcomes}, set(PolicyVariant))
        self.assertEqual(len(outcomes), 9)

    def test_static_waits_and_full_controller_commits_fixture(self):
        outcomes = {outcome.variant: outcome for outcome in run_all_policies(self.build_run())}
        self.assertEqual(outcomes[PolicyVariant.STATIC].decision.action, GateAction.WAIT)
        self.assertEqual(outcomes[PolicyVariant.FULL].decision.action, GateAction.COMMIT)
        self.assertEqual(outcomes[PolicyVariant.COLD_MIGRATION].migration_mode, "cold")

    def test_ablation_removes_corresponding_benefit_credit(self):
        run = self.build_run()
        full = run_policy(PolicyVariant.FULL, run).decision.net_benefit
        carbon = run_policy(PolicyVariant.CARBON_UNAWARE, run).decision.net_benefit
        risk = run_policy(PolicyVariant.RISK_UNAWARE, run).decision.net_benefit
        neither = run_policy(PolicyVariant.UNCERTAINTY_NO_CARBON_RISK, run).decision.net_benefit
        self.assertAlmostEqual(full - carbon, 0.1)
        self.assertAlmostEqual(full - risk, 0.1)
        self.assertAlmostEqual(full - neither, 0.2)

    def test_reactive_candidate_check_uses_only_observed_demand(self):
        run = self.build_run()
        wide = replace(run.decision_input, forecast=Forecast(90, 0, 999, 60, "wide"))
        result = run_policy(PolicyVariant.REACTIVE, replace(run, decision_input=wide))
        self.assertEqual(result.decision.action, GateAction.COMMIT)


if __name__ == "__main__":
    unittest.main()
