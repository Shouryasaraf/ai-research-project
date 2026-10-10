import io
import struct
import unittest

from vfw_research.pcapng_rates import aggregate


def block(block_type, body):
    length = len(body) + 12
    return struct.pack("<II", block_type, length) + body + struct.pack("<I", length)


def fixture(*, malformed_trailer=False, simple=False):
    section = block(0x0A0D0D0A, b"\x4d\x3c\x2b\x1a" + struct.pack("<HHq", 1, 0, -1))
    interface = block(1, struct.pack("<HHI", 1, 0, 65535))
    first = block(6, struct.pack("<IIIII", 0, 0, 1_000_000, 4, 100) + b"data")
    second = block(6, struct.pack("<IIIII", 0, 0, 3_000_000, 4, 200) + b"data")
    if simple:
        second = block(3, struct.pack("<I", 100) + b"data")
    if malformed_trailer:
        second = second[:-4] + b"\x00" * 4
    return section + interface + first + second


class PcapngRatesTests(unittest.TestCase):
    def test_aggregates_original_lengths_and_empty_bin(self):
        series, metadata = aggregate(io.BytesIO(fixture()))
        self.assertEqual(series, [(1, 0.0008), (2, 0.0), (3, 0.0016)])
        self.assertEqual(metadata["packet_count"], 2)
        self.assertEqual(metadata["total_original_length_bytes"], 300)
        self.assertEqual(metadata["zero_packet_bins"], 1)

    def test_rejects_corrupt_block_trailer(self):
        with self.assertRaisesRegex(ValueError, "trailer mismatch"):
            aggregate(io.BytesIO(fixture(malformed_trailer=True)))

    def test_rejects_timestampless_packet(self):
        with self.assertRaisesRegex(ValueError, "timestampless"):
            aggregate(io.BytesIO(fixture(simple=True)))

    def test_rejects_truncated_packet(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            aggregate(io.BytesIO(fixture()[:-3]))


if __name__ == "__main__":
    unittest.main()
