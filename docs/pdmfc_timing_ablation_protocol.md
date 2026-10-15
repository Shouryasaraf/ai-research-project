# Frozen secondary-segment fixed-timing ablation

This protocol must be committed before running the secondary segment. It is an **exploratory within-source timing decomposition**, not a new independent traffic source, not a replacement for the negative original-controller result, and not a causal estimate of all migration costs. The selected PDMFC file and chronological train/calibration/test split remain unchanged from `docs/pdmfc_confirmatory_protocol.md`. The first 30 held-out seconds have already been inspected; this protocol selects the **next 30 held-out seconds** (test offset 30, length 30) without examining their outcomes. The source trace contains 160 held-out seconds.

## Fixed arms and endpoint

- Five seeds: `311 313 317 331 337`, each using the same second 30-second segment and three persistent TCP flows; order shuffled per seed.
- Arms: unchanged `full_proposed_controller`, `reactive_threshold`, `full_liveness_guarded_experimental`, and the new `reactive_fixed_timing_warm_experimental` control.
- Fixed-timing reactive retains reactive overload trigger, selected target, telemetry and security checks. Once triggered, it waits until step 2, performs warm state sync at step 2, and commits no earlier than step 3 after sync; the runner re-syncs before commit, as with the guard. The steps 2 and 3 were chosen from already inspected *first-segment* guard behavior, not optimized on this second segment. If the trigger arrives too late or any prerequisite fails, it does not force a commit.
- Primary descriptive contrast: guard minus fixed-timing reactive completed-request goodput. Report each pair, mean, capture deficits, successful-request p95 RTT, decision actions/steps, sync counts and duration, commit counts, failed requests, RST and repeated payload sequences. Also report full-minus-reactive unchanged policy contrast. No unreported exclusions or outcome-based early stopping.
- Interpret only if both experimental arms commit at the same decision step and have matched sync count in each paired trial. Otherwise report the timing mismatch and do not call the comparison matched. Same source slice repeated across seeds is not independent workload replication; bootstrap intervals are descriptive only.
- Stop on infrastructure or safety failure, preserve failed attempt, and do not silently substitute another segment or tune parameters. Carbon/risk remain modeled, packet deficits are capture-point observations, and no physical cross-host migration is tested.

## Command on an authorized Linux lab host

From a clean checkout with the PDMFC derived rates and sidecar already generated locally:

```sh
bash scripts/independent_host_preflight.sh
PYTHONPATH=src python3 -m unittest discover -s tests -q
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/pdmfc-2025-v2-timing-ablation --seeds 311 313 317 331 337 --policies full_proposed_controller reactive_threshold full_liveness_guarded_experimental reactive_fixed_timing_warm_experimental --steps 30 --flows 3 --capture --trace-csv artifacts/raw/pdmfc-2025-v1/rates-1s.csv --provenance artifacts/raw/pdmfc-2025-v1/rates-1s.provenance.json --trace-test-offset 30
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/pdmfc-2025-v2-timing-ablation artifacts/processed/pdmfc-2025-v2-timing-ablation
```

The original PDMFC source PCAP and derived CSV remain private and Git-ignored. This arm is experimental and must never be relabeled as the original full controller.
