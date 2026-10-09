"""Supervised active-flow failback and unrecoverable-state containment probes.

Controller interruption retains target kernel state. Target-state loss explicitly
does not restore stale source state. Neither case proves full TCP equivalence.
"""
from __future__ import annotations
import argparse
import fcntl
import json
import os
import select
from pathlib import Path
import subprocess
import sys
import threading
import traceback
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from live_experiment import command, commit_ready, entries, policy_evidence, synchronize
from live_experiment_batch import code_digest
from route_actuator import apply_route, verify_route
from validate_conntrack import compare_entries, parse_entry
from vfw_research.route_transaction import RouteTransaction


def source_ready() -> bool:
    if not policy_evidence()["allowed"]:
        return False
    target = entries("target")
    source = {parse_entry(line)["original"]["sport"]: line for line in entries("source")}
    return len(target) == 3 and all(
        parse_entry(line)["original"]["sport"] in source and
        compare_entries(line, source[parse_entry(line)["original"]["sport"]])["ready_for_route_commit"]
        for line in target)


def trial(output: Path, fault: str, capture: bool = False) -> dict:
    if "vfwlab3-" in command("ip", "netns", "list"):
        raise RuntimeError("existing lab preserved")
    output.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "fault": fault, "code_sha256": code_digest(),
              "scope": "three persistent TCP echo flows; coarse state only; supervised fault detection",
              "samples": []}
    process = None
    controller = None
    recorder = None
    watchdog = None
    script = ROOT / "scripts/route_migration_lab.sh"
    try:
        command("bash", str(script), "up")
        if capture:
            from endpoint_capture import EndpointCapture
            recorder = EndpointCapture(output)
            recorder.start()
        plan = output / "traffic-plan.json"
        plan.write_text(json.dumps({"rates_mbps": [.3]*15, "interval_seconds": 1, "flows": 3}))
        process = subprocess.Popen(["ip", "netns", "exec", "vfwlab3-client", "python3",
                                    str(ROOT / "scripts/paced_traffic.py"), str(plan.resolve())],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        watchdog = threading.Timer(30, lambda: process.kill() if process.poll() is None else None)
        watchdog.start()
        for line in process.stdout:
            sample = json.loads(line)
            if sample["type"] == "ready":
                record["traffic_started_monotonic"] = sample["started_monotonic"]
            elif sample["type"] == "complete":
                record["events"] = sample["events"]
            else:
                record["samples"].append(sample)
                if sample["step"] == 1:
                    record["forward_sync"] = synchronize("source", "target")
                    tx = RouteTransaction(output / "journal", apply_route, verify_route)
                    if fault == "controller_exit":
                        controller = subprocess.Popen([sys.executable, __file__, "--crash-worker",
                                                       "--output", str(output / "journal")],
                                                      stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                        if not select.select([controller.stdout], [], [], 8)[0] or controller.stdout.readline().strip() != "COMMITTED":
                            raise RuntimeError("migration controller did not report committed routes")
                    else:
                        tx.commit(lambda: commit_ready(False, 3))
                    if tx.events()[-1]["state"] != "COMMITTED":
                        raise RuntimeError("initial migration refused")
                    record["target_committed_monotonic"] = time.monotonic()
                if ("target_committed_monotonic" in record and "fault_started_monotonic" not in record
                    and sample["observed_monotonic"] >= record["target_committed_monotonic"] + 2):
                    record["fault_started_monotonic"] = time.monotonic()
                    if fault == "controller_exit":
                        # Terminate the process that committed the target routes;
                        # the independent supervisor retains traffic ownership.
                        controller.stdin.write("crash\n")
                        controller.stdin.flush()
                        code = controller.wait(timeout=5)
                        record["controller_exit_code"] = code
                        if code != 77:
                            raise RuntimeError("controller fault injection failed")
                    else:
                        command("ip", "netns", "exec", "vfwlab3-target", "conntrack", "-D", "-p", "tcp",
                                "--orig-src", "10.50.0.2", "--orig-dst", "10.50.5.2", "--orig-port-dst", "9000")
                    restarted = RouteTransaction(output / "journal", apply_route, verify_route)
                    record["containment"] = restarted.recover(lambda: False)
                    record["blocked_monotonic"] = time.monotonic()
                    record["both_routes_blocked"] = all(verify_route(side, "blocked") for side in ("ingress", "egress"))
                    if fault == "controller_exit":
                        record["reverse_sync"] = synchronize("target", "source")
                        record["recovery"] = restarted.recover(source_ready)
                        record["restored_monotonic"] = time.monotonic()
                    else:
                        record["recovery"] = "BLOCKED_STATE_UNAVAILABLE"
        _, stderr = process.communicate(timeout=5)
        record["stderr"] = stderr
        if process.returncode or "events" not in record:
            raise RuntimeError("traffic process failed")
        from vfw_research.recovery_metrics import summarize_recovery
        record["metrics"] = summarize_recovery(record)
        record["status"] = "completed" if record["metrics"]["acceptance_passed"] else "failed"
    except Exception as error:
        record["status"] = "failed"
        record["error"] = type(error).__name__ + ": " + str(error)
        record["error_traceback"] = traceback.format_exc()
    finally:
        if watchdog:
            watchdog.cancel()
        if controller is not None and controller.poll() is None:
            controller.kill()
            controller.wait(timeout=5)
        if process is not None and process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
        if recorder is not None:
            time.sleep(2)
            recorder.stop()
            try:
                record["packet_observation"] = recorder.analyze()
                if not record["packet_observation"]["comparison_valid"]:
                    record["status"] = "failed"
                    record["packet_observation_error"] = "capture comparison validity failed"
            except Exception as error:
                record["status"] = "failed"
                record["packet_observation_error"] = str(error)
        command("bash", str(script), "down")
        record["leftover_namespaces"] = command("ip", "netns", "list").strip()
        if record["leftover_namespaces"]:
            record["status"] = "failed"
        with (output / "record.json").open("x", encoding="utf-8") as handle:
            json.dump(record, handle, indent=2)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--crash-worker", action="store_true")
    parser.add_argument("--capture", action="store_true")
    args = parser.parse_args()
    if args.crash_worker:
        transaction = RouteTransaction(args.output, apply_route, verify_route)
        transaction.commit(lambda: commit_ready(False, 3))
        print(transaction.events()[-1]["state"], flush=True)
        if sys.stdin.readline().strip() == "crash":
            os._exit(77)
        raise RuntimeError("missing controlled crash signal")
    if os.geteuid() != 0:
        raise PermissionError("Linux root required for isolated lab")
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        args.output.mkdir(parents=True, exist_ok=False)
        for repetition in range(3):
            for fault in ("controller_exit", "target_state_loss"):
                record = trial(args.output / f"r{repetition}-{fault}", fault, args.capture)
                print(json.dumps({"fault": fault, "repetition": repetition, "status": record["status"],
                                  "metrics": record.get("metrics"), "error": record.get("error")}), flush=True)
                if record["status"] != "completed":
                    raise RuntimeError("failed probe retained; stopping")

if __name__ == "__main__":
    main()
