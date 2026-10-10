import copy
import unittest

from vfw_research.decision_episode_analysis import summarize


def fixture():
    actions = ["WAIT", "COMMIT", "COMMIT", "WAIT", "COMMIT"]
    return {
        "evidence_class": "offline trace-driven controller decision pilot; no packet replay or migration",
        "split_counts": {"test": 5}, "sampling_interval_seconds": 2,
        "summary": [{"model": "m", "policy": "p", "action_counts": {"COMMIT": 3}}],
        "decisions": [{"model": "m", "policy": "p", "test_index": i, "action": action}
                      for i, action in enumerate(actions)],
    }


class DecisionEpisodeTests(unittest.TestCase):
    def test_counts_contiguous_runs_not_migrations(self):
        row = summarize(fixture())[0]
        self.assertEqual(row["commit_recommendations"], 3)
        self.assertEqual(row["contiguous_commit_episodes"], 2)
        self.assertEqual(row["episode_start_indices"], [1, 4])
        self.assertEqual(row["longest_commit_episode_seconds"], 4)

    def test_rejects_incomplete_and_inconsistent_records(self):
        record = fixture()
        record["decisions"].pop()
        with self.assertRaisesRegex(ValueError, "missing or duplicate"):
            summarize(record)
        record = copy.deepcopy(fixture())
        record["summary"][0]["action_counts"]["COMMIT"] = 2
        with self.assertRaisesRegex(ValueError, "disagrees"):
            summarize(record)


if __name__ == "__main__":
    unittest.main()
