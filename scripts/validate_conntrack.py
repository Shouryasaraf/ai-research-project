"""Validate the supported fields of a copied conntrack TCP tuple.

This checks tuple identity and coarse state only. It cannot establish TCP
sequence/window equivalence or end-to-end continuity after path switching.
"""

from __future__ import annotations

import argparse
import json
import re


FIELDS = ("src", "dst", "sport", "dport")


def parse_entry(line: str) -> dict[str, object]:
    if not line.startswith("tcp ") or "ESTABLISHED" not in line:
        raise ValueError("expected an ESTABLISHED TCP conntrack entry")
    pairs = re.findall(r"\b(src|dst|sport|dport)=([^\s]+)", line)
    if len(pairs) < 8:
        raise ValueError("conntrack entry lacks original or reply tuple")
    original = tuple(pairs[:4])
    reply = tuple(pairs[4:8])
    if tuple(name for name, _ in original) != FIELDS or tuple(name for name, _ in reply) != FIELDS:
        raise ValueError("conntrack tuple fields are incomplete or out of order")
    return {
        "original": dict(original),
        "reply": dict(reply),
        "state": "ESTABLISHED",
        "assured": "[ASSURED]" in line,
        "unreplied": "[UNREPLIED]" in line,
    }


def compare_entries(source_line: str, target_line: str) -> dict[str, object]:
    source = parse_entry(source_line)
    target = parse_entry(target_line)
    mismatches = [
        name
        for name in ("original", "reply", "state", "assured")
        if source[name] != target[name]
    ]
    return {
        "supported_fields_match": not mismatches,
        "mismatched_fields": mismatches,
        "source_unreplied": source["unreplied"],
        "target_unreplied": target["unreplied"],
        "ready_for_route_commit": not mismatches and not target["unreplied"],
        "tcp_sequence_window_validated": False,
        "flow_continuity_validated": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--require-seen-reply", action="store_true",
                        help="refuse route commit while the imported target tuple is UNREPLIED")
    args = parser.parse_args()
    result = compare_entries(args.source, args.target)
    print(json.dumps(result, sort_keys=True))
    passed = (result["ready_for_route_commit"] if args.require_seen_reply
              else result["supported_fields_match"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
