import json
import tempfile
import unittest
from pathlib import Path

from vfw_research.experiment_records import (
    ExperimentRecord,
    RunStatus,
    configuration_digest,
    write_immutable_record,
)


class ExperimentRecordTests(unittest.TestCase):
    def build_record(self):
        return ExperimentRecord(
            run_id="run-001",
            scenario_id="synthetic-smoke",
            policy_id="full_proposed_controller",
            seed=7,
            synthetic_inputs=True,
            status=RunStatus.COMPLETED,
            started_utc="2026-10-06T00:00:00Z",
            finished_utc="2026-10-06T00:00:01Z",
            config_sha256=configuration_digest({"seed": 7}),
            environment={"kind": "unit-test"},
            measured_metrics={"decision_seconds": 0.001},
            modeled_metrics={"carbon_grams": 0.1},
            notes=("not a publication result",),
        )

    def test_record_separates_measured_and_modeled_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            path = write_immutable_record(Path(directory), self.build_record())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("measured_metrics", payload)
            self.assertIn("modeled_metrics", payload)
            self.assertTrue(payload["synthetic_inputs"])

    def test_record_cannot_be_silently_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_immutable_record(output, self.build_record())
            with self.assertRaises(FileExistsError):
                write_immutable_record(output, self.build_record())


if __name__ == "__main__":
    unittest.main()

