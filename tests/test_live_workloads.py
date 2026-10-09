import unittest
from vfw_research.workloads import live_demand_schedule

class LiveWorkloadTests(unittest.TestCase):
    def test_determinism_bounds_and_common_training(self):
        original = live_demand_schedule("step", 31, 12)
        for family in ("step", "steady", "bursts", "trend", "flash"):
            result = live_demand_schedule(family, 31, 12)
            self.assertEqual(result, live_demand_schedule(family, 31, 12))
            self.assertEqual(result[1:], original[1:])
            self.assertEqual(len(result[0]), 12)
            self.assertTrue(all(0 < value < 2 for value in result[0]))
        self.assertNotEqual(original[0], live_demand_schedule("steady", 31, 12)[0])

    def test_invalid_parameters(self):
        for family, seed, steps in [("unknown", 1, 12), ("step", -1, 12), ("step", 1, 2)]:
            with self.assertRaises(ValueError):
                live_demand_schedule(family, seed, steps)
