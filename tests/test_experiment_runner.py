import json
import tempfile
import unittest
from pathlib import Path

from vfw_research.analysis import (
    build_paired_decision_contrasts,
    build_summary,
    read_records,
    write_summary,
)
from vfw_research.experiment_runner import run_experiment
from vfw_research.policies import PolicyVariant
from vfw_research.scenarios import load_scenario


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCENARIO = REPOSITORY_ROOT / "configs" / "scenarios" / "synthetic_small.json"


class ExperimentRunnerTests(unittest.TestCase):
    def test_scenario_builds_identical_input_for_same_seed(self):
        scenario = load_scenario(SCENARIO)
        first = scenario.build_run(7)
        second = scenario.build_run(7)
        self.assertEqual(first, second)
        self.assertEqual(scenario.seeds, (7, 11, 19))

    def test_scenario_rejects_unknown_seed(self):
        scenario = load_scenario(SCENARIO)
        with self.assertRaises(ValueError):
            scenario.build_run(999)

    def test_runner_writes_one_immutable_record_per_seed_and_policy(self):
        scenario = load_scenario(SCENARIO)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = run_experiment(scenario, output_root=root, batch_id="unit-batch")
            records = read_records(raw)
            self.assertEqual(len(records), len(scenario.seeds) * len(PolicyVariant))
            self.assertEqual({record["seed"] for record in records}, set(scenario.seeds))
            self.assertEqual(
                {record["policy_id"] for record in records},
                {variant.value for variant in PolicyVariant},
            )
            self.assertEqual(len({record["config_sha256"] for record in records}), 1)
            self.assertTrue(all(record["synthetic_inputs"] for record in records))
            self.assertTrue(all(record["decision"]["action"] for record in records))
            with self.assertRaises(FileExistsError):
                run_experiment(scenario, output_root=root, batch_id="unit-batch")

    def test_summary_is_generated_only_from_records(self):
        scenario = load_scenario(SCENARIO)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = run_experiment(scenario, output_root=root, batch_id="unit-summary")
            output = root / "processed" / "unit-summary"
            paths = write_summary(raw, output)
            self.assertTrue(all(path.exists() for path in paths))
            summary = json.loads(paths[0].read_text(encoding="utf-8"))
            self.assertEqual(summary["completed_records"], 27)
            self.assertEqual(len(summary["policies"]), len(PolicyVariant))
            self.assertIn("not a network benchmark", summary["evidence_class"])
            self.assertEqual(len(summary["paired_decision_contrasts"]), len(PolicyVariant) - 1)
            self.assertTrue(all(item["paired_runs"] == 3 for item in summary["paired_decision_contrasts"]))
            rebuilt = build_summary(read_records(raw))
            self.assertEqual(
                [item["policy_id"] for item in rebuilt["policies"]],
                [item["policy_id"] for item in summary["policies"]],
            )
            with self.assertRaises(FileExistsError):
                write_summary(raw, output)

    def test_paired_contrast_rejects_missing_or_duplicate_policy_seed(self):
        scenario = load_scenario(SCENARIO)
        with tempfile.TemporaryDirectory() as directory:
            records = read_records(run_experiment(scenario, output_root=Path(directory), batch_id="pairs"))
            with self.assertRaisesRegex(ValueError, "incomplete policy pair"):
                build_paired_decision_contrasts(records[1:])
            with self.assertRaisesRegex(ValueError, "duplicate paired record"):
                build_paired_decision_contrasts(records + [records[0]])


if __name__ == "__main__":
    unittest.main()
