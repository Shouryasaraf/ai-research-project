import unittest

from vfw_research.models import ControllerDecision, GateAction
from vfw_research.timing_ablation import scheduled_reactive_decision


class TimingAblationTests(unittest.TestCase):
    def decision(self, action=GateAction.COMMIT, target="target"):
        return ControllerDecision(action, "reactive", target, 1.0, 0.0, (), {}, "test")

    def test_fixed_schedule_requires_trigger_and_sync(self):
        baseline = self.decision()
        self.assertEqual(scheduled_reactive_decision(baseline, step=0, triggered=True, synced=False).action, GateAction.WAIT)
        self.assertEqual(scheduled_reactive_decision(baseline, step=2, triggered=False, synced=False).action, GateAction.WAIT)
        self.assertEqual(scheduled_reactive_decision(baseline, step=2, triggered=True, synced=False).action, GateAction.SYNC)
        self.assertEqual(scheduled_reactive_decision(baseline, step=3, triggered=True, synced=False).action, GateAction.WAIT)
        self.assertEqual(scheduled_reactive_decision(baseline, step=3, triggered=True, synced=True).action, GateAction.COMMIT)

    def test_fallback_and_no_candidate_not_overridden(self):
        self.assertEqual(scheduled_reactive_decision(self.decision(GateAction.FALLBACK), step=3,
                         triggered=True, synced=True).action, GateAction.FALLBACK)
        self.assertEqual(scheduled_reactive_decision(self.decision(GateAction.WAIT, None), step=3,
                         triggered=True, synced=True).action, GateAction.WAIT)


if __name__ == "__main__":
    unittest.main()
