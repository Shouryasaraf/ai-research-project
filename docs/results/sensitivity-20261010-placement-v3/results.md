# Modeled sensitivity audit

No traffic, power or attack outcomes are measured.

| Policy | Opportunities | COMMIT | WAIT | PREWARM | Other |
|---|---:|---:|---:|---:|---:|
| static_no_migration | 243 | 0 | 243 | 0 | 0 |
| reactive_threshold | 243 | 243 | 0 | 0 | 0 |
| prediction_only | 243 | 243 | 0 | 0 | 0 |
| uncertainty_without_carbon_or_risk | 243 | 90 | 153 | 0 | 0 |
| risk_unaware | 243 | 90 | 153 | 0 | 0 |
| carbon_unaware | 243 | 90 | 153 | 0 | 0 |
| cold_migration | 243 | 90 | 153 | 0 | 0 |
| fixed_benefit_threshold | 243 | 108 | 135 | 0 | 0 |
| full_proposed_controller | 243 | 90 | 153 | 0 | 0 |

All policies retained the same hard risk ceiling and quarantine constraints.
These are decision counts, not migration frequency in a time-evolving system.
Carbon/risk candidate scores vary; benefit credits remain independently modeled inputs.
Raw records SHA-256: d27be9e60586930e67500d7cd5f2c34dd0a5d07c6f33cf8502b39ab06de1412c

## Modeled candidate preferences

Candidate selections are recorded even for WAIT decisions; they are not deployments or measured emissions.

| Policy | Candidate counts | Mean selected carbon input (gCO2/kWh) | Mean selected risk input |
|---|---|---:|---:|
| static_no_migration | {'none': 243} | n/a | n/a |
| reactive_threshold | {'node-green': 81, 'node-low-latency': 162} | 268.889 | 0.136 |
| prediction_only | {'node-green': 81, 'node-low-latency': 162} | 268.889 | 0.136 |
| uncertainty_without_carbon_or_risk | {'node-low-latency': 243} | 340.000 | 0.120 |
| risk_unaware | {'node-green': 108, 'node-low-latency': 135} | 264.444 | 0.167 |
| carbon_unaware | {'node-low-latency': 243} | 340.000 | 0.120 |
| cold_migration | {'node-green': 81, 'node-low-latency': 162} | 268.889 | 0.136 |
| fixed_benefit_threshold | {'node-green': 81, 'node-low-latency': 162} | 268.889 | 0.136 |
| full_proposed_controller | {'node-green': 81, 'node-low-latency': 162} | 268.889 | 0.136 |

| Full compared with | Different candidate choices | Full lower carbon input | Full lower risk input |
|---|---:|---:|---:|
| carbon_unaware | 81 | 81 | 54 |
| risk_unaware | 27 | 0 | 27 |
| uncertainty_without_carbon_or_risk | 81 | 81 | 54 |

The prohibited node is never selected. These synthetic inputs do not quantify physical carbon or attack reduction.
