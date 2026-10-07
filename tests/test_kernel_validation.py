import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_conntrack.py"
SPEC = importlib.util.spec_from_file_location("validate_conntrack", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SOURCE = (
    "tcp 6 100 ESTABLISHED src=10.1.1.2 dst=10.2.2.2 sport=40000 dport=5201 "
    "src=10.2.2.2 dst=10.1.1.2 sport=5201 dport=40000 [ASSURED] mark=0 use=1"
)
TARGET = SOURCE.replace("[ASSURED]", "[UNREPLIED] [ASSURED]")


class KernelValidationTests(unittest.TestCase):
    def test_matching_supported_tuple_fields(self):
        result = MODULE.compare_entries(SOURCE, TARGET)
        self.assertTrue(result["supported_fields_match"])
        self.assertTrue(result["target_unreplied"])
        self.assertFalse(result["ready_for_route_commit"])
        self.assertFalse(result["flow_continuity_validated"])

    def test_wrong_reply_tuple_is_rejected(self):
        wrong = TARGET.replace("sport=5201 dport=40000", "sport=5201 dport=40001")
        self.assertIn("reply", MODULE.compare_entries(SOURCE, wrong)["mismatched_fields"])

    def test_missing_assured_status_is_rejected(self):
        wrong = TARGET.replace("[ASSURED]", "")
        self.assertIn("assured", MODULE.compare_entries(SOURCE, wrong)["mismatched_fields"])

    def test_seen_reply_target_is_ready_for_route_commit(self):
        result = MODULE.compare_entries(SOURCE, SOURCE)
        self.assertTrue(result["ready_for_route_commit"])

    def test_incomplete_entry_is_rejected(self):
        with self.assertRaises(ValueError):
            MODULE.parse_entry("tcp 6 100 ESTABLISHED src=10.1.1.2")
