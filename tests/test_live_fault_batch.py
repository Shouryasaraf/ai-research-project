import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from live_fault_batch import parse_observations


class LiveFaultBatchTests(unittest.TestCase):
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
