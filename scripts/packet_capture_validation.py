"""Paired endpoint capture controls in the isolated route lab.

The forced-drop case applies a bounded 100% netem loss interval to the source
firewall's client-to-server output link. It is a capture-method control, not a
migration performance experiment or production packet-loss estimate.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from endpoint_capture import EndpointCapture
from live_experiment import command
from live_experiment_batch import code_digest

SCOPE = "three persistent TCP echo flows; isolated paired endpoint capture control"


def snapshot(output: Path) -> dict:
    digest = code_digest()
    path = output / "executed-source.zip"
    with zipfile.ZipFile(path, "x", zipfile.ZIP_DEFLATED) as archive:
        for directory in (ROOT / "src", ROOT / "scripts", ROOT / "configs"):
            for source in sorted(directory.rglob("*")):
                if source.is_file() and source.suffix in {".py", ".sh", ".nft", ".json"}:
                    archive.write(source, source.relative_to(ROOT).as_posix())
    if code_digest() != digest:
        raise RuntimeError("source changed while snapshotting; do not execute this batch")
    return {"code_sha256": digest, "executed_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def run_trial(output: Path, mode: str, provenance: dict) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    record = {"status": "running", "mode": mode, "scope": SCOPE, **provenance,
              "plan": {"rates_mbps": [0.3] * 8, "interval_seconds": 1, "flows": 3},
              "drop_injection": None}
    lab = ROOT / "scripts/route_migration_lab.sh"
    capture = None
    traffic = None
    dropped = False
    lab_started = False
    try:
        if "vfwlab3-" in command("ip", "netns", "list"):
            raise RuntimeError("existing lab preserved")
        lab_started = True
        command("bash", str(lab), "up")
        capture = EndpointCapture(output)
        capture.start()
        plan = output / "traffic-plan.json"
        plan.write_text(json.dumps(record["plan"]), encoding="utf-8")
        traffic = subprocess.Popen(["ip", "netns", "exec", "vfwlab3-client", "python3",
                                    str(ROOT / "scripts/paced_traffic.py"), str(plan.resolve())],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        ready = traffic.stdout.readline()
        if json.loads(ready).get("type") != "ready":
            raise RuntimeError("persistent traffic did not become ready")
        time.sleep(1.0)
        if mode == "forced_drop":
            command("ip", "netns", "exec", "vfwlab3-source", "tc", "qdisc", "replace",
                    "dev", "output0", "root", "netem", "loss", "100%")
            dropped = True
            start = time.monotonic()
            time.sleep(1.5)
            command("ip", "netns", "exec", "vfwlab3-source", "tc", "qdisc", "del",
                    "dev", "output0", "root")
            dropped = False
            record["drop_injection"] = {"method": "netem 100% loss on isolated source output0",
                                        "duration_seconds": time.monotonic() - start}
        tail, stderr = traffic.communicate(timeout=20)
        samples = [json.loads(line) for line in tail.splitlines() if line.strip()]
        completed = [sample for sample in samples if sample["type"] == "complete"]
        if traffic.returncode or len(completed) != 1:
            raise RuntimeError(f"traffic failed: {stderr}")
        events = completed[0]["events"]
        record["traffic"] = {"requests": len(events), "successes": sum(e["success"] for e in events),
                             "failures": sum(not e["success"] for e in events),
                             "samples": [s for s in samples if s["type"] == "sample"]}
        time.sleep(2)
        capture.stop()
        record["packet_observation"] = capture.analyze()
        if not record["packet_observation"]["comparison_valid"]:
            raise ValueError("paired endpoint capture invalid")
        if mode == "forced_drop" and record["packet_observation"]["directions"][0]["missing_receiver_instances"] <= 0:
            raise ValueError("controlled drop was not detected in forward capture")
        record["status"] = "completed"
    except Exception as error:
        record.update(status="failed", error=type(error).__name__ + ": " + str(error),
                      error_traceback=traceback.format_exc())
    finally:
        if dropped:
            try:
                command("ip", "netns", "exec", "vfwlab3-source", "tc", "qdisc", "del", "dev", "output0", "root")
            except Exception as error:
                record["drop_cleanup_error"] = str(error)
                record["status"] = "failed"
        if traffic is not None and traffic.poll() is None:
            traffic.kill()
            traffic.communicate(timeout=5)
        if capture is not None:
            capture.stop()
            if "packet_observation" not in record:
                try:
                    record["packet_observation"] = capture.analyze()
                except Exception as error:
                    record["capture_error"] = str(error)
        if lab_started:
            try:
                command("bash", str(lab), "down")
            except Exception as error:
                record["cleanup_error"] = str(error)
                record["status"] = "failed"
        record["leftover_namespaces"] = command("ip", "netns", "list").strip()
        if record["leftover_namespaces"]:
            record["status"] = "failed"
        (output / "record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=2)
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("isolated Linux root environment required")
    if not 1 <= args.repetitions <= 5:
        parser.error("repetitions must be 1..5")
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if "vfwlab3-" in command("ip", "netns", "list"):
            raise RuntimeError("existing lab preserved")
        args.output.mkdir(parents=True, exist_ok=False)
        provenance = snapshot(args.output)
        for repetition in range(args.repetitions):
            for mode in ("ordinary", "forced_drop"):
                record = run_trial(args.output / f"r{repetition}-{mode}", mode, provenance)
                print(json.dumps({"trial": f"r{repetition}-{mode}", "status": record["status"],
                                  "error": record.get("error")}), flush=True)
                if record["status"] != "completed":
                    raise RuntimeError("failed control preserved; stopping")


if __name__ == "__main__":
    main()
