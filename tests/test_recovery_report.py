import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from vfw_research.recovery_report import build_report, verify_capture

class RecoveryReportTests(unittest.TestCase):
    def test_failed_and_unexecuted_attempts_remain_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch = root / "batch"
            trial = batch / "r0-controller_exit"
            trial.mkdir(parents=True)
            (trial / "record.json").write_text(json.dumps({"status": "failed", "fault": "controller_exit",
                                                          "code_sha256": "test", "error": "setup failure"}))
            result = build_report([batch], root / "out")
            self.assertEqual(result["attempts"][0]["failed"], 1)
            self.assertEqual(result["attempts"][0]["not_executed"], 5)
            self.assertIn("setup failure", json.dumps(result))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                build_report([batch, batch], root / "duplicate")
            (trial / "record.json").write_text(json.dumps({"status": "completed", "code_sha256": "test"}))
            with self.assertRaisesRegex(ValueError, "raw outcome"):
                build_report([batch], root / "missing")

    def test_tampered_capture_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "client.pcap").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "checksum"):
                verify_capture(root, {"capture_sha256": {"client": hashlib.sha256(b"original").hexdigest()}})
