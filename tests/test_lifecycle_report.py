import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from vfw_research.lifecycle_report import build_report, verify_record


class LifecycleReportTests(unittest.TestCase):
    def setUp(self):
        self.record = {"status": "completed", "code_sha256": "test", "leftover_namespaces": "",
                       "active_paths": [1, 2, 1], "modeled": {"mbps_per_active_flow": 1},
                       "balanced_flow_counts": {"source": 2, "target": 1},
                       "original_flow_pins_preserved": True, "new_target_flow_verified": True,
                       "drain_before_scale_in": True, "post_scale_in_service": True,
                       "events": [
                           {"actuation": "target_firewall_and_backend_started", "decision": {"action": "PREWARM"}, "scaling_action": "SCALE_OUT"},
                           {"actuation": "source_pin_checkpoint_validated_no_conntrack_transfer", "decision": {"action": "SYNC"}, "live_guard": self.guard()},
                           {"actuation": "balanced_new_flow_admission", "decision": {"action": "COMMIT"}, "live_guard": self.guard()}]}

    @staticmethod
    def guard():
        return {"allowed": True, "source_flow_pinned_at_decision": True,
                "conntrack_transfer_claimed": False,
                "source_policy_digest": "same", "target_policy_digest": "same"}

    def test_rejects_unverified_actuation(self):
        verify_record(self.record)
        for key, value in (("scaling_action", "HOLD"), ("actuation", "not_warmed")):
            altered = copy.deepcopy(self.record)
            altered["events"][0][key] = value
            with self.assertRaises(ValueError):
                verify_record(altered)
        altered = copy.deepcopy(self.record)
        altered["events"][2]["live_guard"]["source_policy_digest"] = "different"
        with self.assertRaisesRegex(ValueError, "policy mismatch"):
            verify_record(altered)
        altered = copy.deepcopy(self.record)
        altered["events"][1]["live_guard"]["conntrack_transfer_claimed"] = True
        with self.assertRaisesRegex(ValueError, "state transfer"):
            verify_record(altered)

    def test_rejects_missing_flow_or_cleanup(self):
        for field, value in (("balanced_flow_counts", {"source": 0, "target": 1}),
                             ("leftover_namespaces", "vfwlab2-fw-source"),
                             ("drain_before_scale_in", False)):
            altered = copy.deepcopy(self.record)
            altered[field] = value
            with self.assertRaises(ValueError):
                verify_record(altered)

    def test_snapshot_hash_and_source_fingerprint_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            trial = Path(directory) / "trial"
            trial.mkdir()
            source = trial / "executed-source.zip"
            with zipfile.ZipFile(source, "x") as archive:
                archive.writestr("src/example.py", "x = 1\n")
            digest = hashlib.sha256()
            digest.update(b"src/example.py")
            digest.update(b"x = 1\n")
            self.record["code_sha256"] = digest.hexdigest()
            self.record["executed_source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            record_path = trial / "record.json"
            record_path.write_text(json.dumps(self.record))
            result = build_report([record_path], Path(directory) / "out")
            self.assertTrue(result["trials"][0]["source_snapshot_verified"])
            self.record["code_sha256"] = "wrong"
            record_path.write_text(json.dumps(self.record))
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                build_report([record_path], Path(directory) / "invalid")
