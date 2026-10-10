import hashlib
import tempfile
import unittest
from pathlib import Path

from vfw_research.trace_adapter import load_trace
from vfw_research.zeroswarm_trace import FILENAME, convert
from tests.test_mawi_trace import pcap


class ZeroSwarmTraceTests(unittest.TestCase):
    def test_checksum_and_rate_only_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / FILENAME
            data = pcap()
            source.write_bytes(data)
            csv_path = Path(directory) / "rates.csv"
            sidecar = Path(directory) / "rates.provenance.json"
            with self.assertRaisesRegex(ValueError, "checksum"):
                convert(source, csv_path, sidecar)
            metadata = convert(source, csv_path, sidecar,
                               expected_md5=hashlib.md5(data).hexdigest())
            self.assertEqual(metadata["capture"]["packet_count"], 2)
            self.assertEqual([point.value for point in load_trace(csv_path, sidecar).points],
                             [0.0008, 0, 0.0016])
            with self.assertRaises(FileExistsError):
                convert(source, csv_path, sidecar)

    def test_other_named_normal_file_and_unknown_file(self):
        with tempfile.TemporaryDirectory() as directory:
            data = pcap()
            source = Path(directory) / "ZeroSWARM Normal data_v2.pcap"
            source.write_bytes(data)
            metadata = convert(source, Path(directory) / "rates.csv",
                               Path(directory) / "rates.json",
                               expected_md5=hashlib.md5(data).hexdigest())
            self.assertIn("data_v2.pcap", metadata["version"])
            unknown = Path(directory) / "unknown.pcap"
            unknown.write_bytes(data)
            with self.assertRaisesRegex(ValueError, "publisher-identified"):
                convert(unknown, Path(directory) / "other.csv",
                        Path(directory) / "other.json")


if __name__ == "__main__":
    unittest.main()
