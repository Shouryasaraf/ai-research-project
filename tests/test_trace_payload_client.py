import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from trace_payload_client import payload_bytes


class TracePayloadClientTests(unittest.TestCase):
    def test_bounded_one_percent_trace_payload(self):
        self.assertEqual(payload_bytes(8.0, 1), 10_000)
        self.assertEqual(payload_bytes(0.0, 1), 1)
        self.assertEqual(payload_bytes(1000.0, 1), 65_536)

    def test_invalid_inputs_rejected(self):
        for rate in (-1.0, float("nan")):
            with self.assertRaises(ValueError):
                payload_bytes(rate, 1)
        with self.assertRaises(ValueError):
            payload_bytes(1.0, 0)


if __name__ == "__main__":
    unittest.main()
