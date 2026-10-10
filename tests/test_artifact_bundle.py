import importlib.util
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("research_artifact", Path(__file__).resolve().parents[1] / "scripts/build_research_artifact.py")
artifact = importlib.util.module_from_spec(spec)
spec.loader.exec_module(artifact)

class ArtifactTests(unittest.TestCase):
    def test_only_attested_matching_lab_captures_are_opted_in(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trial = root / "artifacts/raw/trial"
            trial.mkdir(parents=True)
            for node in ("client", "server"):
                (trial / f"{node}.pcap").write_bytes(b"synthetic fixture")
            record = {"scope": "three persistent TCP echo flows; coarse state only; supervised fault detection",
                      "packet_observation": {"capture_sha256": {node: hashlib.sha256(b"synthetic fixture").hexdigest()
                                                                 for node in ("client", "server")}}}
            (trial / "record.json").write_text(json.dumps(record))
            self.assertEqual(sum(p.suffix == ".pcap" for p in artifact.collect(root, [trial], True)), 2)
            record["scope"] = "three persistent TCP echo flows; isolated paired endpoint capture control"
            (trial / "record.json").write_text(json.dumps(record))
            self.assertEqual(sum(p.suffix == ".pcap" for p in artifact.collect(root, [trial], True)), 2)
            record = {"evidence_class": "single-host namespace live pilot; modeled carbon/risk; coarse TCP state copy",
                      "source": {"kind": "seeded synthetic demand"}, "status": "completed",
                      "packet_observation": {"capture_sha256": {node: hashlib.sha256(b"synthetic fixture").hexdigest()
                                                                for node in ("client", "server")}}}
            (trial / "record.json").write_text(json.dumps(record))
            self.assertEqual(sum(p.suffix == ".pcap" for p in artifact.collect(root, [trial], True)), 2)
            record["source"] = {"kind": "scaled external trace", "csv_sha256": "a" * 64,
                                "scale": 0.01}
            (trial / "record.json").write_text(json.dumps(record))
            self.assertEqual(sum(p.suffix == ".pcap" for p in artifact.collect(root, [trial], True)), 2)
            record["source"]["scale"] = 2
            (trial / "record.json").write_text(json.dumps(record))
            self.assertEqual(sum(p.suffix == ".pcap" for p in artifact.collect(root, [trial], True)), 2)
            record["source"]["scale"] = float("inf")
            (trial / "record.json").write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "attested"):
                artifact.collect(root, [trial], True)
            record["source"]["scale"] = 0.01
            (trial / "record.json").write_text(json.dumps(record))
            (trial / "client.pcap").write_bytes(b"altered")
            with self.assertRaisesRegex(ValueError, "hash"):
                artifact.collect(root, [trial], True)

    def test_excludes_captures_and_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src/main.py").write_text("pass\n")
            (root / ".env").write_text("not-for-export")
            evidence = root / "artifacts/raw/run"
            evidence.mkdir(parents=True)
            (evidence / "record.json").write_text('{}')
            (evidence / "capture.pcap").write_bytes(b"excluded")
            output = root / "artifact.zip"
            report = artifact.build(root, [evidence], output)
            self.assertEqual(report["files"], 2)
            with zipfile.ZipFile(output) as archive:
                self.assertNotIn(".env", archive.namelist())
                self.assertFalse(any(name.endswith(".pcap") for name in archive.namelist()))
            with self.assertRaises(FileExistsError):
                artifact.build(root, [evidence], output)
            with self.assertRaises(ValueError):
                artifact.collect(root, [root])
            with self.assertRaisesRegex(ValueError, "requires attested"):
                artifact.build(root, [evidence], root / "larger.zip", max_uncompressed_mib=300)
            with self.assertRaisesRegex(ValueError, "capped"):
                artifact.build(root, [evidence], root / "too-large.zip", True, 501)
