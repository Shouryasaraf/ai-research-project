"""Paired live pilot with shuffled policy order, immutable trials and resume."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import signal
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vfw_research.policies import PolicyVariant
from vfw_research.liveness_guard import POLICY_NAME as LIVENESS_POLICY_NAME


def code_digest() -> str:
    digest = hashlib.sha256()
    for directory in (ROOT / "src", ROOT / "scripts", ROOT / "configs"):
        for path in sorted(directory.rglob("*")):
            if path.suffix in {".py", ".sh", ".nft", ".json"}:
                digest.update(str(path.relative_to(ROOT)).encode())
                digest.update(path.read_bytes())
    return digest.hexdigest()


def resumable(record: dict, policy: str, seed: int, digest: str) -> bool:
    return (record.get("status") == "completed" and not record.get("leftover_namespaces")
            and record.get("policy") == policy and record.get("seed") == seed
            and record.get("code_sha256") == digest)


def timeout_cleanup(output: Path, process_id: int) -> bool:
    """Clean only the timed-out child's owned lab; never a colliding/reused lab."""
    import fcntl
    marker = output / "ownership.json"
    if not marker.is_file():
        return False
    owner = json.loads(marker.read_text(encoding="utf-8"))
    if owner != {"pid": process_id, "namespace_prefix": "vfwlab3-"}:
        return False
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return False
        subprocess.run(["bash", str(ROOT / "scripts/route_migration_lab.sh"), "down"], timeout=20, check=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", type=int, nargs="+", default=[7, 11, 19])
    parser.add_argument("--policies", choices=[p.value for p in PolicyVariant] + [LIVENESS_POLICY_NAME], nargs="+", default=[p.value for p in PolicyVariant])
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--flows", type=int, default=3)
    parser.add_argument("--family", choices=["step", "steady", "bursts", "trend", "flash"], default="step")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--trace-csv", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--capture", action="store_true", help="paired endpoint captures for isolated generated traffic")
    args = parser.parse_args()
    if len(args.seeds) != len(set(args.seeds)) or len(args.policies) != len(set(args.policies)):
        parser.error("duplicate seeds/policies")
    if any(seed < 0 for seed in args.seeds) or not 6 <= args.steps <= 120 or not 1 <= args.flows <= 16:
        parser.error("invalid seed, steps, or flows")
    if bool(args.trace_csv) != bool(args.provenance):
        parser.error("trace CSV and provenance must be supplied together")
    manifest = {"phase": "exploratory_pilot", "code_sha256": code_digest(),
                "seeds": args.seeds, "policies": args.policies, "steps": args.steps,
                "flows": args.flows, "family": args.family, "capture": args.capture,
                "policy_order": "seeded shuffle per repetition",
                "trace_sha256": hashlib.sha256(args.trace_csv.read_bytes()).hexdigest() if args.trace_csv else None,
                "provenance_sha256": hashlib.sha256(args.provenance.read_bytes()).hexdigest() if args.provenance else None}
    path = args.output / "manifest.json"
    if args.resume:
        if json.loads(path.read_text(encoding="utf-8")) != manifest:
            raise ValueError("resume config/code/trace mismatch; use a fresh batch")
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        with path.open("x", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2)
        with zipfile.ZipFile(args.output / "executed-source.zip", "x", zipfile.ZIP_DEFLATED) as archive:
            for directory in (ROOT / "src", ROOT / "scripts", ROOT / "configs"):
                for source in sorted(directory.rglob("*")):
                    if source.suffix in {".py", ".sh", ".nft", ".json"} and source.is_file():
                        archive.write(source, source.relative_to(ROOT).as_posix())
        if code_digest() != manifest["code_sha256"]:
            raise RuntimeError("source changed while snapshotting; batch preserved but not executed")
    for seed in args.seeds:
        policies = list(args.policies)
        random.Random(seed).shuffle(policies)
        for policy in policies:
            if code_digest() != manifest["code_sha256"]:
                raise RuntimeError("code/config changed during batch; stopping to preserve provenance")
            output = args.output / f"s{seed}-{policy}"
            if output.exists():
                record_path = output / "record.json"
                if not record_path.exists() or not resumable(json.loads(record_path.read_text()), policy, seed, manifest["code_sha256"]):
                    raise ValueError(f"interrupted/failed trial preserved at {output}; start a fresh batch")
                print(f"resume: {output.name}", flush=True)
                continue
            command = [sys.executable, str(ROOT / "scripts/live_experiment.py"), "--output", str(output),
                       "--policy", policy, "--seed", str(seed), "--steps", str(args.steps), "--flows", str(args.flows),
                       "--family", args.family]
            if args.trace_csv:
                command.extend(["--trace-csv", str(args.trace_csv.resolve()), "--provenance", str(args.provenance.resolve())])
            if args.capture:
                command.append("--capture")
            process = subprocess.Popen(command, start_new_session=True)
            try:
                code = process.wait(timeout=args.steps + 60)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                cleaned = timeout_cleanup(output, process.pid)
                raise RuntimeError(f"trial timed out; owned cleanup={cleaned}; incomplete evidence retained at {output}")
            if code:
                raise RuntimeError(f"failed trial retained at {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
