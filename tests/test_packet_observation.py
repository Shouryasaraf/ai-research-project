from pathlib import Path
import socket
import struct
import tempfile
import unittest
from vfw_research.packet_observation import packets, compare_endpoints

def packet(source, key, payload=1):
    return {"source": source, "key": (key,), "payload_key": (key,), "payload_bytes": payload}

class PacketObservationTests(unittest.TestCase):
    def test_losses_duplicates_and_invalid_capture(self):
        a, b = packet("10.50.0.2", "a"), packet("10.50.5.2", "b")
        result = compare_endpoints([a, a, b], [a, b], capture_drops=0)
        self.assertTrue(result["comparison_valid"])
        self.assertEqual(result["directions"][0]["observed_packet_deficit_fraction"], .5)
        self.assertEqual(result["directions"][0]["repeated_payload_sequence_instances"], 1)
        self.assertFalse(compare_endpoints([a, b], [a, a, b], capture_drops=0)["comparison_valid"])
        self.assertIsNone(compare_endpoints([a, b], [a, b], capture_drops=1)["directions"][0]["observed_packet_deficit_fraction"])

    def test_parse_ethernet_and_reject_truncation(self):
        tcp = struct.pack("!HHIIBBHHH", 12345, 9000, 1, 2, 5 << 4, 24, 4096, 0, 0) + b"test"
        ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20+len(tcp), 3, 0, 64, 6, 0,
                         socket.inet_aton("10.50.0.2"), socket.inet_aton("10.50.5.2"))
        frame = b"\x00"*12 + b"\x08\x00" + ip + tcp
        data = struct.pack("<IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
        data += struct.pack("<IIII", 1, 0, len(frame), len(frame)) + frame
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capture.pcap"
            path.write_bytes(data)
            parsed = packets(path)
            self.assertEqual(parsed[0]["payload_bytes"], 4)
            self.assertEqual(parsed[0]["key"][2], 3)
            self.assertEqual(parsed[0]["flags"], 24)
            self.assertEqual(parsed[0]["window"], 4096)
            path.write_bytes(data[:-1])
            with self.assertRaises(ValueError):
                packets(path)

    def test_empty_or_unknown_drop_counts_are_not_zero_loss(self):
        self.assertFalse(compare_endpoints([], [], capture_drops=0)["comparison_valid"])
        with self.assertRaises(ValueError):
            compare_endpoints([], [], capture_drops=-1)
