import unittest

from vfw_research.benefit import adaptive_threshold, calculate_benefit
from vfw_research.models import BenefitTerms, ThresholdContext, ThresholdPolicy


class BenefitTests(unittest.TestCase):
    def setUp(self):
        self.policy = ThresholdPolicy(0.2, 0.001, 0.002, 0.3, 0.1, 0.2, 0.5, 0.1, 0.05, 2.0)

    def test_net_benefit_preserves_all_terms(self):
        terms = BenefitTerms(0.8, 0.2, 0.1, 0.2, 0.1, 0.05, 0.05)
        result = calculate_benefit(terms)
        self.assertAlmostEqual(result.net_benefit, 0.7)
        self.assertEqual(result.terms, terms)

    def test_adaptive_threshold_context(self):
        low = ThresholdContext(0, 0, 0, 0, 0, False, 1)
        high = ThresholdContext(100, 100, 0.5, 2, 1, True, 0)
        self.assertLess(adaptive_threshold(low, self.policy), adaptive_threshold(high, self.policy))

    def test_threshold_is_bounded(self):
        context = ThresholdContext(100000, 100000, 1, 100, 1, True, 0)
        self.assertEqual(adaptive_threshold(context, self.policy), self.policy.maximum)


if __name__ == "__main__":
    unittest.main()

