# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 3 | 0 | 0.834172 | 0.000000 | 0.472455 |
| reactive_threshold | 3 | 0 | 0.834740 | 0.000000 | 0.529917 |

## Paired goodput differences

Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.000568 Mbps (n=3; interval=[-0.0011245243819066886, -0.00012854348764013146]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 47 | 0/2141 | 15/2149 |
| reactive_threshold / 47 | 0/2142 | 15/2156 |
| full_proposed_controller / 53 | 0/2140 | 15/2144 |
| reactive_threshold / 53 | 0/2142 | 15/2161 |
| full_proposed_controller / 59 | 0/2142 | 15/2153 |
| reactive_threshold / 59 | 0/2141 | 15/2153 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
