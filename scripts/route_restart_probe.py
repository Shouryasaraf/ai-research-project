"""Isolated real-process interruption tests; no established-flow recovery claim."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vfw_research.route_transaction import RouteTransaction
from live_experiment import command, policy_evidence
from route_actuator import NETWORKS, apply_route as apply, verify_route as verify

def empty_state_and_policy() -> bool:
    if not policy_evidence()["allowed"]:
        return False
    for node in ("source", "target"):
        if command("ip", "netns", "exec", "vfwlab3-" + node, "conntrack", "-L", "-p", "tcp").strip():
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--crash-after", choices=["ingress", "egress"])
    args = parser.parse_args()
    if args.crash_after:
        def crash_apply(side, destination):
            apply(side, destination)
            if destination == "target" and side == args.crash_after:
                os._exit(77)
        RouteTransaction(args.output, crash_apply, verify).commit(empty_state_and_policy)
        raise RuntimeError("injected interruption did not occur")
    if os.geteuid() != 0:
        raise PermissionError("requires isolated Linux root lab")
    import fcntl
    with open("/tmp/vfwlab-research.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if "vfwlab3-" in command("ip", "netns", "list"):
            raise RuntimeError("existing lab preserved")
        args.output.mkdir(parents=True, exist_ok=False)
        results = []
        try:
            command("bash", str(ROOT / "scripts/route_migration_lab.sh"), "up")
            for repetition in range(3):
                for side in ("ingress", "egress"):
                    journal = args.output / f"r{repetition}-{side}"
                    child = subprocess.run([sys.executable, __file__, "--output", str(journal),
                                            "--crash-after", side], timeout=20, check=False)
                    if child.returncode != 77:
                        raise RuntimeError(f"unexpected interruption return code {child.returncode}")
                    tx = RouteTransaction(journal, apply, verify)
                    started = time.monotonic()
                    blocked = tx.recover(lambda: False)
                    contained = all(verify(direction, "blocked") for direction in NETWORKS)
                    block_seconds = time.monotonic() - started
                    restored = tx.recover(empty_state_and_policy)
                    source = all(verify(direction, "source") for direction in NETWORKS)
                    row = {"repetition": repetition, "crash_after": side,
                           "child_exit": child.returncode, "containment": blocked,
                           "both_routes_blocked": contained, "containment_seconds": block_seconds,
                           "recovery": restored, "both_routes_source": source,
                           "established_flows": 0, "passed": contained and source and restored == "RECOVERED"}
                    results.append(row)
                    if not row["passed"]:
                        raise RuntimeError("restart containment/recovery check failed")
        finally:
            command("bash", str(ROOT / "scripts/route_migration_lab.sh"), "down")
            record = {"evidence_class": "no-flow real-process restart containment probe",
                      "trials": results, "leftover_namespaces": command("ip", "netns", "list").strip(),
                      "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      "transaction_sha256": hashlib.sha256((ROOT / "src/vfw_research/route_transaction.py").read_bytes()).hexdigest()}
            (args.output / "record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
