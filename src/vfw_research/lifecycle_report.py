"""Verify bounded proxy lifecycle records and generate a reproducible report."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ACTUATIONS = (
    "target_firewall_and_backend_started",
    "source_pin_checkpoint_validated_no_conntrack_transfer",
    "balanced_new_flow_admission",
)
ACTIONS = ("PREWARM", "SYNC", "COMMIT")


def verify_record(record: dict) -> dict:
    if record.get("status") != "completed" or record.get("leftover_namespaces"):
        raise ValueError("lifecycle did not complete cleanly")
    if record.get("active_paths") != [1, 2, 1]:
        raise ValueError("scale-out/scale-in path evidence missing")
    if record.get("modeled", {}).get("mbps_per_active_flow") != 1:
        raise ValueError("modeled demand provenance missing")
    events = record.get("events", [])
    actuated = [e for e in events if "actuation" in e]
    if [e["actuation"] for e in actuated] != list(ACTUATIONS):
        raise ValueError("lifecycle actuation order invalid")
    if [e.get("decision", {}).get("action") for e in actuated] != list(ACTIONS):
        raise ValueError("policy decisions do not match actuation")
    if actuated[0].get("scaling_action") != "SCALE_OUT":
        raise ValueError("target started without scale-out")
    for event in actuated[1:]:
        guard = event.get("live_guard") or {}
        if not guard.get("allowed") or not guard.get("source_flow_pinned_at_decision"):
            raise ValueError("live source-pin guard missing")
        if guard.get("conntrack_transfer_claimed") is not False:
            raise ValueError("unsupported state transfer claim")
        if guard.get("source_policy_digest") != guard.get("target_policy_digest"):
            raise ValueError("policy mismatch at admission")
    balanced = record.get("balanced_flow_counts", {})
    if balanced.get("source", 0) < 2 or balanced.get("target", 0) < 1:
        raise ValueError("pinned and new flow observations missing")
    for key in ("original_flow_pins_preserved", "new_target_flow_verified",
                "drain_before_scale_in", "post_scale_in_service"):
        if record.get(key) is not True:
            raise ValueError(f"missing lifecycle assertion: {key}")
    return {"status": "completed", "actions": list(ACTIONS), "active_paths": [1, 2, 1],
            "source_flows_at_admission": balanced["source"],
            "target_flows_at_admission": balanced["target"],
            "modeled_input": True, "conntrack_transfer": False,
            "code_sha256": record["code_sha256"]}


def build_report(records: list[Path], output: Path) -> dict:
    if not records or len({p.resolve() for p in records}) != len(records):
        raise ValueError("provide distinct lifecycle records")
    rows = []
    for path in records:
        record = json.loads(path.read_text(encoding="utf-8"))
        row = verify_record(record)
        if "executed_source_sha256" in record:
            snapshot = path.parent / "executed-source.zip"
            if hashlib.sha256(snapshot.read_bytes()).hexdigest() != record["executed_source_sha256"]:
                raise ValueError("executed source snapshot hash mismatch")
            digest = hashlib.sha256()
            with zipfile.ZipFile(snapshot) as archive:
                if archive.testzip() is not None:
                    raise ValueError("executed source snapshot damaged")
                for name in archive.namelist():
                    digest.update(name.encode())
                    digest.update(archive.read(name))
            if digest.hexdigest() != record["code_sha256"]:
                raise ValueError("executed source does not reproduce code fingerprint")
            row["source_snapshot_verified"] = True
        else:
            row["source_snapshot_verified"] = False
        row.update(trial=path.parent.name, raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(row)
    report = {"scope": "bounded proxy lifecycle functional repetitions; not a benchmark",
              "trials": rows, "all_verified": len(rows) == len(records),
             "caveats": ["1 Mbps per flow and 2 Mbps source capacity are modeled",
                          "source-pinned SYNC validates a checkpoint; it does not transfer conntrack",
                          "carbon/risk/resource inputs are synthetic candidate assumptions",
                          "earlier trials without executed-source.zip retain only a code fingerprint",
                          "post-admission recovery and production lifecycle remain unverified here"]}
    output.mkdir(parents=True, exist_ok=False)
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = ["# Predictive proxy lifecycle evidence", "", report["scope"], "",
             "| Trial | Controller actions | Active paths | Source / target flows at admission | Source snapshot | Clean |",
             "|---|---|---|---:|---|---|"]
    for row in rows:
        lines.append(f'| {row["trial"]} | {" → ".join(row["actions"])} | '
                     f'{" → ".join(map(str, row["active_paths"]))} | '
                     f'{row["source_flows_at_admission"]} / {row["target_flows_at_admission"]} | '
                     f'{"verified" if row["source_snapshot_verified"] else "fingerprint only"} | yes |')
    lines.extend(["", "Each row is validated against its raw JSON record; SHA-256 values are in summary.json.",
                  "The `SYNC` action verifies source pinning and policy equivalence in this proxy path; it does not copy conntrack state.",
                  "Traffic demand and carbon/risk/resource inputs are modeled, and this is not a comparative benchmark.",
                  "Post-admission recovery was tested separately; this witness does not establish a complete production lifecycle.", ""])
    (output / "results.md").write_text("\n".join(lines), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", nargs="+", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build_report(args.records, args.output)["all_verified"]))
