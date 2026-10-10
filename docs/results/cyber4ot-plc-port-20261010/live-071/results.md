# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 5 | 0 | 0.906875 | 0.000000 | 54.970909 |
| reactive_threshold | 5 | 0 | 0.946482 | 0.000000 | 0.418598 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.039607 Mbps (n=5; interval=[-0.041601349295507406, -0.03746436613332656]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 101 | 0/5238 | 0/5238 |
| reactive_threshold / 101 | 0/5429 | 18/5429 |
| full_proposed_controller / 103 | 0/5235 | 0/5232 |
| reactive_threshold / 103 | 0/5386 | 15/5431 |
| full_proposed_controller / 83 | 0/5240 | 0/5237 |
| reactive_threshold / 83 | 0/5408 | 15/5418 |
| full_proposed_controller / 89 | 0/5241 | 0/5242 |
| reactive_threshold / 89 | 0/5396 | 17/5396 |
| full_proposed_controller / 97 | 0/5237 | 0/5238 |
| reactive_threshold / 97 | 0/5418 | 8/5426 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_proposed_controller / 101 | unmeasured |
| reactive_threshold / 101 | 0.466378 |
| full_proposed_controller / 103 | unmeasured |
| reactive_threshold / 103 | 0.500561 |
| full_proposed_controller / 83 | unmeasured |
| reactive_threshold / 83 | 0.502915 |
| full_proposed_controller / 89 | unmeasured |
| reactive_threshold / 89 | 0.493630 |
| full_proposed_controller / 97 | unmeasured |
| reactive_threshold / 97 | 0.470813 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
