import unittest

from vfw_research.state_sync import FlowKey, FlowRecord, synchronize_state, validate_state


class StateSyncTests(unittest.TestCase):
    def setUp(self):
        self.key = FlowKey("tcp", "10.0.0.2", 50000, "10.0.2.2", 5201)
        self.record = FlowRecord(self.key, "ESTABLISHED", "p1", 10, 8, 100.0)

    def test_sync_copies_eligible_state_and_matches_digest(self):
        target = {}
        report = synchronize_state({self.key: self.record}, target, expected_policy_hash="p1")
        self.assertTrue(report.consistent)
        self.assertEqual(report.transferred_count, 1)

    def test_wrong_policy_state_is_not_transferred(self):
        target = {}
        report = synchronize_state({self.key: self.record}, target, expected_policy_hash="p2")
        self.assertEqual(report.source_count, 0)
        self.assertFalse(target)

    def test_validation_detects_corrupt_target(self):
        corrupt = FlowRecord(self.key, "ESTABLISHED", "p1", 9, 8, 100.0)
        report = validate_state(
            {self.key: self.record}, {self.key: corrupt}, expected_policy_hash="p1"
        )
        self.assertFalse(report.consistent)
        self.assertEqual(report.mismatch_fraction, 1.0)


if __name__ == "__main__":
    unittest.main()

