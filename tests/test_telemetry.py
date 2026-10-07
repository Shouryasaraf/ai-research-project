import unittest
from dataclasses import replace

from vfw_research.models import GateAction
from vfw_research.policies import PolicyVariant, run_policy
from vfw_research.scenarios import load_scenario
from vfw_research.telemetry import NetworkTelemetrySnapshot, TelemetrySnapshot

from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCENARIO = REPOSITORY_ROOT / "configs" / "scenarios" / "synthetic_small.json"


class TelemetryTests(unittest.TestCase):
    def network_record(self):
        return {
            "schema_version": 1,
            "namespace": "vfwlab2-fw-source",
            "observed_utc": "2026-10-06T11:44:23Z",
            "observed_monotonic_seconds": 100.0,
            "source": "linux-ip-conntrack-nft",
            "conntrack_entries": 1,
            "firewall_table_present": True,
            "interfaces": {
                "input0": {
                    "rx": {"bytes": 100, "packets": 2, "dropped": 0, "errors": 0},
                    "tx": {"bytes": 80, "packets": 2, "dropped": 0, "errors": 0},
                }
            },
        }

    def build_snapshot(self):
        return TelemetrySnapshot(
            node_id="node-a",
            observed_monotonic_seconds=100.0,
            cpu_utilization_fraction=0.4,
            memory_utilization_fraction=0.3,
            throughput_mbps=75.0,
            latency_ms=8.0,
            dropped_packets=2,
            active_flows=12,
            state_size_bytes=4096,
            healthy=True,
            source="unit-fixture",
        )

    def test_freshness_boundary_is_inclusive(self):
        snapshot = self.build_snapshot()
        self.assertTrue(snapshot.is_fresh(105.0, 5.0))
        self.assertFalse(snapshot.is_fresh(105.001, 5.0))

    def test_snapshot_exports_only_measured_fields(self):
        metrics = self.build_snapshot().measured_metrics()
        self.assertEqual(metrics["active_flows_count"], 12.0)
        self.assertEqual(metrics["health_boolean"], 1.0)

    def test_invalid_fraction_is_rejected(self):
        with self.assertRaises(ValueError):
            replace(self.build_snapshot(), cpu_utilization_fraction=1.1)

    def test_stale_telemetry_prevents_commit_for_all_migrating_policies(self):
        scenario = load_scenario(SCENARIO)
        run = scenario.build_run(7)
        stale = replace(run, decision_input=replace(run.decision_input, telemetry_fresh=False))
        for variant in PolicyVariant:
            outcome = run_policy(variant, stale)
            if variant is PolicyVariant.STATIC:
                self.assertEqual(outcome.decision.action, GateAction.WAIT)
            else:
                self.assertEqual(outcome.decision.action, GateAction.FALLBACK)
                self.assertIn("telemetry_stale", outcome.decision.invariant_violations)

    def test_live_network_schema_and_freshness(self):
        snapshot = NetworkTelemetrySnapshot.from_record(self.network_record())
        self.assertTrue(snapshot.is_fresh(104, 5))
        self.assertFalse(snapshot.is_fresh(106, 5))
        self.assertEqual(snapshot.measured_metrics()["interface.input0.rx.bytes"], 100.0)

    def test_live_network_schema_rejects_missing_firewall_and_bad_counters(self):
        missing = self.network_record()
        missing["firewall_table_present"] = False
        with self.assertRaises(ValueError):
            NetworkTelemetrySnapshot.from_record(missing)
        invalid = self.network_record()
        invalid["interfaces"]["input0"]["rx"]["bytes"] = -1
        with self.assertRaises(ValueError):
            NetworkTelemetrySnapshot.from_record(invalid)


if __name__ == "__main__":
    unittest.main()
