import unittest

from vfw_research.transition_latency import stratify


def event(sent, finished, rtt):
    return {"success": True, "sent_monotonic": sent,
            "finished_monotonic": finished, "rtt_ms": rtt}


class TransitionLatencyTests(unittest.TestCase):
    def test_strict_pre_post_windows_exclude_in_flight(self):
        record = {"status": "completed", "leftover_namespaces": [],
                  "transitions": [{"route_committed": True,
                                   "started_monotonic": 2, "finished_monotonic": 3}],
                  "traffic_events": [event(0, 1, 1), event(1.5, 2.5, 30),
                                     event(2.8, 3.2, 40), event(4, 5, 2)]}
        result = stratify(record)
        self.assertEqual(result["before"], {"successes": 1, "rtt_p95_ms": 1})
        self.assertEqual(result["after"], {"successes": 1, "rtt_p95_ms": 2})
        self.assertEqual(result["excluded_in_flight_successes"], 2)
        self.assertEqual(result["route_commits"], 1)

    def test_no_commit_and_invalid_timing(self):
        record = {"status": "completed", "leftover_namespaces": [],
                  "transitions": [], "traffic_events": [event(0, 1, 1)]}
        self.assertIsNone(stratify(record)["before"])
        record["transitions"] = [{"route_committed": True,
                                  "started_monotonic": 3, "finished_monotonic": 2}]
        with self.assertRaisesRegex(ValueError, "transition"):
            stratify(record)


if __name__ == "__main__":
    unittest.main()
