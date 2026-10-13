import hashlib
import tempfile
import unittest
from pathlib import Path

from tests.test_mawi_trace import pcap
from vfw_research.pdmfc_trace import FILENAME, convert
from vfw_research.trace_adapter import load_trace


class PdmfcTraceTests(unittest.TestCase):
    def test_strict_checksum_rate_only_and_immutable_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / FILENAME
            data = pcap()
            source.write_bytes(data)
            csv_path = Path(directory) / "rates.csv"
            sidecar = Path(directory) / "rates.provenance.json"
            with self.assertRaisesRegex(ValueError, "checksum"):
                convert(source, csv_path, sidecar)
            self.assertFalse(csv_path.exists())
            metadata = convert(source, csv_path, sidecar,
                               expected_md5=hashlib.md5(data).hexdigest())
            self.assertEqual(metadata["capture"]["packet_count"], 2)
            self.assertEqual([point.value for point in load_trace(csv_path, sidecar).points],
                             [0.0008, 0, 0.0016])
            self.assertEqual(metadata["pcap_sha256"], hashlib.sha256(data).hexdigest())
            with self.assertRaises(FileExistsError):
                convert(source, csv_path, sidecar,
                        expected_md5=hashlib.md5(data).hexdigest())

    def test_unknown_filename_is_rejected_before_conversion(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "other.pcap"
            source.write_bytes(pcap())
            with self.assertRaisesRegex(ValueError, "preselected"):
                convert(source, Path(directory) / "rates.csv",
                        Path(directory) / "rates.json",
                        expected_md5=hashlib.md5(source.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
