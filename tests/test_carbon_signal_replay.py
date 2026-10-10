import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vfw_research.carbon_signal_replay import evaluate
from vfw_research.scenarios import load_scenario
from vfw_research.trace_adapter import ImportedTrace, TraceKind, TracePoint


SCENARIO = Path(__file__).resolve().parents[1] / "configs/scenarios/synthetic_small.json"


def trace(region, values):
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    region_id = {"north": 1, "london": 13}[region]
    source = ("https://api.carbonintensity.org.uk/regional/intensity/"
              f"2025-01-01T00:00Z/2025-01-02T00:00Z/regionid/{region_id}")
    return ImportedTrace(TraceKind.CARBON, "gCO2/kWh", source,
                         "NESO Carbon Intensity API, CC BY 4.0; attribution required",
                         "test", start, "none", "reject", region, 1800,
                         tuple(TracePoint(start + timedelta(minutes=30 * i), value)
                               for i, value in enumerate(values)))


class CarbonSignalReplayTests(unittest.TestCase):
    def test_keeps_noncarbon_inputs_modeled_and_never_selects_prohibited_node(self):
        result = evaluate(trace("north", [0] * 48), trace("london", [100] * 48), load_scenario(SCENARIO))
        self.assertEqual(result["opportunities"], 48)
        self.assertEqual(result["hard_prohibited_choices"], 0)
        self.assertIn("risk", result["modeled_inputs"])
        self.assertEqual(len(result["rows"]), 48)

    def test_rejects_unaligned_or_noncarbon_series(self):
        north, london = trace("north", [0] * 48), trace("london", [100] * 48)
        shifted = replace(london, points=tuple(replace(p, observed_utc=p.observed_utc + timedelta(minutes=30))
                                                for p in london.points))
        with self.assertRaisesRegex(ValueError, "missing or irregular"):
            evaluate(north, shifted, load_scenario(SCENARIO))
        with self.assertRaisesRegex(ValueError, "carbon-intensity"):
            evaluate(replace(north, kind=TraceKind.TRAFFIC), london, load_scenario(SCENARIO))


if __name__ == "__main__":
    unittest.main()
