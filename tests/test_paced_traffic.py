import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/paced_traffic.py"
SPEC = importlib.util.spec_from_file_location("paced_traffic", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AcceptedPayloadTelemetryTests(unittest.TestCase):
    def test_half_open_sample_boundaries_do_not_double_count(self):
        sends = [(1.0, 10), (1.5, 20), (2.0, 30), (3.0, 40)]
        self.assertEqual(MODULE.accepted_payload_bytes(sends, 1.0, 2.0), 30)
        self.assertEqual(MODULE.accepted_payload_bytes(sends, 2.0, 3.0), 30)
        self.assertEqual(MODULE.accepted_payload_bytes(sends, 3.0, 4.0), 40)

    def test_rejects_empty_or_reversed_window(self):
        for start, end in ((1.0, 1.0), (2.0, 1.0)):
            with self.assertRaises(ValueError):
                MODULE.accepted_payload_bytes([], start, end)


if __name__ == "__main__":
    unittest.main()
