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
    "route-run",
    "route-no-seen-reply",
    "route-policy-mismatch",
    "route-rollback",
    "route-trace-payload",
)
DEFAULT_SCENARIOS = tuple(item for item in SCENARIOS if item != "route-trace-payload")

ROUTE_SCENARIOS = {
    "route-run": "run",
    "route-no-seen-reply": "test-no-seen-reply",
    "route-policy-mismatch": "test-policy-mismatch",
    "route-rollback": "test-rollback",
    "route-trace-payload": "test-trace-payload",
}


def parse_observations(output: str) -> dict[str, object]:
    observations: dict[str, object] = {}
    trace_samples: list[dict] = []
    for line in output.splitlines():
        json_line = line.removeprefix("client_output=")
        if json_line.startswith("{"):
            try:
                value = json.loads(json_line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and "active_vfw_paths" in value:
                observations["scaling"] = value
            elif isinstance(value, dict) and "sample_index" in value:
                trace_samples.append(value)
            continue
        if "=" not in line or line.startswith("---"):
            continue
        key, value = line.split("=", 1)
        if key in {
            "dual_vfw_integration_passed", "automatic_proxy_fallback_verified",
            "unsafe_commit_rejected", "unsafe_source_fallback_rejected",
            "new_flow_failed_closed", "live_scaling_smoke_passed",
            "same_tcp_connection_survived_route_change",
            "target_firewall_traversal_verified",
            "unreplied_target_state_rejected_before_route_commit",
            "route_policy_mismatch_rejected_before_commit",
            "validated_source_flow_retained",
            "same_tcp_connection_survived_route_rollback",
            "target_policy_fault_injected",
            "trace_derived_payload_verified",
        }:
            observations[key] = value == "true"
        elif key in {"fallback_recovery_ms", "new_flow_admission_ms",
                     "source_application_flow_drain_ms",
                     "target_established_accept_packets_after"}:
            observations[key] = int(value)
        elif key in {"source_established_accept_packets_before_rollback",
                     "source_established_accept_packets_after_rollback"}:
            observations[key] = int(value)
    if trace_samples:
        observations["trace_samples"] = trace_samples
    return observations


def run_batch(output_directory: Path, *, repeats: int, scenarios: tuple[str, ...] = DEFAULT_SCENARIOS,
              trace_csv: Path | None = None, provenance: Path | None = None) -> Path:
    if platform.system() != "Linux" or not hasattr(os, "geteuid"):
        raise RuntimeError("this privileged harness requires Linux/WSL")
    if os.geteuid() != 0:
        raise PermissionError("run as root inside the isolated test environment")
    if repeats < 1 or any(scenario not in SCENARIOS for scenario in scenarios):
        raise ValueError("invalid repeat count or scenario")
    if "route-trace-payload" in scenarios:
        if trace_csv is None or provenance is None or not trace_csv.is_file() or not provenance.is_file():
            raise ValueError("route-trace-payload requires existing --trace-csv and --provenance")
    scripts = {
        "dual": SCRIPT_DIR / "dual_vfw_testbed.sh",
        "route": SCRIPT_DIR / "route_migration_lab.sh",
        "trace_client": SCRIPT_DIR / "trace_payload_client.py",
    }
    output_directory.mkdir(parents=True, exist_ok=False)
    manifest = {
        "evidence_class": "isolated Linux namespace functional fault regression; not a benchmark",
        "script_sha256": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in scripts.items()
        },
        "scenarios": list(scenarios),
        "repeats": repeats,
        "environment": {"kernel": platform.release(), "python": platform.python_version()},
        "records": [],
    }
    if "route-trace-payload" in scenarios:
        assert trace_csv is not None and provenance is not None
        manifest["trace_csv_sha256"] = hashlib.sha256(trace_csv.read_bytes()).hexdigest()
        manifest["provenance_sha256"] = hashlib.sha256(provenance.read_bytes()).hexdigest()
    failures = []
    for scenario in scenarios:
        for repetition in range(repeats):
            started = datetime.now(timezone.utc).isoformat()
            selected_script = scripts["route" if scenario in ROUTE_SCENARIOS else "dual"]
            selected_command = ROUTE_SCENARIOS.get(scenario, scenario)
            command = ["bash", str(selected_script), selected_command]
            if scenario == "route-trace-payload":
                assert trace_csv is not None and provenance is not None
                command.extend([str(trace_csv.resolve()), str(provenance.resolve())])
            timed_out = False
            try:
                result = subprocess.run(
                    command, cwd=SCRIPT_DIR.parent,
                    capture_output=True, text=True, timeout=45,
                )
            except subprocess.TimeoutExpired as error:
                timed_out = True
                subprocess.run(["bash", str(selected_script), "down"], capture_output=True, text=True,
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
                "route-run": "same_tcp_connection_survived_route_change",
                "route-no-seen-reply": "unreplied_target_state_rejected_before_route_commit",
                "route-policy-mismatch": "route_policy_mismatch_rejected_before_commit",
                "route-rollback": "same_tcp_connection_survived_route_rollback",
                "route-trace-payload": "trace_derived_payload_verified",
            }[scenario]
            trace_samples = observed.get("trace_samples", [])
            trace_ok = scenario != "route-trace-payload" or (
                len(trace_samples) == 2
                and [row.get("sample_index") for row in trace_samples] == [0, 1]
                and all(row.get("response_verified") is True for row in trace_samples)
                and all(row.get("trace_csv_sha256") == manifest["trace_csv_sha256"]
                        for row in trace_samples)
                and observed.get("same_tcp_connection_survived_route_change") is True
                and observed.get("target_firewall_traversal_verified") is True
            )
            passed = (result.returncode == 0 and observed.get(expected_key) is True
                      and trace_ok and not leaked)
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
    parser.add_argument("--scenarios", nargs="+", choices=SCENARIOS, default=list(DEFAULT_SCENARIOS))
    parser.add_argument("--trace-csv", type=Path)
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()
    path = run_batch(args.output_directory, repeats=args.repeats, scenarios=tuple(args.scenarios),
                     trace_csv=args.trace_csv, provenance=args.provenance)
    result = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps({"manifest": str(path), "all_passed": result["all_passed"]}))
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
