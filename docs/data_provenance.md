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
