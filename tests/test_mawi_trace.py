import gzip
import json
import struct
import tempfile
import unittest
from pathlib import Path

from vfw_research.mawi_trace import aggregate_pcap, convert
from vfw_research.trace_adapter import load_trace


def pcap(endian="<", *, nanos=False, out_of_order=False):
    magic = (b"\x4d\x3c\xb2\xa1" if nanos else b"\xd4\xc3\xb2\xa1") if endian == "<" else (
        b"\xa1\xb2\x3c\x4d" if nanos else b"\xa1\xb2\xc3\xd4")
    data = magic + struct.pack(endian + "HHiiii", 2, 4, 0, 0, 96, 1)
    records = [(100, 0, 2, 100), (99 if out_of_order else 102, 0, 2, 200)]
    for seconds, fraction, captured, original in records:
        data += struct.pack(endian + "IIII", seconds, fraction, captured, original) + b"ab"
    return data


class MawiTraceTests(unittest.TestCase):
    def test_streams_original_lengths_without_payload_or_gap_interpolation(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "capture.dump.gz"
            source.write_bytes(gzip.compress(pcap()))
            series, info = aggregate_pcap(source)
            self.assertEqual(series, [(100, 0.0008), (101, 0), (102, 0.0016)])
            self.assertEqual(info["packet_count"], 2)
            self.assertEqual(info["zero_packet_bins"], 1)
            csv_path = Path(directory) / "traffic.csv"
            sidecar = Path(directory) / "traffic.json"
            convert(source, csv_path, sidecar,
                    source="https://mawi.nezu.wide.ad.jp/mawi/test/capture.dump.gz")
            trace = load_trace(csv_path, sidecar)
            self.assertEqual([point.value for point in trace.points], [0.0008, 0, 0.0016])
            self.assertEqual(json.loads(sidecar.read_text())["capture"]["packet_count"], 2)
            with self.assertRaises(FileExistsError):
                convert(source, csv_path, sidecar,
                        source="https://mawi.nezu.wide.ad.jp/mawi/test/capture.dump.gz")

    def test_big_endian_nanosecond_and_malformed_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "capture.pcap"
            source.write_bytes(pcap(">", nanos=True))
            self.assertEqual(len(aggregate_pcap(source)[0]), 3)
            source.write_bytes(pcap(out_of_order=True))
            with self.assertRaisesRegex(ValueError, "out-of-order"):
                aggregate_pcap(source)
            source.write_bytes(pcap()[:-1])
            with self.assertRaisesRegex(ValueError, "truncated"):
                aggregate_pcap(source)
