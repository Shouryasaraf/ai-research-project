import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from flow_service import ProxyState, source_policy_is_approved_now
from unittest.mock import patch


class LiveProxyStateTests(unittest.TestCase):
    def test_fallback_policy_check_fails_closed_when_lookup_fails(self):
        with patch("flow_service.subprocess.run", side_effect=OSError("missing namespace")):
            self.assertFalse(source_policy_is_approved_now())

    def test_balanced_assignment_prefers_less_loaded_and_releases_pin(self):
        with tempfile.TemporaryDirectory() as directory:
            state = ProxyState(Path(directory) / "metrics.json")
            self.assertEqual(state.assign("old-source", "source"), "source")
            self.assertEqual(state.assign("new-balanced", "balanced"), "target")
            self.assertEqual(state.counts, {"source": 1, "target": 1})
            state.release("new-balanced", "target")
            state.release("old-source", "source")
            self.assertEqual(state.counts, {"source": 0, "target": 0})
            self.assertIsNone(state.director.pinned_instance("new-balanced"))
