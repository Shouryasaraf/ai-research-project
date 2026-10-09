import unittest
import json
import tempfile
from pathlib import Path
from vfw_research.live_analysis import summarize, trial_metrics, write_summary, render_report, qdisc_drop_delta


def fixture(policy="full_proposed_controller", seed=1):
    return {"policy": policy, "seed": seed, "plan_sha256": "same", "status": "completed",
            "leftover_namespaces": [], "traffic_started_monotonic": 10,
            "traffic_finished_monotonic": 12, "controller_cpu_seconds": .1,
            "controller_maxrss_kib": 100, "transitions": [{"route_committed": True}],
            "traffic_events": [
                {"flow_id": 0, "finished_monotonic": 10.1, "payload_bytes": 1000,
                 "success": True, "rtt_ms": 2},
                {"flow_id": 0, "finished_monotonic": 11.1, "payload_bytes": 1000,
                 "success": True, "rtt_ms": 4},
                {"flow_id": 1, "finished_monotonic": 11.5, "payload_bytes": 1000,
                 "success": False, "rtt_ms": 1000}]}


class LiveAnalysisTests(unittest.TestCase):
    def test_queue_drop_delta_is_not_packet_loss(self):
        def snap(drops):
            return {name: [{"root": True, "kind": "tbf", "handle": "1:", "drops": drops}]
                    for name in ("source_qdisc", "target_qdisc")}
        row = fixture()
        row["network"] = [snap(2), snap(5)]
        self.assertEqual(qdisc_drop_delta(row), 6)
        self.assertIsNone(trial_metrics(row)["packet_loss_fraction"])
        row["network"][-1]["target_qdisc"][0]["handle"] = "2:"
        self.assertIsNone(qdisc_drop_delta(row))
        row["network"] = [snap(5), snap(0)]
        self.assertIsNone(qdisc_drop_delta(row))

    def test_report_retains_negative_comparison(self):
        full, baseline = fixture(), fixture("reactive_threshold")
        baseline["traffic_events"][0]["payload_bytes"] = 2000
        report = render_report(summarize([full, baseline]))
        self.assertIn("-0.004000 Mbps", report)
        self.assertIn("successful requests only", report)

    def test_batch_manifest_requires_complete_matching_records(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch = root / "batch"
            trial = batch / "one"
            trial.mkdir(parents=True)
            row = fixture()
            row["code_sha256"] = "code"
            (trial / "record.json").write_text(json.dumps(row))
            manifest = {"policies": [row["policy"]], "seeds": [1, 2], "code_sha256": "code"}
            (batch / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                write_summary(batch, root / "out")
            manifest["seeds"] = [1]
            manifest["code_sha256"] = "other"
            (batch / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "digest"):
                write_summary(batch, root / "out")
            manifest["code_sha256"] = "code"
            (batch / "manifest.json").write_text(json.dumps(manifest))
            result = write_summary(batch, root / "out")
            self.assertEqual(len(result["provenance"]["raw_record_sha256"]), 1)
            self.assertTrue((root / "out/results.md").exists())

    def test_metrics_count_application_failures_and_do_not_invent_packet_loss(self):
        metrics = trial_metrics(fixture())
        self.assertAlmostEqual(metrics["goodput_mbps"], .008)
        self.assertAlmostEqual(metrics["request_failure_fraction"], 1 / 3)
        self.assertEqual(metrics["rtt_p95_ms"], 4)
        self.assertEqual(metrics["disrupted_flows"], 1)
        self.assertIsNone(metrics["packet_loss_fraction"])
        self.assertIsNone(metrics["migration_interruption_seconds"])

    def test_pair_integrity_and_single_pair_uncertainty(self):
        full, baseline = fixture(), fixture("static_no_migration")
        summary = summarize([full, baseline])
        self.assertIsNone(summary["paired_goodput"][0]["descriptive_paired_bootstrap_ci95"])
        baseline["plan_sha256"] = "different"
        with self.assertRaisesRegex(ValueError, "different traffic"):
            summarize([full, baseline])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize([full, full])
