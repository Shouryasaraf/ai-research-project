# Data and Trace Provenance

## Current synthetic fixture

| Field | Value |
|---|---|
| Configuration | `configs/scenarios/synthetic_small.json` |
| Scenario ID | `synthetic-small-overload` |
| Origin | Deterministic project-authored synthetic fixture |
| Seeds | 7, 11, 19 |
| Workload values | Synthetic Mbps forecast with bounded seeded jitter |
| Carbon values | Synthetic node attributes in gCO2/kWh |
| Security-risk values | Synthetic dimensionless scores in [0, 1] |
| Labels | No external labels |
| Intended use | CI, schema validation, policy-interface parity and analysis-pipeline smoke testing |
| Prohibited interpretation | Real workload, physical energy, measured emissions, observed attack probability, network performance, or publication comparison |

The complete JSON configuration is hashed with canonical key ordering. Every run record stores that SHA-256 digest, seed, environment, scenario ID and an explicit synthetic-input flag.

## External data

No external workload, carbon, vulnerability, anomaly or attack dataset has been incorporated yet. Before adding one, record its stable source, version/date, license or terms, acquisition checksum, fields used, time resolution, timezone, preprocessing, missing-data policy, label limitations and redistribution constraints. Network downloads must not be required for unit tests.

The offline CSV adapter in `src/vfw_research/trace_adapter.py` enforces a minimal sidecar and strict UTC/unit/checksum/time-series validation; see `external_trace_contract.md`. It does not certify licensing or prove that any real trace has been evaluated.

`dataset_candidate_screen.md` lists source-owner pages considered for future work. None has been adopted or downloaded.

## Synthetic forecast families

`src/vfw_research/workloads.py` deterministically generates five one-minute traffic-rate families: steady, periodic bursts, gradual trend, a short flash crowd, and a step change confined to the held-out test segment. Each value is a synthetic Mbps rate and is never represented as measured packet traffic. The family, seed, length, trace SHA-256, split counts and runtime are saved by `vfw_research.forecast_evaluation`. The evaluation observes a real next value before updating the model's point state; it does not create labels from its own forecasts. The conformal radius stays fixed after calibration.

`vfw_research.forecast_batch` writes separate exclusive-write records for every declared family/seed pair and a derived summary. The 2026-10-07 pilot used all five families and seeds 0–9 (50 records, 240 observations each). It is a descriptive synthetic pilot, not a confirmatory comparison or a real workload trace.
