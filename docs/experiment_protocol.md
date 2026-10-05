# Experiment Protocol

## Design freeze

Final primary outcomes, scenario ranges, practical-significance margins, exclusions, sample sizes, and statistical tests must be committed before held-out final runs. Pilot runs may estimate variance but must be labeled and excluded from confirmatory results.

## Policies

All policies consume the same timestamped scenario stream and run under the same resource constraints:

1. static/no migration;
2. reactive threshold;
3. prediction-only;
4. uncertainty-aware without carbon/risk;
5. carbon-unaware and risk-unaware variants;
6. cold/naive migration;
7. fixed benefit threshold;
8. full proposed controller.

## Scenario families

- steady, bursty, trending, flash-crowd, and out-of-distribution workloads;
- mixed short/long flows and varying state sizes;
- stable and volatile carbon traces;
- step and transient risk changes;
- telemetry loss/staleness;
- target health, policy, capacity, and state-sync failures;
- simultaneous load, carbon, and risk pressure.

## Repetition and analysis

- Use identical seeds and inputs for paired policy comparisons.
- Retain warm-up data and record any rule used to exclude it.
- Save raw per-run events and mark interrupted/failed runs.
- Report sample size, mean/median as appropriate, dispersion, 95% confidence intervals, and effect sizes.
- Prefer paired bootstrap intervals or a justified paired test for paired outcomes.
- Correct or clearly label families of multiple comparisons.
- Publish negative and trade-off results.

## Data boundary

Synthetic workloads, carbon traces, and risk events must be labeled synthetic. External data requires source, version, license, checksum, preprocessing, and limitations. Estimated carbon is not physical power measurement.

