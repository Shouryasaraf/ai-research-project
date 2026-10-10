import unittest

from vfw_research.tcp_wire_diagnostic import sender_stats


class TcpWireDiagnosticTests(unittest.TestCase):
    def test_rst_and_repeated_payload_are_separate(self):
        base = {"source": "10.50.0.2", "flags": 0x10, "window": 100,
                "payload_key": ("flow", 1), "payload_bytes": 10}
        frames = [base, dict(base), dict(base, flags=0x14, payload_bytes=0,
                                           payload_key=("rst",), window=0),
                  dict(base, source="10.50.5.2")]
        result = sender_stats(frames, "10.50.0.2")
        self.assertEqual(result["sent_packet_instances"], 3)
        self.assertEqual(result["sender_rst_instances"], 1)
        self.assertEqual(result["repeated_payload_sequence_instances"], 1)
        self.assertEqual(result["zero_window_advertisements"], 1)


if __name__ == "__main__":
    unittest.main()
