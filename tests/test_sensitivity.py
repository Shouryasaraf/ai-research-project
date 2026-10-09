from dataclasses import replace
from pathlib import Path
import unittest
from vfw_research.models import PlacementWeights
from vfw_research.policies import _weights_without, PolicyVariant, run_policy
from vfw_research.scenarios import load_scenario
from vfw_research.sensitivity import evaluate, placement_summary, AXES

class SensitivityTests(unittest.TestCase):
    def base(self):
        definition = load_scenario(Path(__file__).resolve().parents[1] / "configs/scenarios/synthetic_small.json")
        return definition.build_run(definition.seeds[0])

    def test_paired_grid_and_repeatability(self):
        axes = {key: values[:1] for key, values in AXES.items()}
        rows = evaluate(self.base(), axes)
        self.assertEqual(len(rows), 9)
        self.assertEqual(len({row["input_sha256"] for row in rows}), 1)
        self.assertEqual(rows, evaluate(self.base(), axes))
        result = placement_summary(rows)
        self.assertEqual(result["opportunities"], 1)
        self.assertNotIn("node-quarantined", result["policies"][PolicyVariant.FULL.value]["candidate_counts"])
        with self.assertRaisesRegex(ValueError, "paired"):
            placement_summary(rows[:-1])

    def test_risk_ablation_keeps_hard_ceiling(self):
        base = self.base()
        base = replace(base, candidates=[replace(base.candidates[0], security_risk=.9)])
        for variant in (PolicyVariant.RISK_UNAWARE, PolicyVariant.UNCERTAINTY_NO_CARBON_RISK):
            self.assertIsNone(run_policy(variant, base).decision.selected_node_id)

    def test_ablation_renormalizes_actual_weights(self):
        weights = PlacementWeights(.6, .1, .1, .1, .1)
        changed = _weights_without(weights, "carbon")
        self.assertAlmostEqual(changed.capacity, .6/.9)
        self.assertEqual(changed.carbon, 0)
        with self.assertRaises(ValueError):
            _weights_without(PlacementWeights(0, 0, 1, 0, 0), "carbon")
