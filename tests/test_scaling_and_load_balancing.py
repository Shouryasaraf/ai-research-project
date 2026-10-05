import unittest

from vfw_research.load_balancing import (
    FirewallInstance,
    FlowDirector,
    NoEligibleFirewall,
)
from vfw_research.scaling import ScalingAction, ScalingManager, ScalingPolicy


class ScalingTests(unittest.TestCase):
    def setUp(self):
        self.manager = ScalingManager(ScalingPolicy(1, 4, 0.8, 0.3, 3, 3, 30))

    def test_scale_out_requires_sustained_evidence(self):
        self.assertEqual(self.manager.observe(0.9, 1, 0).action, ScalingAction.HOLD)
        self.assertEqual(self.manager.observe(0.9, 1, 1).action, ScalingAction.HOLD)
        decision = self.manager.observe(0.9, 1, 2)
        self.assertEqual(decision.action, ScalingAction.SCALE_OUT)
        self.assertEqual(decision.desired_instances, 2)

    def test_cooldown_prevents_immediate_reversal(self):
        for time in (0, 1, 2):
            decision = self.manager.observe(0.9, 2, time)
        self.assertEqual(decision.action, ScalingAction.SCALE_OUT)
        self.assertEqual(self.manager.observe(0.1, 3, 3).reason, "cooldown active")

    def test_hysteresis_clears_transient_counts(self):
        self.manager.observe(0.9, 2, 0)
        self.manager.observe(0.5, 2, 1)
        self.manager.observe(0.9, 2, 2)
        self.manager.observe(0.9, 2, 3)
        self.assertEqual(self.manager.observe(0.5, 2, 4).action, ScalingAction.HOLD)


class FlowDirectorTests(unittest.TestCase):
    def test_new_flow_selects_least_utilized_instance(self):
        director = FlowDirector()
        instances = [
            FirewallInstance("a", 80, 100),
            FirewallInstance("b", 10, 100),
        ]
        assignment = director.assign("flow-1", instances)
        self.assertEqual(assignment.instance_id, "b")
        self.assertFalse(assignment.reused_pin)

    def test_existing_flow_remains_pinned_during_drain(self):
        director = FlowDirector()
        director.assign("flow-1", [FirewallInstance("a", 1, 100)])
        assignment = director.assign(
            "flow-1", [FirewallInstance("a", 1, 100, accepting_new_flows=False)]
        )
        self.assertEqual(assignment.instance_id, "a")
        self.assertTrue(assignment.reused_pin)

    def test_failed_pinned_instance_requires_explicit_recovery(self):
        director = FlowDirector()
        director.assign("flow-1", [FirewallInstance("a", 1, 100)])
        with self.assertRaises(NoEligibleFirewall):
            director.assign("flow-1", [FirewallInstance("a", 1, 100, healthy=False)])


if __name__ == "__main__":
    unittest.main()

