import unittest
from vfw_research.recovery_metrics import summarize_recovery

class RecoveryMetricsTests(unittest.TestCase):
    def fixture(self):
        return {"fault": "controller_exit", "blocked_monotonic": 4.1, "restored_monotonic": 4.2,
                "target_committed_monotonic": 2, "fault_started_monotonic": 4,
                "both_routes_blocked": True, "recovery": "RECOVERED", "events": [
                    {"flow_id": f, "sent_monotonic": t, "success": True} for f in range(3) for t in (3, 5)]}

    def test_requires_all_original_flows_resume(self):
        record = self.fixture()
        self.assertTrue(summarize_recovery(record)["acceptance_passed"])
        record["events"].pop()
        self.assertFalse(summarize_recovery(record)["acceptance_passed"])

    def test_fail_closed_is_not_availability_success(self):
        record = self.fixture()
        record.update(fault="target_state_loss", recovery="BLOCKED_STATE_UNAVAILABLE")
        for event in record["events"]:
            if event["sent_monotonic"] == 5:
                event["success"] = False
        summary = summarize_recovery(record)
        self.assertTrue(summary["acceptance_passed"])
        self.assertEqual(summary["disrupted_flows"], 3)
        self.assertIsNone(summary["packet_loss_fraction"])
