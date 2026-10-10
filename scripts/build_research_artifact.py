"""Local allowlisted artifact archive; excludes captures, credentials and Git data."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".py", ".sh", ".nft", ".json", ".md", ".bib", ".toml", ".yml", ".csv"}
ATTESTED_CAPTURE_SCOPES = {
    "three persistent TCP echo flows; coarse state only; supervised fault detection",
    "three persistent TCP echo flows; isolated paired endpoint capture control",
}


def collect(root: Path, evidence: list[Path], include_lab_captures: bool = False) -> list[Path]:
    root = root.resolve()
    paths = set()
    for directory in ("src", "scripts", "configs", "tests", "docs", ".github/workflows"):
        for path in (root / directory).rglob("*"):
            if path.is_file() and path.suffix in SOURCE_SUFFIXES and "__pycache__" not in path.parts:
                paths.add(path)
    for name in ("README.md", "pyproject.toml", "LICENSE"):
        if (root / name).is_file():
            paths.add(root / name)
    raw = (root / "artifacts/raw").resolve()
    for directory in evidence:
        resolved = directory.resolve()
        if not resolved.is_relative_to(raw) or not resolved.is_dir() or directory.is_symlink():
            raise ValueError("evidence must be an explicit local directory under artifacts/raw")
        for path in resolved.rglob("*"):
            if path.is_file() and (path.name in {"record.json", "records.json", "manifest.json", "campaign.json",
                                                "traffic-plan.json", "executed-source.zip", "results.md"}
                                   or (path.suffix == ".json" and path.stem.isdigit())):
                paths.add(path)
        if include_lab_captures:
            for record_path in resolved.rglob("record.json"):
                record = json.loads(record_path.read_text(encoding="utf-8"))
                observation = record.get("packet_observation")
                if not observation:
                    continue
                source = record.get("source", {})
                scaled_trace = (source.get("kind") == "scaled external trace"
                                and isinstance(source.get("csv_sha256"), str)
                                and len(source["csv_sha256"]) == 64
                                and type(source.get("scale")) in (int, float)
                                and math.isfinite(source["scale"])
                                and source["scale"] > 0)
                isolated_live = (record.get("evidence_class") ==
                    "single-host namespace live pilot; modeled carbon/risk; coarse TCP state copy"
                    and (source.get("kind") == "seeded synthetic demand" or scaled_trace)
                    and record.get("status") == "completed")
                if record.get("scope") not in ATTESTED_CAPTURE_SCOPES and not isolated_live:
                    raise ValueError("capture is not attested as an isolated synthetic lab")
                for node in ("client", "server"):
                    capture = record_path.parent / f"{node}.pcap"
                    if hashlib.sha256(capture.read_bytes()).hexdigest() != observation["capture_sha256"][node]:
                        raise ValueError("lab capture hash mismatch")
                    paths.add(capture)
                    log = record_path.parent / f"{node}-capture.log"
                    if log.is_file():
                        paths.add(log)
    for path in paths:
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("artifact symlinks/out-of-root paths are prohibited")
    return sorted(paths)


def build(root: Path, evidence: list[Path], output: Path, include_lab_captures: bool = False,
          max_uncompressed_mib: int = 100) -> dict:
    root = root.resolve()
    if (type(max_uncompressed_mib) is not int or not 1 <= max_uncompressed_mib <= 500
            or (max_uncompressed_mib > 100 and not include_lab_captures)):
        raise ValueError("larger artifact limit requires attested lab captures and is capped at 500 MiB")
    files = collect(root, evidence, include_lab_captures)
    if sum(path.stat().st_size for path in files) > max_uncompressed_mib * 1024 * 1024:
        raise ValueError("artifact exceeds configured local safety bound")
    manifest = {"classification": "local research development artifact; redistribution license not implied",
                "excluded": ["external/original traffic captures", "unattested captures", "credentials", "Git internals", "Python environments"],
                "verified_synthetic_lab_captures_included": include_lab_captures,
                "files": {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in files}}
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(root).as_posix())
        archive.writestr("ARTIFACT_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("artifact integrity failed")
        for name, expected in manifest["files"].items():
            if hashlib.sha256(archive.read(name)).hexdigest() != expected:
                raise RuntimeError("source changed while archiving; artifact is not validated")
    return {"files": len(files), "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, nargs="+", required=True)
    parser.add_argument("--include-lab-captures", action="store_true")
    parser.add_argument("--max-uncompressed-mib", type=int, default=100)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.evidence, args.output, args.include_lab_captures,
                           args.max_uncompressed_mib), indent=2))
