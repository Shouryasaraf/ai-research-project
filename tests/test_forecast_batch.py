import json
import tempfile
import unittest
from pathlib import Path

from vfw_research.forecast_batch import run_batch, summarize_forecasts
from vfw_research.forecast_evaluation import evaluate_family
from vfw_research.workloads import WorkloadFamily


class ForecastBatchTests(unittest.TestCase):
    def test_batch_writes_all_seeded_family_records_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "forecast-pilot"
            summary_path = run_batch(output, seeds=[3, 5], length=60)
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(summary["record_count"], 2 * len(WorkloadFamily))
            self.assertEqual(len(summary["families"]), len(WorkloadFamily))
            self.assertEqual(len(list(output.glob("*.json"))), 1 + 2 * len(WorkloadFamily))
            self.assertTrue(all(item["seeds"] == [3, 5] for item in summary["families"]))
            with self.assertRaises(FileExistsError):
                run_batch(output, seeds=[3, 5], length=60)

    def test_duplicate_seed_and_mixed_evidence_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run_batch(Path(directory) / "invalid", seeds=[2, 2], length=60)
        record = evaluate_family(WorkloadFamily.STEADY, seed=2, length=60)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize_forecasts([record, record])
        invalid = {**record, "evidence_class": "network benchmark", "seed": 3}
        with self.assertRaisesRegex(ValueError, "mixed evidence"):
            summarize_forecasts([record, invalid])
