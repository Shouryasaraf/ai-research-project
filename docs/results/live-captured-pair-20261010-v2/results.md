# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 3 | 0 | 1.093041 | 0.000000 | 76.989850 |
| reactive_threshold | 3 | 0 | 1.160598 | 0.000000 | 74.390398 |

## Paired goodput differences

Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.067557 Mbps (n=3; interval=[-0.08315815291042394, -0.04018862305325288]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 47 | 0/1973 | 8/1856 |
| reactive_threshold / 47 | 0/2136 | 8/2008 |
| full_proposed_controller / 53 | 0/2212 | 8/2066 |
| reactive_threshold / 53 | 0/2378 | 8/2226 |
| full_proposed_controller / 59 | 0/2240 | 8/2101 |
| reactive_threshold / 59 | 0/2316 | 8/2188 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
