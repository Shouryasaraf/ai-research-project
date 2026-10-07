import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from live_fault_batch import DEFAULT_SCENARIOS, SCENARIOS, parse_observations


class LiveFaultBatchTests(unittest.TestCase):
    def test_optional_trace_scenario_does_not_break_default_batch(self):
        self.assertIn("route-trace-payload", SCENARIOS)
        self.assertNotIn("route-trace-payload", DEFAULT_SCENARIOS)

    def test_extracts_only_declared_observations(self):
        output = (
            'fallback_recovery_ms=57\n'
            'automatic_proxy_fallback_verified=true\n'
            'same_tcp_connection_survived_route_change=true\n'
            '{"active_vfw_paths":[1,2,1]}\n'
            'unrelated=123\n'
        )
        self.assertEqual(parse_observations(output), {
            "fallback_recovery_ms": 57,
            "automatic_proxy_fallback_verified": True,
            "same_tcp_connection_survived_route_change": True,
            "scaling": {"active_vfw_paths": [1, 2, 1]},
        })

    def test_extracts_two_trace_payload_observations(self):
        output = (
            'client_output={"sample_index":0,"response_verified":true,"trace_csv_sha256":"abc"}\n'
            '{"sample_index":1,"response_verified":true,"trace_csv_sha256":"abc"}\n'
            'trace_derived_payload_verified=true\n'
            'same_tcp_connection_survived_route_change=true\n'
            'target_firewall_traversal_verified=true\n'
        )
        observed = parse_observations(output)
        self.assertEqual([item["sample_index"] for item in observed["trace_samples"]], [0, 1])
        self.assertTrue(observed["trace_derived_payload_verified"])
