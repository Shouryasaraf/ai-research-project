# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 5 | 0 | 0.922939 | 0.000000 | 0.597349 |
| reactive_threshold | 5 | 0 | 0.918691 | 0.000000 | 0.557152 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus reactive_threshold: 0.004248 Mbps (n=5; interval=[0.0015178024712845684, 0.006294847145474259]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 107 | 0/5410 | 10/5493 |
| reactive_threshold / 107 | 0/5364 | 15/5473 |
| full_proposed_controller / 109 | 0/5434 | 11/5507 |
| reactive_threshold / 109 | 0/5380 | 15/5422 |
| full_proposed_controller / 113 | 0/5375 | 16/5488 |
| reactive_threshold / 113 | 0/5386 | 15/5429 |
| full_proposed_controller / 127 | 0/5434 | 6/5489 |
| reactive_threshold / 127 | 0/5364 | 15/5451 |
| full_proposed_controller / 131 | 0/5410 | 14/5463 |
| reactive_threshold / 131 | 0/5371 | 15/5461 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_proposed_controller / 107 | 0.350928 |
| reactive_threshold / 107 | 0.461278 |
| full_proposed_controller / 109 | 0.351168 |
| reactive_threshold / 109 | 0.454679 |
| full_proposed_controller / 113 | 0.472064 |
| reactive_threshold / 113 | 0.462609 |
| full_proposed_controller / 127 | 0.375264 |
| reactive_threshold / 127 | 0.508139 |
| full_proposed_controller / 131 | 0.567941 |
| reactive_threshold / 131 | 0.506512 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
