# Modeled sensitivity audit

The deterministic grid varies interval width, state size, operational benefit, one candidate's carbon intensity and that candidate's soft risk score. Three values per axis yield 243 identical input opportunities for each of nine policies. Input hashes prove pairing. The target is already warm and synchronized in the base scenario.

```sh
PYTHONPATH=src python3 -m vfw_research.sensitivity configs/scenarios/synthetic_small.json artifacts/raw/reviewer-sensitivity --summary-output artifacts/processed/reviewer-sensitivity
```

This is structural sensitivity testing, not measured performance, temporal migration frequency, physical emissions or attack reduction. State size affects the modeled threshold but does not allocate matching live conntrack state. Carbon/risk ranking inputs change independently of supplied benefit credits; this deliberately exposes the separation between those components and is not a calibrated utility model.

The generated summary also compares candidate preferences on identical input hashes. A selected candidate may accompany `WAIT`; count differences as placement decisions, not executed migrations. The 2026-10-10 grid found 81/243 changed candidate choices after removing carbon and 27/243 after removing soft risk. The prohibited node was never selected. See `results/sensitivity-20261010-placement-v3/`.

All variants retain the same hard risk ceiling and quarantine restriction. Removing a soft risk weight is not permission to select an unsafe node. Ablations renormalize the scenario's actual remaining weights rather than substitute hard-coded defaults. An all-removed weight vector is rejected.

Grid outcomes may be equal across policies; no additional favorable cases are selected after viewing results. Fixed/adaptive decision differences show rule sensitivity, not that either policy is better. Forecast horizon, traffic mix, long-flow fraction, threshold coefficient estimation and sensitivity of a complete time-evolving lifecycle remain separate research requirements.
