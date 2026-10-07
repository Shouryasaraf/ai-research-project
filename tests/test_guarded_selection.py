import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
from guarded_selection import evaluate_gate


SOURCE_FLOW = (
    "tcp 6 100 ESTABLISHED src=10.21.0.1 dst=10.31.0.2 sport=41000 dport=9000 "
    "src=10.31.0.2 dst=10.21.0.1 sport=9000 dport=41000 [ASSURED]"
)


APPROVED_POLICY = {"nftables": [
    {"table": {"family": "inet", "name": "vfw"}},
    {"chain": {"family": "inet", "table": "vfw", "name": "forward",
               "type": "filter", "hook": "forward", "policy": "drop"}},
    {"rule": {"family": "inet", "table": "vfw", "chain": "forward", "expr": [
        {"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": "invalid"}},
        {"counter": {"packets": 0, "bytes": 0}}, {"drop": None}]}},
    {"rule": {"family": "inet", "table": "vfw", "chain": "forward", "expr": [
        {"match": {"op": "in", "left": {"ct": {"key": "state"}},
                   "right": ["established", "related"]}},
        {"counter": {"packets": 0, "bytes": 0}}, {"accept": None}]}},
    {"rule": {"family": "inet", "table": "vfw", "chain": "forward", "expr": [
        {"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}},
                   "right": 9000}},
        {"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": "new"}},
        {"counter": {"packets": 0, "bytes": 0}}, {"accept": None}]}},
    {"rule": {"family": "inet", "table": "vfw", "chain": "forward", "expr": [
        {"counter": {"packets": 0, "bytes": 0}}, {"drop": None}]}},
]}


def telemetry(namespace, observed=100.0):
    counters = {"bytes": 0, "packets": 0, "dropped": 0, "errors": 0}
    return {
        "schema_version": 1,
        "namespace": namespace,
        "observed_utc": "2026-10-07T00:00:00Z",
        "observed_monotonic_seconds": observed,
        "source": "unit-test",
        "conntrack_entries": 1,
        "firewall_table_present": True,
        "interfaces": {"input0": {"rx": dict(counters), "tx": dict(counters)}},
    }


def evidence(**changes):
    values = {
        "source_policy": APPROVED_POLICY,
        "target_policy": APPROVED_POLICY,
        "source_entries": SOURCE_FLOW,
        "target_entries": "",
        "source_telemetry": telemetry("vfwlab2-fw-source"),
        "target_telemetry": telemetry("vfwlab2-fw-target"),
        "target_alive": True,
        "current_selection": "source",
        "now_monotonic": 101.0,
    }
    values.update(changes)
    return values


class GuardedSelectionTests(unittest.TestCase):
    def test_valid_source_pinned_flow_allows_new_target_flows(self):
        result = evaluate_gate(**evidence())
        self.assertTrue(result["allowed"])
        self.assertEqual(result["violations"], [])
        self.assertFalse(result["conntrack_transfer_claimed"])
        self.assertTrue(result["source_flow_pinned_at_decision"])
        self.assertEqual(result["source_conntrack_entries_observed"], 1)
        self.assertEqual(result["source_telemetry_age_seconds"], 1.0)

    def test_missing_source_state_rejects_commit(self):
        result = evaluate_gate(**evidence(source_entries=""))
        self.assertIn("source_flow_not_pinned_or_state_mismatch", result["violations"])

    def test_nearby_address_does_not_match_pinned_flow(self):
        nearby = SOURCE_FLOW.replace("src=10.21.0.1 ", "src=10.21.0.10 ", 1)
        result = evaluate_gate(**evidence(source_entries=nearby))
        self.assertIn("source_flow_not_pinned_or_state_mismatch", result["violations"])

    def test_policy_mismatch_rejects_commit(self):
        changed = {"nftables": [{"table": {"family": "inet", "name": "other"}}]}
        result = evaluate_gate(**evidence(target_policy=changed))
        self.assertIn("policy_mismatch", result["violations"])

    def test_two_identical_unsafe_rulesets_are_rejected(self):
        unsafe = {"nftables": [
            {"table": {"family": "inet", "name": "vfw"}},
            {"chain": {"family": "inet", "table": "vfw", "name": "forward",
                       "type": "filter", "hook": "forward", "policy": "accept"}},
        ]}
        result = evaluate_gate(**evidence(source_policy=unsafe, target_policy=unsafe))
        self.assertNotIn("policy_mismatch", result["violations"])
        self.assertIn("source_policy_not_approved", result["violations"])
        self.assertIn("target_policy_not_approved", result["violations"])

    def test_stale_or_invalid_telemetry_rejects_commit(self):
        stale = evaluate_gate(**evidence(target_telemetry=telemetry("vfwlab2-fw-target", 90)))
        self.assertIn("target_telemetry_stale", stale["violations"])
        bad = telemetry("vfwlab2-fw-target")
        bad["firewall_table_present"] = False
        invalid = evaluate_gate(**evidence(target_telemetry=bad))
        self.assertIn("target_telemetry_invalid", invalid["violations"])

    def test_target_failure_and_duplicate_state_reject_commit(self):
        result = evaluate_gate(**evidence(target_alive=False, target_entries=SOURCE_FLOW))
        self.assertIn("target_unhealthy", result["violations"])
        self.assertIn("source_flow_not_pinned_or_state_mismatch", result["violations"])
