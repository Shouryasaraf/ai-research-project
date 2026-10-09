"""Bounded predictive/scaling/proxy lifecycle integration, not a benchmark.

One active flow is assigned a modeled 1 Mbps resource demand. This is NOT a
bandwidth measurement. Existing sockets remain on source; new flows balance.
"""
from __future__ import annotations
import argparse
from dataclasses import replace
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from live_experiment import command
from live_experiment_batch import code_digest
from live_scaling_smoke import CONTROL, METRICS, TARGET_PID, TARGET_FW, counts, wait_counts, start_client
from guarded_selection import _live_evidence, commit_selection, policy_is_approved
from vfw_research.forecasting import EwmaConformalForecaster
from vfw_research.policies import PolicyVariant, run_policy
from vfw_research.scenarios import load_scenario
from vfw_research.scaling import ScalingAction, ScalingManager, ScalingPolicy


def finish(process, backend, label):
    stdout, stderr = process.communicate(timeout=25)
    if process.returncode or stdout.strip().splitlines() != [f"{backend}:{label}-before", f"{backend}:{label}-after"]:
        raise RuntimeError(f"flow continuity assertion failed: {stdout} {stderr}")


def run(output: Path) -> dict:
    if "vfwlab2-" in command("ip", "netns", "list"):
        raise RuntimeError("existing dual-path lab preserved")
    output.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "code_sha256": code_digest(), "events": [],
              "evidence_class": "live proxy lifecycle with modeled flow-to-demand mapping; not transparent state transfer",
              "modeled": {"mbps_per_active_flow": 1, "source_capacity_mbps": 2,
                          "training_history": "constant 1 Mbps", "calibration": "alternating .95/1.05 Mbps",
                          "carbon_risk_resources": "synthetic_small scenario candidate assumptions"}}
    snapshot = output / "executed-source.zip"
    with zipfile.ZipFile(snapshot, "x", zipfile.ZIP_DEFLATED) as archive:
        for directory in (ROOT / "src", ROOT / "scripts", ROOT / "configs"):
            for source in sorted(directory.rglob("*")):
                if source.suffix in {".py", ".sh", ".nft", ".json"} and source.is_file():
                    archive.write(source, source.relative_to(ROOT).as_posix())
    if code_digest() != record["code_sha256"]:
        raise RuntimeError("source changed while snapshotting; trial preserved but not executed")
    record["executed_source_sha256"] = hashlib.sha256(snapshot.read_bytes()).hexdigest()
    script = ROOT / "scripts/dual_vfw_testbed.sh"
    clients = []
    target = None
    try:
        command("bash", str(script), "up")
        os.kill(int(TARGET_PID.read_text()), signal.SIGTERM)
        time.sleep(.2)
        TARGET_PID.unlink()
        command("ip", "netns", "exec", TARGET_FW, "nft", "delete", "table", "inet", "vfw")
        model = EwmaConformalForecaster()
        model.fit(tuple([1.0]*60), tuple([.95, 1.05]*15))
        manager = ScalingManager(ScalingPolicy(1, 2, .8, .2, 2, 2, .2))
        scenario = load_scenario(ROOT / "configs/scenarios/synthetic_small.json")
        base = scenario.build_run(scenario.seeds[0])
        warm, ready, scale_requested = False, False, False
        clients = [start_client("old-a", 15), start_client("old-b", 15)]
        wait_counts(source_at_least=2)
        for step in range(16):
            observed = counts()
            demand = float(observed["source"])
            model.observe(demand)
            forecast = model.predict(1)
            scaling = manager.observe(min(1, demand/2), 2 if warm else 1, time.monotonic())
            scale_requested |= scaling.action is ScalingAction.SCALE_OUT
            guard = _live_evidence(CONTROL, TARGET_PID) if warm else None
            invariants = base.decision_input.invariants
            if guard is not None:
                invariants = replace(invariants, source_policy_hash=guard["source_policy_digest"],
                    target_policy_hash=guard["target_policy_digest"], expected_policy_hash=guard["source_policy_digest"],
                    traffic_path_enforced=guard["allowed"], state_mismatch_fraction=0 if guard["source_flow_pinned_at_decision"] else 1)
            inp = replace(base.decision_input, source_capacity_mbps=2, forecast=forecast,
                          target_warm=warm, state_synchronized=ready, invariants=invariants,
                          threshold_context=replace(base.decision_input.threshold_context,
                                                    active_flows=sum(observed.values()),
                                                    uncertainty_fraction=min(1, forecast.width_fraction(2))))
            decision = run_policy(PolicyVariant.FULL, replace(base, decision_input=inp,
                current_utilization=min(1, demand/2), candidates=[replace(base.candidates[0], node_id="target")])).decision
            event = {"step": step, "live_flow_counts": observed, "modeled_demand_mbps": demand,
                     "scaling_action": scaling.action.value, "decision": decision.as_record(), "live_guard": guard}
            record["events"].append(event)
            if decision.action.value == "PREWARM" and scale_requested and not warm:
                command("ip", "netns", "exec", TARGET_FW, "nft", "-f", str(ROOT / "scripts/dual_firewall.nft"))
                target = subprocess.Popen(["ip", "netns", "exec", "vfwlab2-server-target", "python3",
                    str(ROOT / "scripts/flow_service.py"), "backend", "--listen", "10.32.0.2", "--id", "target"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                TARGET_PID.write_text(str(target.pid))
                time.sleep(.25)
                warm = True
                event["actuation"] = "target_firewall_and_backend_started"
            elif decision.action.value == "SYNC":
                if not guard or not guard["allowed"]:
                    raise RuntimeError("source pin readiness failed")
                ready = True
                event["actuation"] = "source_pin_checkpoint_validated_no_conntrack_transfer"
            elif decision.action.value == "COMMIT":
                committed = commit_selection(CONTROL, TARGET_PID, selection="balanced")
                if not committed.get("selection_committed"):
                    raise RuntimeError("live admission guard refused")
                event["actuation"] = "balanced_new_flow_admission"
                break
            elif decision.action.value == "FALLBACK":
                raise RuntimeError("lifecycle precommit safety gate failed; source retained")
            time.sleep(.1)
        else:
            raise RuntimeError("bounded lifecycle never reached guarded admission")
        new = start_client("new-target", 1)
        clients.append(new)
        record["balanced_flow_counts"] = wait_counts(source_at_least=2, target_at_least=1)
        finish(new, "target", "new-target")
        finish(clients[0], "source", "old-a")
        finish(clients[1], "source", "old-b")
        deadline = time.monotonic()+3
        while any(counts().values()) and time.monotonic() < deadline:
            time.sleep(.05)
        if any(counts().values()):
            raise RuntimeError("flows did not drain before deactivation")
        source_policy = json.loads(command("ip", "netns", "exec", "vfwlab2-fw-source", "nft", "-j", "list", "table", "inet", "vfw"))
        if not policy_is_approved(source_policy):
            raise RuntimeError("source policy not approved for post-drain service")
        CONTROL.write_text("source\n")
        time.sleep(.25)
        manager.observe(0, 2, time.monotonic())
        scaled_in = manager.observe(0, 2, time.monotonic())
        if scaled_in.action is not ScalingAction.SCALE_IN:
            raise RuntimeError("scale-in evidence gate failed")
        target.terminate()
        target.wait(timeout=5)
        TARGET_PID.unlink(missing_ok=True)
        command("ip", "netns", "exec", TARGET_FW, "nft", "delete", "table", "inet", "vfw")
        final = command("ip", "netns", "exec", "vfwlab2-client", "python3", str(ROOT / "scripts/flow_client.py"),
                        "10.20.0.1", "after-scale-in").strip()
        if final != "source:after-scale-in":
            raise RuntimeError("post-scale-in source service failed")
        record.update(status="completed", active_paths=[1, 2, 1], original_flow_pins_preserved=True,
                      new_target_flow_verified=True, drain_before_scale_in=True, post_scale_in_service=True)
    except Exception as error:
        record.update(status="failed", error=str(error), traceback=traceback.format_exc())
    finally:
        for process in clients + ([target] if target else []):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
        command("bash", str(script), "down")
        record["leftover_namespaces"] = command("ip", "netns", "list").strip()
        if record["leftover_namespaces"]:
            record["status"] = "failed"
        (output / "record.json").write_text(json.dumps(record, indent=2))
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result = run(args.output)
    print(json.dumps({"status": result["status"], "error": result.get("error")}))
    raise SystemExit(0 if result["status"] == "completed" else 1)
