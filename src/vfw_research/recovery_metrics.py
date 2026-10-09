"""Explicit application-level acceptance checks for bounded fault probes."""

def summarize_recovery(record: dict) -> dict:
    events = record["events"]
    blocked = record["blocked_monotonic"]
    committed = record["target_committed_monotonic"]
    faulted = record["fault_started_monotonic"]
    target_flows = {e["flow_id"] for e in events if e["success"] and committed <= e["sent_monotonic"] < faulted}
    errors = {e["flow_id"] for e in events if not e["success"]}
    result = {"successful_flows_before_fault": len(target_flows), "disrupted_flows": len(errors),
              "fault_to_containment_seconds": blocked - faulted,
              "packet_loss_fraction": None, "exact_downtime_seconds": None}
    if record["fault"] == "controller_exit":
        restored = record["restored_monotonic"]
        resumed = {e["flow_id"] for e in events if e["success"] and e["sent_monotonic"] >= restored}
        result.update({"resumed_original_flows": len(resumed),
                       "fault_to_routes_restored_seconds": restored - faulted,
                       "acceptance_passed": record["both_routes_blocked"] and target_flows == {0, 1, 2}
                       and resumed == target_flows and not errors and record["recovery"] == "RECOVERED"})
    else:
        # In-flight replies sent before containment may complete afterward.
        bypass = sum(e["success"] and e["sent_monotonic"] >= blocked for e in events)
        result.update({"successful_requests_started_after_containment": bypass,
                       "acceptance_passed": record["both_routes_blocked"] and target_flows == {0, 1, 2}
                       and errors == target_flows and bypass == 0 and record["recovery"] == "BLOCKED_STATE_UNAVAILABLE"})
    return result
