import copy
import unittest

from vfw_research.finite_placement_audit import audit


def fixture():
    actions = ["WAIT", "COMMIT", "COMMIT", "WAIT", "COMMIT"]
    return {
        "evidence_class": "offline trace-driven controller decision pilot; no packet replay or migration",
        "split_counts": {"test": 5}, "sampling_interval_seconds": 1,
        "summary": [{"model": "m", "policy": "p", "action_counts": {"COMMIT": 3}}],
        "decisions": [
            {"model": "m", "policy": "p", "test_index": i,
             "action": action, "selected_node_id": "target" if action == "COMMIT" else None}
            for i, action in enumerate(actions)
        ],
    }


class FinitePlacementAuditTests(unittest.TestCase):
    def test_repeated_target_not_counted_as_distinct_move(self):
        row = audit(fixture())[0]
        self.assertEqual(row["raw_commit_recommendations"], 3)
        self.assertEqual(row["first_commit_index"], 1)
        self.assertEqual(row["later_same_target_recommendations"], 2)
        self.assertEqual(row["single_target_possible_distinct_moves_upper_bound"], 1)

    def test_no_commit_has_zero_bound(self):
        record = fixture()
        for row in record["decisions"]:
            row["action"] = "WAIT"
        record["summary"][0]["action_counts"]["COMMIT"] = 0
        row = audit(record)[0]
        self.assertIsNone(row["first_commit_index"])
        self.assertEqual(row["single_target_possible_distinct_moves_upper_bound"], 0)

    def test_invalid_commit_target_rejected(self):
        record = copy.deepcopy(fixture())
        record["decisions"][1]["selected_node_id"] = None
        with self.assertRaisesRegex(ValueError, "without selected target"):
            audit(record)

    def test_other_target_is_not_replayed(self):
        record = fixture()
        record["decisions"][4]["selected_node_id"] = "different"
        row = audit(record)[0]
        self.assertEqual(row["later_same_target_recommendations"], 1)
        self.assertEqual(row["later_other_target_recommendations_not_replayed"], 1)


if __name__ == "__main__":
    unittest.main()
