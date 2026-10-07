"""Repeat isolated vFW fault smokes and preserve each observed outcome.

Run as root on Linux/WSL. This is a functional regression batch, not a
latency benchmark; process launch and scheduler overhead are uncontrolled.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SCENARIOS = (
    "run",
    "test-policy-mismatch",
    "test-state-mismatch",
    "test-target-unhealthy",
    "test-unsafe-source-fallback",
    "test-scaling",
)


def parse_observations(output: str) -> dict[str, object]:
    observations: dict[str, object] = {}
    for line in output.splitlines():
        if line.startswith("{"):
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and "active_vfw_paths" in value:
                observations["scaling"] = value
            continue
        if "=" not in line or line.startswith("---"):
            continue
        key, value = line.split("=", 1)
        if key in {
            "dual_vfw_integration_passed", "automatic_proxy_fallback_verified",
            "unsafe_commit_rejected", "unsafe_source_fallback_rejected",
            "new_flow_failed_closed", "live_scaling_smoke_passed",
        }:
            observations[key] = value == "true"
        elif key in {"fallback_recovery_ms", "new_flow_admission_ms",
                     "source_application_flow_drain_ms"}:
            observations[key] = int(value)
    return observations


def run_batch(output_directory: Path, *, repeats: int, scenarios: tuple[str, ...] = SCENARIOS) -> Path:
    if platform.system() != "Linux" or not hasattr(os, "geteuid"):
        raise RuntimeError("this privileged harness requires Linux/WSL")
    if os.geteuid() != 0:
        raise PermissionError("run as root inside the isolated test environment")
    if repeats < 1 or any(scenario not in SCENARIOS for scenario in scenarios):
        raise ValueError("invalid repeat count or scenario")
    script = SCRIPT_DIR / "dual_vfw_testbed.sh"
    script_hash = hashlib.sha256(script.read_bytes()).hexdigest()
    output_directory.mkdir(parents=True, exist_ok=False)
    manifest = {
        "evidence_class": "isolated Linux namespace functional fault regression; not a benchmark",
        "script_sha256": script_hash,
        "scenarios": list(scenarios),
        "repeats": repeats,
        "environment": {"kernel": platform.release(), "python": platform.python_version()},
        "records": [],
    }
    failures = []
    for scenario in scenarios:
        for repetition in range(repeats):
            started = datetime.now(timezone.utc).isoformat()
            timed_out = False
            try:
                result = subprocess.run(
                    ["bash", str(script), scenario], cwd=SCRIPT_DIR.parent,
                    capture_output=True, text=True, timeout=45,
                )
            except subprocess.TimeoutExpired as error:
                timed_out = True
                subprocess.run(["bash", str(script), "down"], capture_output=True, text=True,
                               timeout=10, check=False)
                result = subprocess.CompletedProcess(
                    error.cmd, 124,
                    error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else error.stdout or "",
                    error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr or "",
                )
            remaining = subprocess.run(
                ["ip", "netns", "list"], capture_output=True, text=True, check=True,
            ).stdout
            leaked = [line for line in remaining.splitlines()
                      if line.split() and line.split()[0].startswith("vfwlab")]
            observed = parse_observations(result.stdout)
            expected_key = {
                "run": "dual_vfw_integration_passed",
                "test-policy-mismatch": "unsafe_commit_rejected",
                "test-state-mismatch": "unsafe_commit_rejected",
                "test-target-unhealthy": "unsafe_commit_rejected",
                "test-unsafe-source-fallback": "unsafe_source_fallback_rejected",
                "test-scaling": "live_scaling_smoke_passed",
            }[scenario]
            passed = result.returncode == 0 and observed.get(expected_key) is True and not leaked
            record = {
                "scenario": scenario,
                "repetition": repetition,
                "started_utc": started,
                "finished_utc": datetime.now(timezone.utc).isoformat(),
                "exit_code": result.returncode,
                "timed_out": timed_out,
                "passed": passed,
                "observations": observed,
                "leftover_project_namespaces": leaked,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
            record_name = f"{scenario}-{repetition:03d}.json"
            with (output_directory / record_name).open("x", encoding="utf-8") as handle:
                json.dump(record, handle, indent=2, sort_keys=True)
                handle.write("\n")
            manifest["records"].append({"file": record_name, "passed": passed})
            print(f"{scenario} repetition={repetition} passed={str(passed).lower()}", flush=True)
            if not passed:
                failures.append(record_name)
                break
        if failures:
            break
    manifest["all_passed"] = not failures
    manifest["failure_records"] = failures
    manifest_path = output_directory / "manifest.json"
    with manifest_path.open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--scenarios", nargs="+", choices=SCENARIOS, default=list(SCENARIOS))
    args = parser.parse_args()
    path = run_batch(args.output_directory, repeats=args.repeats, scenarios=tuple(args.scenarios))
    result = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps({"manifest": str(path), "all_passed": result["all_passed"]}))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
