import unittest

from vfw_research.accepted_tx_analysis import classify


class AcceptedTxAnalysisTests(unittest.TestCase):
    def test_confusion_counts_use_fixed_threshold_and_strict_planned_capacity(self):
        rows = [
            {"scheduled_mbps": 1.1, "accepted_tx_mbps": .8},
            {"scheduled_mbps": 1.2, "accepted_tx_mbps": .79},
            {"scheduled_mbps": 1.0, "accepted_tx_mbps": .8},
            {"scheduled_mbps": .7, "accepted_tx_mbps": .79},
        ]
        self.assertEqual(classify(rows, "accepted_tx_mbps"),
                         {"TP": 1, "FN": 1, "FP": 1, "TN": 1})


if __name__ == "__main__":
    unittest.main()
