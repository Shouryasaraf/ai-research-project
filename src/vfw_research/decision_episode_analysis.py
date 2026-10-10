"""Recompute contiguous action episodes from immutable offline decision records.

An episode is a run of COMMIT recommendations, not an executed migration. The
source evaluator independently resets its target for every time step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


def summarize(record: dict) -> list[dict]:
    if record.get("evidence_class") != "offline trace-driven controller decision pilot; no packet replay or migration":
        raise ValueError("expected an offline decision record")
    test_count = record.get("split_counts", {}).get("test")
    if type(test_count) is not int or test_count < 1:
        raise ValueError("invalid held-out count")
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in record.get("decisions", []):
        groups[row["model"], row["policy"]].append(row)
    expected = {(row["model"], row["policy"]) for row in record.get("summary", [])}
    if not expected or set(groups) != expected:
        raise ValueError("decision groups do not match summary")
    result = []
    for (model, policy), rows in sorted(groups.items()):
        rows.sort(key=lambda row: row["test_index"])
        if [row["test_index"] for row in rows] != list(range(test_count)):
            raise ValueError("missing or duplicate held-out decision index")
        counts = [row for row in record["summary"] if row["model"] == model and row["policy"] == policy]
        if len(counts) != 1:
            raise ValueError("duplicate group summary")
        actions = [row["action"] for row in rows]
        commits = sum(action == "COMMIT" for action in actions)
        if commits != counts[0]["action_counts"].get("COMMIT", 0):
            raise ValueError("action count disagrees with raw decisions")
        starts = [index for index, action in enumerate(actions)
                  if action == "COMMIT" and (index == 0 or actions[index - 1] != "COMMIT")]
        lengths = []
        for start in starts:
            end = start
            while end < len(actions) and actions[end] == "COMMIT":
                end += 1
            lengths.append(end - start)
        result.append({"model": model, "policy": policy, "opportunities": test_count,
                       "commit_recommendations": commits,
                       "contiguous_commit_episodes": len(starts),
                       "longest_commit_episode_seconds": max(lengths, default=0) * record["sampling_interval_seconds"],
                       "episode_start_indices": starts})
    return result


def analyze(paths: list[Path]) -> dict:
    if not paths:
        raise ValueError("at least one decision record required")
    output = []
    for path in paths:
        raw = path.read_bytes()
        record = json.loads(raw)
        output.append({"traffic_source": record["traffic_source"],
                       "traffic_csv_sha256": record["traffic_csv_sha256"],
                       "decision_record_sha256": hashlib.sha256(raw).hexdigest(),
                       "sampling_interval_seconds": record["sampling_interval_seconds"],
                       "groups": summarize(record)})
    if len({item["traffic_csv_sha256"] for item in output}) != len(output):
        raise ValueError("repeated traffic CSV; expected distinct workload records")
    return {"evidence_class": "descriptive offline action-run analysis; no migration execution",
            "episode_definition": "maximal contiguous COMMIT recommendations within each model/policy test segment",
            "records": output}


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
