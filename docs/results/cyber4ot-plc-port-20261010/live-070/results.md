# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 5 | 0 | 0.907403 | 0.000000 | 57.923005 |
| reactive_threshold | 5 | 0 | 0.952542 | 0.000000 | 0.407334 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.045139 Mbps (n=5; interval=[-0.04711012699493204, -0.04316779830213437]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 101 | 0/5233 | 0/5229 |
| reactive_threshold / 101 | 0/5437 | 12/5462 |
| full_proposed_controller / 103 | 0/5233 | 0/5233 |
| reactive_threshold / 103 | 0/5410 | 15/5455 |
| full_proposed_controller / 83 | 0/5234 | 0/5234 |
| reactive_threshold / 83 | 0/5410 | 15/5471 |
| full_proposed_controller / 89 | 0/5231 | 0/5227 |
| reactive_threshold / 89 | 0/5418 | 12/5501 |
| full_proposed_controller / 97 | 0/5236 | 0/5237 |
| reactive_threshold / 97 | 0/5432 | 12/5547 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_proposed_controller / 101 | unmeasured |
| reactive_threshold / 101 | 0.300512 |
| full_proposed_controller / 103 | unmeasured |
| reactive_threshold / 103 | 0.477666 |
| full_proposed_controller / 83 | unmeasured |
| reactive_threshold / 83 | 0.512946 |
| full_proposed_controller / 89 | unmeasured |
| reactive_threshold / 89 | 0.300612 |
| full_proposed_controller / 97 | unmeasured |
| reactive_threshold / 97 | 0.300554 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
