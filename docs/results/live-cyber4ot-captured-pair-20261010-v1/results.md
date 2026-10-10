# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 5 | 0 | 0.975867 | 0.000000 | 0.521668 |
| reactive_threshold | 5 | 0 | 0.974459 | 0.000000 | 0.508932 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus reactive_threshold: 0.001408 Mbps (n=5; interval=[-0.001321060557863718, 0.0033360386613427774]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_proposed_controller / 61 | 0/5425 | 9/5501 |
| reactive_threshold / 61 | 0/5409 | 0/5556 |
| full_proposed_controller / 67 | 0/5426 | 9/5422 |
| reactive_threshold / 67 | 0/5372 | 15/5504 |
| full_proposed_controller / 71 | 0/5424 | 9/5424 |
| reactive_threshold / 71 | 0/5377 | 16/5423 |
| full_proposed_controller / 73 | 0/5421 | 6/5425 |
| reactive_threshold / 73 | 0/5373 | 15/5483 |
| full_proposed_controller / 79 | 0/5421 | 9/5422 |
| reactive_threshold / 79 | 0/5372 | 15/5425 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_proposed_controller / 61 | 0.335997 |
| reactive_threshold / 61 | 0.300735 |
| full_proposed_controller / 67 | 0.344175 |
| reactive_threshold / 67 | 0.414068 |
| full_proposed_controller / 71 | 0.337686 |
| reactive_threshold / 71 | 0.467371 |
| full_proposed_controller / 73 | 0.320074 |
| reactive_threshold / 73 | 0.464138 |
| full_proposed_controller / 79 | 0.388144 |
| reactive_threshold / 79 | 0.417885 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
