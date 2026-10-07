"""Guard the dual-vFW proxy's new-flow selection with live kernel evidence.

This testbed pins existing flows to the source. The target never receives the
existing flow's tuple, so this is not a transferred-flow validation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from collect_network_telemetry import collect

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from vfw_research.telemetry import NetworkTelemetrySnapshot


SOURCE_NS = "vfwlab2-fw-source"
TARGET_NS = "vfwlab2-fw-target"
SOURCE_FLOW = ("10.21.0.1", "10.31.0.2", "9000")


def command(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def _normalized(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: _normalized(child)
            for key, child in value.items()
            if key not in {"handle", "packets", "bytes"}
        }
    if isinstance(value, list):
        return [_normalized(child) for child in value]
    return value


def policy_digest(payload: dict) -> str:
    normalized = json.dumps(_normalized(payload), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def policy_is_approved(payload: dict) -> bool:
    """Accept only this testbed's explicit default-deny forward policy.

    Equality between two rulesets is insufficient: two identical allow-all
    policies must never pass the migration gate.
    """
    items = payload.get("nftables")
    if not isinstance(items, list):
        return False
    chains = [item["chain"] for item in items if isinstance(item, dict) and "chain" in item]
    rules = [item["rule"] for item in items if isinstance(item, dict) and "rule" in item]
    if len(chains) != 1 or len(rules) != 4:
        return False
    chain = chains[0]
    if any(chain.get(key) != value for key, value in {
        "family": "inet", "table": "vfw", "name": "forward",
        "type": "filter", "hook": "forward", "policy": "drop",
    }.items()):
        return False
    expected = [
        [{"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": "invalid"}},
         {"counter": {}}, {"drop": None}],
        [{"match": {"op": "in", "left": {"ct": {"key": "state"}},
                    "right": ["established", "related"]}},
         {"counter": {}}, {"accept": None}],
        [{"match": {"op": "==", "left": {"payload": {"protocol": "tcp", "field": "dport"}},
                    "right": 9000}},
         {"match": {"op": "in", "left": {"ct": {"key": "state"}}, "right": "new"}},
         {"counter": {}}, {"accept": None}],
        [{"counter": {}}, {"drop": None}],
    ]
    for rule, expected_expr in zip(rules, expected):
        if any(rule.get(key) != value for key, value in {
            "family": "inet", "table": "vfw", "chain": "forward",
        }.items()):
            return False
        expr = rule.get("expr")
        if not isinstance(expr, list):
            return False
        normalized_expr = [
            {"counter": {}} if isinstance(part, dict) and "counter" in part else part
            for part in expr
        ]
        if normalized_expr != expected_expr:
            return False
    return True


def _age_or_none(observation: dict, now_monotonic: float) -> float | None:
    observed = observation.get("observed_monotonic_seconds")
    if isinstance(observed, (int, float)) and math.isfinite(observed):
        return now_monotonic - observed
    return None


def source_flow_pinned(source_entries: str, target_entries: str) -> bool:
    def is_expected_original_tuple(line: str) -> bool:
        if not line.startswith("tcp "):
            return False
        fields = [token for token in line.split() if token.startswith(("src=", "dst=", "dport="))]
        return (
            len(fields) >= 3
            and fields[0] == f"src={SOURCE_FLOW[0]}"
            and fields[1] == f"dst={SOURCE_FLOW[1]}"
            and f"dport={SOURCE_FLOW[2]}" in fields[:4]
        )

    matching = [line for line in source_entries.splitlines() if is_expected_original_tuple(line)]
    return (
        bool(matching)
        and all("ESTABLISHED" in line and "[ASSURED]" in line for line in matching)
        and not any(is_expected_original_tuple(line) for line in target_entries.splitlines())
    )


def evaluate_gate(
    *,
    source_policy: dict,
    target_policy: dict,
    source_entries: str,
    target_entries: str,
    source_telemetry: dict,
    target_telemetry: dict,
    target_alive: bool,
    current_selection: str,
    now_monotonic: float,
    max_age_seconds: float = 2.0,
) -> dict[str, object]:
    violations: list[str] = []
    source_hash = policy_digest(source_policy)
    target_hash = policy_digest(target_policy)
    pinned = source_flow_pinned(source_entries, target_entries)
    if source_hash != target_hash:
        violations.append("policy_mismatch")
    if not policy_is_approved(source_policy):
        violations.append("source_policy_not_approved")
    if not policy_is_approved(target_policy):
        violations.append("target_policy_not_approved")
    if not target_alive:
        violations.append("target_unhealthy")
    if current_selection != "source":
        violations.append("selection_not_source")
    if not pinned:
        violations.append("source_flow_not_pinned_or_state_mismatch")
    for name, observation in (("source", source_telemetry), ("target", target_telemetry)):
        try:
            validated = NetworkTelemetrySnapshot.from_record(observation)
        except (KeyError, TypeError, ValueError, OverflowError):
            violations.append(f"{name}_telemetry_invalid")
            continue
        if validated.namespace != (SOURCE_NS if name == "source" else TARGET_NS):
            violations.append(f"{name}_telemetry_wrong_namespace")
        try:
            fresh = validated.is_fresh(now_monotonic, max_age_seconds)
        except ValueError:
            fresh = False
        if not fresh:
            violations.append(f"{name}_telemetry_stale")
    return {
        "allowed": not violations,
        "violations": violations,
        "decided_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_policy_digest": source_hash,
        "target_policy_digest": target_hash,
        "source_flow_pinned_at_decision": pinned,
        "source_conntrack_entries_observed": len(source_entries.splitlines()),
        "target_conntrack_entries_observed": len(target_entries.splitlines()),
        "source_telemetry_observed_utc": source_telemetry.get("observed_utc"),
        "target_telemetry_observed_utc": target_telemetry.get("observed_utc"),
        "source_telemetry_age_seconds": _age_or_none(source_telemetry, now_monotonic),
        "target_telemetry_age_seconds": _age_or_none(target_telemetry, now_monotonic),
        "existing_flow_strategy": "pinned_on_source",
        "conntrack_transfer_claimed": False,
    }


def _live_evidence(control_file: Path, target_pid_file: Path) -> dict[str, object]:
    source_policy = json.loads(command("ip", "netns", "exec", SOURCE_NS, "nft", "-j", "list", "table", "inet", "vfw"))
    target_policy = json.loads(command("ip", "netns", "exec", TARGET_NS, "nft", "-j", "list", "table", "inet", "vfw"))
    source_entries = command("ip", "netns", "exec", SOURCE_NS, "conntrack", "-L", "-p", "tcp")
    target_entries = command("ip", "netns", "exec", TARGET_NS, "conntrack", "-L", "-p", "tcp")
    source_telemetry = collect(SOURCE_NS)
    target_telemetry = collect(TARGET_NS)
    pid = int(target_pid_file.read_text(encoding="ascii").strip())
    try:
        os.kill(pid, 0)
        alive = True
    except ProcessLookupError:
        alive = False
    return evaluate_gate(
        source_policy=source_policy,
        target_policy=target_policy,
        source_entries=source_entries,
        target_entries=target_entries,
        source_telemetry=source_telemetry,
        target_telemetry=target_telemetry,
        target_alive=alive,
        current_selection=control_file.read_text(encoding="utf-8").strip(),
        now_monotonic=time.monotonic(),
    )


def commit_selection(
    control_file: Path, target_pid_file: Path, *, selection: str = "target"
) -> dict[str, object]:
    if selection not in {"target", "balanced"}:
        raise ValueError("guarded selection must be target or balanced")
    result = _live_evidence(control_file, target_pid_file)
    if not result["allowed"]:
        return result
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=control_file.parent,
            prefix="vfwlab2-selection-", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(f"{selection}\n")
        os.replace(temporary, control_file)
        temporary = None
        result["selection_committed"] = True
        result["selection"] = selection
        return result
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control-file", type=Path, required=True)
    parser.add_argument("--target-pid-file", type=Path, required=True)
    parser.add_argument("--selection", choices=("target", "balanced"), default="target")
    args = parser.parse_args()
    result = commit_selection(args.control_file, args.target_pid_file, selection=args.selection)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
