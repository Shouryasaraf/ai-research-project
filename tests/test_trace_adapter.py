import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vfw_research.forecast_evaluation import evaluate_imported_trace
from vfw_research.trace_adapter import TraceKind, load_trace


class TraceAdapterTests(unittest.TestCase):
    def write_fixture(self, directory, *, kind="traffic", unit="Mbps", csv_text=None):
        content = csv_text or (
            "timestamp_utc,value\n"
            "2026-01-01T00:00:00Z,10.5\n"
            "2026-01-01T00:01:00Z,12.0\n"
        )
        csv_path = Path(directory) / "trace.csv"
        csv_path.write_text(content, encoding="utf-8")
        sidecar = Path(directory) / "trace.provenance.json"
        sidecar.write_text(json.dumps({
            "kind": kind, "unit": unit, "source": "https://example.org/trace",
            "license": "test-only fixture", "version": "v1",
            "retrieved_utc": "2026-01-02T00:00:00Z",
            "preprocessing": "none", "missing_data_policy": "reject",
            "sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            "sampling_interval_seconds": 60,
        }), encoding="utf-8")
        return csv_path, sidecar

    def test_valid_trace_preserves_explicit_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, sidecar = self.write_fixture(directory)
            result = load_trace(csv_path, sidecar)
            self.assertEqual(result.kind, TraceKind.TRAFFIC)
            self.assertEqual([point.value for point in result.points], [10.5, 12.0])
            self.assertEqual(result.license, "test-only fixture")

    def test_checksum_and_unit_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, sidecar = self.write_fixture(directory)
            csv_path.write_text("timestamp_utc,value\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "checksum"):
                load_trace(csv_path, sidecar)
            csv_path, sidecar = self.write_fixture(directory, kind="carbon", unit="Mbps")
            with self.assertRaisesRegex(ValueError, "unit"):
                load_trace(csv_path, sidecar)

    def test_non_utc_gap_and_risk_range_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            csv_path, sidecar = self.write_fixture(directory, csv_text=(
                "timestamp_utc,value\n2026-01-01T00:00:00Z,10\n"
                "2026-01-01T00:02:00Z,12\n"
            ))
            with self.assertRaisesRegex(ValueError, "irregular"):
                load_trace(csv_path, sidecar)
            csv_path, sidecar = self.write_fixture(directory, kind="risk", unit="score_0_1",
                csv_text="timestamp_utc,value\n2026-01-01T00:00:00Z,1.5\n")
            with self.assertRaisesRegex(ValueError, "out-of-range"):
                load_trace(csv_path, sidecar)
            csv_path, sidecar = self.write_fixture(directory,
                csv_text="timestamp_utc,value\n2026-01-01T00:00:00+01:00,10\n")
            with self.assertRaisesRegex(ValueError, "UTC"):
                load_trace(csv_path, sidecar)

    def test_imported_traffic_can_run_chronological_forecast_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            start = datetime(2026, 1, 1, tzinfo=timezone.utc)
            lines = ["timestamp_utc,value"] + [
                f"{(start + timedelta(minutes=index)).isoformat()}," + str(50 + index % 5)
                for index in range(60)
            ]
            csv_path, sidecar = self.write_fixture(directory, csv_text="\n".join(lines) + "\n")
            result = evaluate_imported_trace(load_trace(csv_path, sidecar))
            self.assertFalse(result["synthetic_inputs"])
            self.assertEqual(result["split_counts"], {"train": 36, "calibration": 12, "test": 12})
            self.assertIn("authenticity not independently verified", result["evidence_class"])
            self.assertEqual(result["source_provenance"]["csv_sha256"],
                             hashlib.sha256(csv_path.read_bytes()).hexdigest())
            self.assertIsNone(result["normalization_capacity_mbps"])
            self.assertIsNone(result["models"]["ewma_conformal"][
                "mean_interval_width_fraction_of_base_capacity"])
