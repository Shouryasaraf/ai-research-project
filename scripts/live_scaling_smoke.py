"""Drive real source/target vFW activation from live proxy flow counts.

The surrounding dual_vfw_testbed.sh owns all namespaces and cleanup.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vfw_research.scaling import ScalingAction, ScalingManager, ScalingPolicy


CONTROL = Path("/tmp/vfwlab2-active-backend")
METRICS = Path("/tmp/vfwlab2-proxy-metrics.json")
TARGET_PID = Path("/tmp/vfwlab2-target.pid")
TARGET_FW = "vfwlab2-fw-target"


def command(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def counts() -> dict[str, int]:
    data = json.loads(METRICS.read_text(encoding="utf-8"))
    values = data["active_flows"]
    if set(values) != {"source", "target"} or any(
        not isinstance(value, int) or value < 0 for value in values.values()
    ):
        raise ValueError("proxy active-flow metrics are invalid")
    return values


def wait_counts(*, source_at_least: int = 0, target_at_least: int = 0, timeout: float = 3) -> dict[str, int]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        values = counts()
        if values["source"] >= source_at_least and values["target"] >= target_at_least:
            return values
        time.sleep(0.05)
    raise TimeoutError("active-flow counts did not reach expected levels")


def start_client(label: str, delay: float) -> subprocess.Popen[str]:
    return subprocess.Popen(
        ["ip", "netns", "exec", "vfwlab2-client", "python3", str(ROOT / "scripts/flow_client.py"),
         "10.20.0.1", "--delay", str(delay), f"{label}-before", f"{label}-after"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def finish_client(process: subprocess.Popen[str], expected_backend: str, label: str) -> None:
    output, error = process.communicate(timeout=10)
    if process.returncode != 0 or any(
        line != f"{expected_backend}:{label}-{suffix}"
        for line, suffix in zip(output.strip().splitlines(), ("before", "after"))
    ) or len(output.strip().splitlines()) != 2:
        raise AssertionError(f"client flow failed or changed backend: {output!r} {error!r}")


def run() -> dict[str, object]:
    clients: list[subprocess.Popen[str]] = []
    target_process: subprocess.Popen | None = None
    try:
        old_target_pid = int(TARGET_PID.read_text(encoding="ascii"))
        os.kill(old_target_pid, signal.SIGTERM)
        time.sleep(0.1)
        command("ip", "netns", "exec", TARGET_FW, "nft", "delete", "table", "inet", "vfw")
        TARGET_PID.unlink()
        if CONTROL.read_text(encoding="utf-8").strip() != "source":
            raise AssertionError("scale-in baseline must select source")

        policy = ScalingPolicy(1, 2, 0.8, 0.2, 2, 2, 0.2)
        manager = ScalingManager(policy)
        clients.extend((start_client("old-a", 4), start_client("old-b", 4)))
        loaded = wait_counts(source_at_least=2)
        first_high = manager.observe(min(1.0, loaded["source"] / 2), 1, time.monotonic())
        time.sleep(0.1)
        second_high = manager.observe(min(1.0, counts()["source"] / 2), 1, time.monotonic())
        decisions = [first_high, second_high]
        if decisions[1].action is not ScalingAction.SCALE_OUT:
            raise AssertionError("sustained live source load did not scale out")

        command("ip", "netns", "exec", TARGET_FW, "nft", "-f", str(ROOT / "scripts/dual_firewall.nft"))
        with Path("/tmp/vfwlab2-target.log").open("w", encoding="utf-8") as log:
            target_process = subprocess.Popen(
                ["ip", "netns", "exec", "vfwlab2-server-target", "python3",
                 str(ROOT / "scripts/flow_service.py"), "backend", "--listen", "10.32.0.2", "--id", "target"],
                stdout=log, stderr=subprocess.STDOUT,
            )
        TARGET_PID.write_text(str(target_process.pid), encoding="ascii")
        time.sleep(0.25)
        guard = json.loads(command(
            "python3", str(ROOT / "scripts/guarded_selection.py"),
            "--control-file", str(CONTROL), "--target-pid-file", str(TARGET_PID),
            "--selection", "balanced",
        ))
        if not guard["allowed"] or CONTROL.read_text(encoding="utf-8").strip() != "balanced":
            raise AssertionError("balanced target activation failed guarded validation")

        new_target = start_client("new-target", 1)
        clients.append(new_target)
        balanced = wait_counts(source_at_least=2, target_at_least=1)
        finish_client(new_target, "target", "new-target")
        finish_client(clients[0], "source", "old-a")
        finish_client(clients[1], "source", "old-b")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline and any(counts().values()):
            time.sleep(0.05)
        if any(counts().values()):
            raise AssertionError("active flows did not drain")

        # Stop new admissions to target before deactivating its firewall.
        CONTROL.write_text("source\n", encoding="utf-8")
        time.sleep(0.25)
        first_low = manager.observe(0.0, 2, time.monotonic())
        time.sleep(0.1)
        second_low = manager.observe(0.0, 2, time.monotonic())
        low_decisions = [first_low, second_low]
        if low_decisions[1].action is not ScalingAction.SCALE_IN:
            raise AssertionError("sustained low live load did not scale in")
        target_process.terminate()
        target_process.wait(timeout=3)
        TARGET_PID.unlink(missing_ok=True)
        command("ip", "netns", "exec", TARGET_FW, "nft", "delete", "table", "inet", "vfw")
        final = command(
            "ip", "netns", "exec", "vfwlab2-client", "python3", str(ROOT / "scripts/flow_client.py"),
            "10.20.0.1", "after-scale-in",
        ).strip()
        if final != "source:after-scale-in":
            raise AssertionError("source path failed after scale-in")
        return {
            "scale_out": decisions[1].action.value,
            "scale_in": low_decisions[1].action.value,
            "active_vfw_paths": [1, 2, 1],
            "source_flows_before_scale_out": loaded["source"],
            "concurrent_flows_after_scale_out": balanced,
            "source_flow_affinity_preserved": True,
            "new_target_flow_verified": True,
            "source_restored_after_scale_in": True,
            "topology": "single-host namespace emulation",
        }
    finally:
        for process in clients:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
        if target_process is not None and target_process.poll() is None:
            target_process.terminate()


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
