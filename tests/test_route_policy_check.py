import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from route_policy_check import evaluate_policies, route_policy_approved
from test_guarded_selection import APPROVED_POLICY


def route_policy():
    policy = deepcopy(APPROVED_POLICY)
    new_rule = policy["nftables"][4]["rule"]
    new_rule["expr"].insert(1, {
        "match": {"op": "==", "left": {"&": [
            {"payload": {"protocol": "tcp", "field": "flags"}},
            {"|": ["fin", "syn", "rst", "ack"]},
        ]}, "right": "syn"}
    })
    return policy


class RoutePolicyCheckTests(unittest.TestCase):
    def test_exact_default_deny_syn_policy_is_allowed(self):
        policy = route_policy()
        self.assertTrue(route_policy_approved(policy))
        self.assertTrue(evaluate_policies(policy, policy)["allowed"])

    def test_two_identical_broad_accept_rulesets_are_rejected(self):
        unsafe = route_policy()
        unsafe["nftables"][4]["rule"]["expr"].pop(1)
        result = evaluate_policies(unsafe, unsafe)
        self.assertFalse(result["allowed"])
        self.assertEqual(result["violations"], [
            "source_policy_not_approved", "target_policy_not_approved",
        ])
