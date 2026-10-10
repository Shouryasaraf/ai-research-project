"""Bound repeated offline COMMIT recommendations under a one-target placement model.

This is a post-hoc logical audit, not a controller replay. The underlying
evaluator resets readiness and source placement for every observation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from .decision_episode_analysis import summarize


def audit(record: dict) -> list[dict]:
    # Reuse the raw-row completeness and summary-consistency checks.
    groups = summarize(record)
    output = []
    for group in groups:
        rows = sorted(
            (row for row in record["decisions"]
             if row["model"] == group["model"] and row["policy"] == group["policy"]),
            key=lambda row: row["test_index"],
        )
        commits = [row for row in rows if row["action"] == "COMMIT"]
        if any(not isinstance(row.get("selected_node_id"), str)
               or not row["selected_node_id"] for row in commits):
            raise ValueError("COMMIT without selected target")
        first = commits[0] if commits else None
        target = first["selected_node_id"] if first else None
        same_target_later = sum(
            row["selected_node_id"] == target for row in commits[1:]
        )
        other_target_later = len(commits) - bool(first) - same_target_later
        output.append({
            "model": group["model"], "policy": group["policy"],
            "held_out_opportunities": group["opportunities"],
            "raw_commit_recommendations": len(commits),
            "first_commit_index": first["test_index"] if first else None,
            "first_target_node_id": target,
            "later_same_target_recommendations": same_target_later,
            "later_other_target_recommendations_not_replayed": other_target_later,
            "single_target_possible_distinct_moves_upper_bound": int(first is not None),
        })
    return output


def analyze(paths: list[Path]) -> dict:
    if not paths:
        raise ValueError("at least one decision record is required")
    records = []
    for path in paths:
        raw = path.read_bytes()
        record = json.loads(raw)
        records.append({
            "traffic_source": record["traffic_source"],
            "traffic_csv_sha256": record["traffic_csv_sha256"],
            "decision_record_sha256": hashlib.sha256(raw).hexdigest(),
            "groups": audit(record),
        })
    if len({row["traffic_csv_sha256"] for row in records}) != len(records):
        raise ValueError("duplicate traffic source digest")
    return {
        "evidence_class": "post-hoc one-target logical audit of offline decisions; no migrations executed",
        "assumption": "after a first COMMIT to one target, repeated recommendations to that same target cannot represent additional distinct placements; no forecast or policy is rerun from the new location",
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, nargs="+", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.inputs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps({"records": len(result["records"]), "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
