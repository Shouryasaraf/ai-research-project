import unittest
from dataclasses import replace
from pathlib import Path

from vfw_research.liveness_guard import is_uncertainty_wait, run_liveness_guarded
from vfw_research.models import Forecast, GateAction
from vfw_research.policies import PolicyVariant, run_policy
from vfw_research.scenarios import load_scenario


SCENARIO = Path(__file__).resolve().parents[1] / "configs/scenarios/synthetic_small.json"


def uncertain_run():
    scenario = load_scenario(SCENARIO)
    run = scenario.build_run(scenario.seeds[0])
    inp = replace(run.decision_input,
                  forecast=Forecast(90, 70, 100, 1, "test-wide"),
                  state_synchronized=False)
    return replace(run, decision_input=inp)


class LivenessGuardTests(unittest.TestCase):
    def test_requires_both_streaks_then_sync_and_commit(self):
        run = uncertain_run()
        baseline = run_policy(PolicyVariant.FULL, run)
        self.assertTrue(is_uncertainty_wait(baseline))
        self.assertEqual(run_liveness_guarded(
            run, observed_overload_streak=2, uncertainty_wait_streak=3
        ).decision.action, GateAction.WAIT)
        self.assertEqual(run_liveness_guarded(
            run, observed_overload_streak=3, uncertainty_wait_streak=2
        ).decision.action, GateAction.WAIT)
        synced = run_liveness_guarded(
            run, observed_overload_streak=3, uncertainty_wait_streak=3,
            baseline=baseline,
        ).decision
        self.assertEqual(synced.action, GateAction.SYNC)
        self.assertEqual(synced.selected_node_id, baseline.decision.selected_node_id)
        ready = replace(run, decision_input=replace(run.decision_input,
                                                    state_synchronized=True))
        self.assertEqual(run_liveness_guarded(
            ready, observed_overload_streak=4, uncertainty_wait_streak=4
        ).decision.action, GateAction.COMMIT)

    def test_never_overrides_security_or_benefit_gate(self):
        run = uncertain_run()
        bad = replace(run, decision_input=replace(
            run.decision_input,
            invariants=replace(run.decision_input.invariants, target_policy_hash="wrong"),
        ))
        self.assertEqual(run_liveness_guarded(
            bad, observed_overload_streak=10, uncertainty_wait_streak=10
        ).decision.action, GateAction.FALLBACK)
        expensive = replace(run, decision_input=replace(
            run.decision_input,
            benefit_terms=replace(run.decision_input.benefit_terms,
                                  migration_cost=10.0),
        ))
        self.assertEqual(run_liveness_guarded(
            expensive, observed_overload_streak=10, uncertainty_wait_streak=10
        ).decision.action, GateAction.WAIT)
        stale = replace(run, decision_input=replace(run.decision_input, telemetry_fresh=False))
        self.assertEqual(run_liveness_guarded(
            stale, observed_overload_streak=10, uncertainty_wait_streak=10
        ).decision.action, GateAction.FALLBACK)

    def test_rejects_invalid_streaks_and_unrelated_baseline(self):
        run = uncertain_run()
        with self.assertRaisesRegex(ValueError, "streak"):
            run_liveness_guarded(run, observed_overload_streak=-1,
                                 uncertainty_wait_streak=3)
        with self.assertRaisesRegex(ValueError, "full controller"):
            run_liveness_guarded(
                run, observed_overload_streak=3, uncertainty_wait_streak=3,
                baseline=run_policy(PolicyVariant.REACTIVE, run),
            )


if __name__ == "__main__":
    unittest.main()
