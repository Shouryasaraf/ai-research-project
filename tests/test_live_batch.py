import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("live_batch_test", Path(__file__).resolve().parents[1] / "scripts/live_experiment_batch.py")
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

class ResumeTests(unittest.TestCase):
    def test_resume_requires_matching_completed_clean_record(self):
        record = {"status": "completed", "leftover_namespaces": [], "policy": "policy", "seed": 1, "code_sha256": "digest"}
        self.assertTrue(batch.resumable(record, "policy", 1, "digest"))
        for key, value in {"status": "running", "leftover_namespaces": ["vfwlab3-source"],
                           "policy": "wrong", "seed": 2, "code_sha256": "other"}.items():
            with self.subTest(key=key):
                self.assertFalse(batch.resumable({**record, key: value}, "policy", 1, "digest"))
