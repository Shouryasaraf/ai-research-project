# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 5 | 0 | 0.885515 | 0.000000 | 51.612264 |
| reactive_threshold | 5 | 0 | 0.890776 | 0.000000 | 0.400744 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.005261 Mbps (n=5; interval=[-0.005564522626082891, -0.004919039463341046]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 101 | 0/5437 | 0/5456 |
| reactive_threshold / 101 | 0/5373 | 15/5447 |
| full_proposed_controller / 103 | 0/5436 | 0/5466 |
| reactive_threshold / 103 | 0/5373 | 15/5462 |
| full_proposed_controller / 83 | 0/5433 | 0/5472 |
| reactive_threshold / 83 | 0/5373 | 15/5450 |
| full_proposed_controller / 89 | 0/5443 | 0/5469 |
| reactive_threshold / 89 | 0/5373 | 15/5472 |
| full_proposed_controller / 97 | 0/5442 | 0/5458 |
| reactive_threshold / 97 | 0/5373 | 15/5468 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_proposed_controller / 101 | unmeasured |
| reactive_threshold / 101 | 0.415460 |
| full_proposed_controller / 103 | unmeasured |
| reactive_threshold / 103 | 0.415801 |
| full_proposed_controller / 83 | unmeasured |
| reactive_threshold / 83 | 0.408629 |
| full_proposed_controller / 89 | unmeasured |
| reactive_threshold / 89 | 0.414032 |
| full_proposed_controller / 97 | unmeasured |
| reactive_threshold / 97 | 0.409261 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
