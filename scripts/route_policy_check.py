"""Attest the isolated route-lab firewall policy before a route transition."""

from __future__ import annotations

import json
import subprocess

from guarded_selection import policy_digest


def route_policy_approved(payload: dict) -> bool:
    items = payload.get("nftables")
    if not isinstance(items, list):
        return False
    chains = [item["chain"] for item in items if isinstance(item, dict) and "chain" in item]
    rules = [item["rule"] for item in items if isinstance(item, dict) and "rule" in item]
    if len(chains) != 1 or len(rules) != 4:
        return False
    chain = chains[0]
    if any(chain.get(key) != value for key, value in {
        "family": "inet", "table": "vfw", "name": "forward", "type": "filter",
        "hook": "forward", "policy": "drop",
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
         {"match": {"op": "==", "left": {"&": [
             {"payload": {"protocol": "tcp", "field": "flags"}},
             {"|": ["fin", "syn", "rst", "ack"]},
         ]}, "right": "syn"}},
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
        normalized = [
            {"counter": {}} if isinstance(part, dict) and "counter" in part else part
            for part in expr
        ]
        if normalized != expected_expr:
            return False
    return True


def evaluate_policies(source: dict, target: dict) -> dict[str, object]:
    source_hash = policy_digest(source)
    target_hash = policy_digest(target)
    violations = []
    if source_hash != target_hash:
        violations.append("policy_mismatch")
    if not route_policy_approved(source):
        violations.append("source_policy_not_approved")
    if not route_policy_approved(target):
        violations.append("target_policy_not_approved")
    return {
        "allowed": not violations,
        "violations": violations,
        "source_policy_digest": source_hash,
        "target_policy_digest": target_hash,
    }


def main() -> int:
    policies = []
    for namespace in ("vfwlab3-source", "vfwlab3-target"):
        output = subprocess.run(
            ["ip", "netns", "exec", namespace, "nft", "-j", "list", "table", "inet", "vfw"],
            check=True, capture_output=True, text=True,
        ).stdout
        policies.append(json.loads(output))
    result = evaluate_policies(*policies)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
