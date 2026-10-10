import copy
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vfw_research.policies import PolicyVariant
from vfw_research.scenarios import load_scenario
from vfw_research.sequential_replay import EVIDENCE_CLASS, replay
from vfw_research.trace_adapter import ImportedTrace, TraceKind, TracePoint
from vfw_research.trace_decision_eval import evaluate_trace_decisions


SCENARIO = Path(__file__).resolve().parents[1] / "configs/scenarios/synthetic_small.json"


def sample_record(values=None):
    values = values or [10.0 + index % 5 for index in range(40)]
    start = datetime(2000, 1, 1, tzinfo=timezone.utc)
    trace = ImportedTrace(
        TraceKind.TRAFFIC, "Mbps", "https://example.org/test", "test-only", "v1",
        start, "none", "reject", "test-sha", 1,
        tuple(TracePoint(start + timedelta(seconds=index), value)
              for index, value in enumerate(values)),
    )
    scenario = load_scenario(SCENARIO)
    return evaluate_trace_decisions(trace, scenario), scenario


class SequentialReplayTests(unittest.TestCase):
    def test_stateful_replay_does_not_count_repeated_commit_recommendations(self):
        record, scenario = sample_record()
        result = replay(record, scenario)
        self.assertEqual(result["evidence_class"], EVIDENCE_CLASS)
        self.assertEqual(len(result["steps"]), 8 * 3 * len(PolicyVariant))
        for summary in result["summary"]:
            rows = [row for row in result["steps"]
                    if (row["model"], row["policy"]) == (summary["model"], summary["policy"])]
            self.assertEqual(summary["simulated_migrations"],
                             sum(row["action"] == "COMMIT" for row in rows))
            self.assertLessEqual(summary["simulated_migrations"], 2)
            self.assertGreaterEqual(summary["modeled_action_cost_utility"], 0)
        static = [summary for summary in result["summary"]
                  if summary["policy"] == PolicyVariant.STATIC.value]
        self.assertTrue(all(row["simulated_migrations"] == 0 for row in static))

    def test_future_observation_does_not_change_prior_actions(self):
        values = [10.0 + index % 5 for index in range(40)]
        record, scenario = sample_record(values)
        changed, _ = sample_record(values[:-1] + [99.0])
        before = replay(record, scenario)["steps"]
        after = replay(changed, scenario)["steps"]
        self.assertEqual([(row["action"], row["source_after"]) for row in before
                          if row["test_index"] < 7],
                         [(row["action"], row["source_after"]) for row in after
                          if row["test_index"] < 7])

    def test_rejects_tampered_or_unpaired_input(self):
        record, scenario = sample_record()
        wrong = copy.deepcopy(record)
        wrong["scenario_config_sha256"] = "bad"
        with self.assertRaisesRegex(ValueError, "digest"):
            replay(wrong, scenario)
        wrong = copy.deepcopy(record)
        wrong["decisions"][0]["actual_next_mbps"] = 99.0
        with self.assertRaisesRegex(ValueError, "disagree"):
            replay(wrong, scenario)
        with self.assertRaisesRegex(ValueError, "cooldown"):
            replay(record, scenario, cooldown_slots=-1)

    def test_cooldown_prevents_same_target_and_immediate_repeat(self):
        _, original = sample_record()
        payload = copy.deepcopy(original.payload)
        payload["candidates"] = payload["candidates"][:2]
        for index, node in enumerate(payload["candidates"]):
            node["capacity_mbps"] = 16.0 + index
            node["current_load_mbps"] = 0.0
        scenario = replace(original, payload=payload)
        start = datetime(2000, 1, 1, tzinfo=timezone.utc)
        trace = ImportedTrace(
            TraceKind.TRAFFIC, "Mbps", "https://example.org/test", "test-only", "v1",
            start, "none", "reject", "constant-sha", 1,
            tuple(TracePoint(start + timedelta(seconds=index), 14.0)
                  for index in range(50)),
        )
        record = evaluate_trace_decisions(trace, scenario)
        result = replay(record, scenario, cooldown_slots=2)
        reactive = [row for row in result["steps"]
                    if row["model"] == "ewma_conformal"
                    and row["policy"] == PolicyVariant.REACTIVE.value]
        commits = [row for row in reactive if row["action"] == "COMMIT"]
        self.assertGreaterEqual(len(commits), 2)
        self.assertTrue(all(row["source_before"] != row["source_after"] for row in commits))
        self.assertTrue(all(later["test_index"] - earlier["test_index"] >= 3
                            for earlier, later in zip(commits, commits[1:])))
        self.assertTrue(any(row["cooldown_remaining_before"] > 0 for row in reactive))


if __name__ == "__main__":
    unittest.main()
