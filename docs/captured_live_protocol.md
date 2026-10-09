# Paired captured migration development pilot

Frozen before the three-seed batch on 2026-10-10. This is a development pilot, not an independent confirmatory study. The earlier single-seed batch (`live-captured-pair-20261010-v1`) was viewed before this protocol and remains separate.

- Policies: full proposed controller and reactive threshold, identical seeded synthetic step schedule, seed values 47, 53 and 59. Run order is shuffled from each seed by the existing batch runner. Three persistent TCP echo flows, 12 one-second intervals, source 1 Mbps and target 3 Mbps shaped paths.
- Raw outcomes: successful request goodput, failures and p95 request RTT; actual route commit count; paired endpoint packet-instance deficits in each direction. Capture starts before connections and ends after workload completion plus a two-second tail. Exact outage duration is not measured.
- Validity: both captures must close cleanly, report zero capture-kernel drops, have no receiver-only unmatched packet instances, match recorded SHA-256 values and be recomputable from the saved PCAPs. A failed, partial or uncaptured trial is retained as a failed attempt; it is never silently excluded.
- Comparison: report both policies and all seeds, including negative results. Compute descriptive paired goodput differences and list packet deficits as counts over sent instances. Do not infer a universal loss rate from three repetitions or select a policy based on these pilot outcomes.
- Inputs: carbon, risk and candidate headroom are modeled. The generated traffic is synthetic. The capture methodology was separately checked against ordinary and deliberate-drop controls in `results/packet-validation-20261010/`.

Run from the repository root in the isolated Linux environment:

```sh
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/live-captured-pair-new --seeds 47 53 59 --policies full_proposed_controller reactive_threshold --steps 12 --flows 3 --capture
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/live-captured-pair-new artifacts/processed/live-captured-pair-new
```
