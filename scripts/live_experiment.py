"""Closed-loop paced-traffic pilot in isolated Linux namespaces.

Source/target bandwidth is enforced by tc. Carbon/risk/resource scores are
explicitly modeled. State copying validates tuples/flags, not TCP windows.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import platform
import random
import resource
import subprocess
import sys
import time
import threading
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from route_policy_check import evaluate_policies
from validate_conntrack import compare_entries, parse_entry
from route_actuator import apply_route, verify_route
from vfw_research.route_transaction import RouteTransaction
from vfw_research.forecasting import EwmaConformalForecaster, time_ordered_split
from vfw_research.models import GateAction, NodeCandidate
from vfw_research.policies import PolicyVariant, run_policy
from vfw_research.liveness_guard import (
    POLICY_NAME as LIVENESS_POLICY_NAME,
    is_uncertainty_wait,
    run_liveness_guarded,
)
from vfw_research.scenarios import load_scenario
from vfw_research.trace_adapter import TraceKind, load_trace
from vfw_research.workloads import live_demand_schedule


def command(*args: str) -> str:
    return subprocess.run(args, capture_output=True, text=True, check=True, timeout=10).stdout


def policy_evidence() -> dict:
    return evaluate_policies(*[
        json.loads(command("ip", "netns", "exec", f"vfwlab3-{name}", "nft", "-j", "list", "table", "inet", "vfw"))
        for name in ("source", "target")
    ])


def entries(node: str) -> list[str]:
    output = command("ip", "netns", "exec", f"vfwlab3-{node}", "conntrack", "-L", "-p", "tcp",
                     "--orig-src", "10.50.0.2", "--orig-dst", "10.50.5.2", "--orig-port-dst", "9000")
    return [line for line in output.splitlines() if "ESTABLISHED" in line and "[ASSURED]" in line]


def synchronize(source: str, target: str) -> dict:
    start = time.monotonic()
    source_entries = entries(source)
    if not source_entries:
        raise ValueError("no established source state available")
    for line in source_entries:
        entry = parse_entry(line)
        original, reply = entry["original"], entry["reply"]
        selector = ["--orig-src", original["src"], "--orig-dst", original["dst"],
                    "--orig-port-src", original["sport"], "--orig-port-dst", original["dport"]]
        subprocess.run(["ip", "netns", "exec", f"vfwlab3-{target}", "conntrack", "-D", "-p", "tcp", *selector],
                       capture_output=True, timeout=5, check=False)
        command("ip", "netns", "exec", f"vfwlab3-{target}", "conntrack", "-I", "-p", "tcp", *selector,
                "--reply-src", reply["src"], "--reply-dst", reply["dst"],
                "--reply-port-src", reply["sport"], "--reply-port-dst", reply["dport"],
                "--state", "ESTABLISHED", "--timeout", "120", "--status", "ASSURED,SEEN_REPLY")
    target_entries = {parse_entry(line)["original"]["sport"]: line for line in entries(target)}
    checks = [compare_entries(line, target_entries[parse_entry(line)["original"]["sport"]])
              for line in source_entries]
    if not all(check["ready_for_route_commit"] for check in checks):
        raise ValueError("copied supported state fields did not validate")
    return {"entry_count": len(checks), "serialized_source_bytes": len("\n".join(source_entries).encode()),
            "duration_seconds": time.monotonic() - start, "checks": checks,
            "finished_monotonic": time.monotonic()}


def route_to(node: str) -> None:
    hops = {"source": ("10.50.1.2", "10.50.3.1"), "target": ("10.50.2.2", "10.50.4.1")}[node]
    command("ip", "-n", "vfwlab3-ingress", "route", "replace", "10.50.5.0/24", "via", hops[0])
    command("ip", "-n", "vfwlab3-egress", "route", "replace", "10.50.0.0/24", "via", hops[1])


def commit_ready(cold: bool, expected_flows: int) -> bool:
    if not policy_evidence()["allowed"]:
        return False
    if cold:
        return True  # Explicit isolated negative-control exception: no state import.
    source = entries("source")
    target = {parse_entry(line)["original"]["sport"]: line for line in entries("target")}
    if len(source) != expected_flows:
        return False
    return all(parse_entry(line)["original"]["sport"] in target and
               compare_entries(line, target[parse_entry(line)["original"]["sport"]])["ready_for_route_commit"]
               for line in source)


def network_snapshot() -> dict:
    result = {"observed_monotonic": time.monotonic()}
    for node in ("source", "target"):
        result[node] = json.loads(command("ip", "-n", f"vfwlab3-{node}", "-s", "-j", "link", "show"))
        result[node + "_qdisc"] = json.loads(command("ip", "netns", "exec", f"vfwlab3-{node}",
                                                     "tc", "-s", "-j", "qdisc", "show", "dev", "output0"))
    return result


def workload(seed: int, steps: int, csv: Path | None, provenance: Path | None, family: str = "step") -> tuple:
    if csv is not None:
        if provenance is None:
            raise ValueError("trace provenance is required")
        trace = load_trace(csv, provenance)
        if trace.kind is not TraceKind.TRAFFIC:
            raise ValueError("traffic trace required")
        split = time_ordered_split([p.value for p in trace.points])
        reference = sorted(split.train)[int(0.9 * (len(split.train) - 1))]
        if reference <= 0 or len(split.test) < steps:
            raise ValueError("trace cannot support requested pilot")
        scale = 1.0 / reference
        train, calibration = tuple(v * scale for v in split.train), tuple(v * scale for v in split.calibration)
        rates = [v * scale for v in split.test[:steps]]
        source = {"kind": "scaled external trace", "csv_sha256": trace.csv_sha256,
                  "source": trace.source, "scale": scale, "original_interval_seconds": trace.sampling_interval_seconds}
    else:
        rates, train, calibration = live_demand_schedule(family, seed, steps)
        source = {"kind": "seeded synthetic demand", "family": family, "seed": seed}
    return train, calibration, rates, source


def run_trial(output: Path, variant: PolicyVariant, *, seed: int, steps: int, flows: int,
              trace_csv: Path | None = None, provenance: Path | None = None, family: str = "step",
              capture: bool = False, liveness_guarded: bool = False) -> dict:
    if os.geteuid() != 0 or not 6 <= steps <= 120 or not 1 <= flows <= 16:
        raise ValueError("requires Linux root, 6..120 steps and 1..16 flows")
    if liveness_guarded and variant is not PolicyVariant.FULL:
        raise ValueError("experimental liveness guard applies only to the full controller")
    train, calibration, rates, source = workload(seed, steps, trace_csv, provenance, family)
    output.mkdir(parents=True, exist_ok=False)
    plan = {"rates_mbps": rates, "interval_seconds": 1.0, "flows": flows}
    (output / "traffic-plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    record = {"status": "running", "policy": LIVENESS_POLICY_NAME if liveness_guarded else variant.value,
              "seed": seed, "source": source,
              "evidence_class": "single-host namespace live pilot; modeled carbon/risk; coarse TCP state copy",
              "plan_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True).encode()).hexdigest(),
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "environment": {"kernel": platform.release(), "python": platform.python_version()},
              "capacity_mbps": {"source": 1.0, "target": 3.0},
              "decisions": [], "transitions": [], "samples": [], "network": []}
    revision = subprocess.run(["git", "-c", f"safe.directory={ROOT}", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=False, timeout=5)
    record["git_revision"] = revision.stdout.strip() or "unavailable"
    from live_experiment_batch import code_digest
    record["code_sha256"] = code_digest()
    record["environment"].update({"nftables": command("nft", "--version").strip(),
                                   "conntrack": command("conntrack", "-V").strip(),
                                   "iproute2": command("ip", "-V").strip()})
    record["modeled_inputs"] = {"source_capacity_mbps": 1.0, "target_capacity_mbps": 3.0,
                                "target_carbon_gco2_per_kwh": 90, "target_risk_score": .18,
                                "cpu_memory_headroom_fraction": .8,
                                "note": "capacity enforced by tc; carbon/risk/headroom supplied as model inputs"}
    model = EwmaConformalForecaster()
    model.fit(train, calibration)
    scenario = load_scenario(ROOT / "configs/scenarios/synthetic_small.json")
    base = scenario.build_run(scenario.seeds[0])
    record["scenario_sha256"] = hashlib.sha256(json.dumps(scenario.payload, sort_keys=True).encode()).hexdigest()
    script = ROOT / "scripts/route_migration_lab.sh"
    process = None
    recorder = None
    watchdog = None
    owns_lab = False
    active, synced = "source", False
    observed_overload_streak = 0
    uncertainty_wait_streak = 0
    cpu_start = time.process_time()
    try:
        existing = command("ip", "netns", "list")
        if any(line.split()[0].startswith("vfwlab3-") for line in existing.splitlines()):
            raise RuntimeError("route-lab namespace collision; existing namespaces preserved")
        owns_lab = True
        with (output / "ownership.json").open("x", encoding="utf-8") as handle:
            json.dump({"pid": os.getpid(), "namespace_prefix": "vfwlab3-"}, handle)
        command("bash", str(script), "up")
        for node, rate in (("source", "1mbit"), ("target", "3mbit")):
            command("ip", "netns", "exec", f"vfwlab3-{node}", "tc", "qdisc", "add", "dev", "output0",
                    "root", "tbf", "rate", rate, "burst", "16kb", "latency", "200ms")
        record["network"].append(network_snapshot())
        if capture:
            from endpoint_capture import EndpointCapture
            recorder = EndpointCapture(output)
            recorder.start()
        process = subprocess.Popen(["ip", "netns", "exec", "vfwlab3-client", "python3",
            str(ROOT / "scripts/paced_traffic.py"), str((output / "traffic-plan.json").resolve())],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        watchdog = threading.Timer(steps + 30, lambda: process.kill() if process.poll() is None else None)
        watchdog.daemon = True
        watchdog.start()
        assert process.stdout is not None
        for line in process.stdout:
            sample = json.loads(line)
            if sample["type"] == "ready":
                record["traffic_started_monotonic"] = sample["started_monotonic"]
                continue
            if sample["type"] == "complete":
                record["traffic_events"] = sample["events"]
                record["traffic_finished_monotonic"] = sample["finished_monotonic"]
                continue
            record["samples"].append(sample)
            model.observe(sample["goodput_mbps"])
            if sample["step"] == steps - 1:
                continue
            forecast = model.predict(1)
            guard = policy_evidence()
            fresh = time.monotonic() - sample["observed_monotonic"] <= 2.0
            inp = replace(base.decision_input, source_capacity_mbps=1.0, forecast=forecast,
                          target_warm=True, state_synchronized=(synced or variant is PolicyVariant.COLD_MIGRATION), telemetry_fresh=fresh,
                          invariants=replace(base.decision_input.invariants,
                              traffic_path_enforced=guard["allowed"],
                              source_policy_hash=guard["source_policy_digest"],
                              target_policy_hash=guard["target_policy_digest"],
                              expected_policy_hash=guard["source_policy_digest"]),
                          threshold_context=replace(base.decision_input.threshold_context,
                              active_flows=flows, uncertainty_fraction=min(1.0, forecast.width_fraction(1.0))))
            run = replace(base, current_utilization=min(1.0, sample["goodput_mbps"]), decision_input=inp,
                          candidates=[NodeCandidate("target", 3.0, 0.0, 0.8, 0.8, 5, 90, 0.18)])
            start = time.monotonic()
            if liveness_guarded:
                baseline = run_policy(PolicyVariant.FULL, run)
                observed_overload_streak = (observed_overload_streak + 1
                    if sample["goodput_mbps"] >= run.overload_trigger_fraction else 0)
                uncertainty_wait_streak = (uncertainty_wait_streak + 1
                    if is_uncertainty_wait(baseline) else 0)
                outcome = run_liveness_guarded(
                    run, observed_overload_streak=observed_overload_streak,
                    uncertainty_wait_streak=uncertainty_wait_streak, baseline=baseline,
                )
                if active == "target":
                    observed_overload_streak = 0
                    uncertainty_wait_streak = 0
                    if outcome.decision.action in (GateAction.PREWARM, GateAction.SYNC, GateAction.COMMIT):
                        outcome = replace(outcome, decision=replace(
                            outcome.decision, action=GateAction.WAIT,
                            reason="already routed through the selected target",
                        ))
            else:
                outcome = run_policy(variant, run)
            record["decisions"].append({"step": sample["step"], "observed_goodput_mbps": sample["goodput_mbps"],
                "forecast": asdict(forecast), "decision": outcome.decision.as_record(),
                "duration_seconds": time.monotonic() - start, "active_path": active, "guard": guard,
                "observed_overload_streak": observed_overload_streak if liveness_guarded else None,
                "uncertainty_wait_streak": uncertainty_wait_streak if liveness_guarded else None})
            action = outcome.decision.action.value
            if active == "source" and action in {"SYNC", "COMMIT"}:
                transition = {"requested_action": action, "started_monotonic": time.monotonic()}
                if action == "SYNC" or variant is not PolicyVariant.COLD_MIGRATION:
                    transition["state_sync"] = synchronize("source", "target")
                    synced = True
                if action == "COMMIT":
                    if not policy_evidence()["allowed"]:
                        raise RuntimeError("policy drift before route commit")
                    transaction = RouteTransaction(output / "route-journal", apply_route, verify_route)
                    transaction.commit(lambda: commit_ready(variant is PolicyVariant.COLD_MIGRATION, flows))
                    if transaction.events()[-1]["state"] != "COMMITTED":
                        raise RuntimeError("route transaction refused")
                    transition["route_journal"] = transaction.events()
                    active = "target"
                    if liveness_guarded:
                        observed_overload_streak = 0
                        uncertainty_wait_streak = 0
                    transition["route_committed"] = True
                transition["finished_monotonic"] = time.monotonic()
                record["transitions"].append(transition)
        stdout, stderr = process.communicate(timeout=5)
        record["client_stderr"] = stderr
        if process.returncode or "traffic_events" not in record:
            raise RuntimeError(f"traffic worker failed: {process.returncode}: {stderr}")
        record["network"].append(network_snapshot())
        if recorder is not None:
            time.sleep(2)
            recorder.stop()
            record["packet_observation"] = recorder.analyze()
            if not record["packet_observation"]["comparison_valid"]:
                raise ValueError("paired endpoint capture invalid")
        record["status"] = "completed"
    except Exception as error:
        record["status"] = "failed"
        record["error"] = type(error).__name__ + ": " + str(error)
    finally:
        if watchdog is not None:
            watchdog.cancel()
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
        if recorder is not None and "packet_observation" not in record:
            recorder.stop()
            try:
                record["packet_observation"] = recorder.analyze()
            except Exception as error:
                record["capture_error"] = str(error)
        # Clean up only when this run reached setup (not on an existing-lab collision).
        if owns_lab:
            subprocess.run(["bash", str(script), "down"], capture_output=True, timeout=15, check=False)
        record["leftover_namespaces"] = [line for line in command("ip", "netns", "list").splitlines()
                                         if line.split()[0].startswith("vfwlab3-")]
        if record["leftover_namespaces"]:
            record["status"] = "failed"
            record["error"] = record.get("error", "lab cleanup incomplete")
        record["controller_cpu_seconds"] = time.process_time() - cpu_start
        record["controller_maxrss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        with (output / "record.json").open("x", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--policy", choices=[v.value for v in PolicyVariant] + [LIVENESS_POLICY_NAME], required=True)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--flows", type=int, default=3)
    parser.add_argument("--family", choices=["step", "steady", "bursts", "trend", "flash"], default="step")
    parser.add_argument("--trace-csv", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--capture", action="store_true", help="capture generated lab TCP at both endpoints")
    args = parser.parse_args()
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        liveness_guarded = args.policy == LIVENESS_POLICY_NAME
        result = run_trial(args.output, PolicyVariant.FULL if liveness_guarded else PolicyVariant(args.policy), seed=args.seed, steps=args.steps,
                           flows=args.flows, trace_csv=args.trace_csv, provenance=args.provenance, family=args.family,
                           capture=args.capture, liveness_guarded=liveness_guarded)
    print(json.dumps({"status": result["status"], "output": str(args.output), "error": result.get("error")}))
    return 0 if result["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
