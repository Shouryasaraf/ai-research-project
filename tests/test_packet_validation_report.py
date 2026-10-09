import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from vfw_research.packet_validation_report import build_report, verify_source


class PacketValidationReportTests(unittest.TestCase):
    def test_source_archive_must_match_recorded_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "executed-source.zip"
            with zipfile.ZipFile(path, "x") as archive:
                archive.writestr("src/example.py", "x=1\n")
            code = hashlib.sha256(b"src/example.pyx=1\n").hexdigest()
            record = {"executed_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "code_sha256": code}
            verify_source(root, record)
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                verify_source(root, {**record, "code_sha256": "incorrect"})
            with self.assertRaisesRegex(ValueError, "archive hash"):
                verify_source(root, {**record, "executed_source_sha256": "incorrect"})

    def test_incomplete_pair_is_rejected_before_capture_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial = root / "r0-ordinary"
            trial.mkdir()
            (trial / "record.json").write_text(json.dumps({"status": "completed"}))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                build_report(root, root / "out")
