import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vfw_research.policies import PolicyVariant
from vfw_research.scenarios import load_scenario
from vfw_research.trace_adapter import ImportedTrace, TraceKind, TracePoint
from vfw_research.trace_decision_eval import evaluate_trace_decisions


SCENARIO = Path(__file__).resolve().parents[1] / "configs/scenarios/synthetic_small.json"


def trace(values):
    start = datetime(2000, 1, 1, tzinfo=timezone.utc)
    return ImportedTrace(
        TraceKind.TRAFFIC, "Mbps", "https://example.org/test", "test-only", "v1",
        start, "none", "reject", "test-sha", 1,
        tuple(TracePoint(start + timedelta(seconds=index), value)
              for index, value in enumerate(values)),
    )


class TraceDecisionEvaluationTests(unittest.TestCase):
    def test_paired_one_step_decisions_are_trace_driven_and_causal(self):
        scenario = load_scenario(SCENARIO)
        values = [10.0 + index % 5 for index in range(40)]
        first = evaluate_trace_decisions(trace(values), scenario)
        self.assertIn("no packet replay", first["evidence_class"])
        self.assertEqual(first["split_counts"], {"train": 24, "calibration": 8, "test": 8})
        self.assertEqual(len(first["decisions"]), 8 * 3 * len(PolicyVariant))
        self.assertEqual(first["assumed_source_capacity_mbps"], 14.0)
        self.assertEqual(len(first["summary"]), 3 * len(PolicyVariant))
        self.assertTrue(all(row["prior_observed_mbps"] == values[31]
                            for row in first["decisions"] if row["test_index"] == 0))
        changed = evaluate_trace_decisions(trace(values[:-1] + [99.0]), scenario)
        self.assertEqual(
            [(row["action"], row["forecast_point_mbps"]) for row in first["decisions"]],
            [(row["action"], row["forecast_point_mbps"]) for row in changed["decisions"]],
        )
        self.assertNotEqual(first["decisions"][-1]["actual_next_mbps"],
                            changed["decisions"][-1]["actual_next_mbps"])

    def test_rejects_nontraffic_and_zero_training_capacity(self):
        scenario = load_scenario(SCENARIO)
        with self.assertRaisesRegex(ValueError, "traffic trace"):
            evaluate_trace_decisions(replace(trace([1.0] * 40), kind=TraceKind.CARBON), scenario)
        with self.assertRaisesRegex(ValueError, "positive"):
            evaluate_trace_decisions(trace([0.0] * 40), scenario)
        unready_payload = {**scenario.payload, "target_warm": False}
        with self.assertRaisesRegex(ValueError, "ready"):
            evaluate_trace_decisions(trace([1.0] * 40), replace(scenario, payload=unready_payload))


if __name__ == "__main__":
    unittest.main()
