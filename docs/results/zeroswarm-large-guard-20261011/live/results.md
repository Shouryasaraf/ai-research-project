# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_liveness_guarded_experimental | 5 | 0 | 0.952018 | 0.000000 | 0.917407 |
| full_proposed_controller | 5 | 0 | 0.952592 | 0.000000 | 0.874408 |
| reactive_threshold | 5 | 0 | 0.952738 | 0.000000 | 0.717686 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus full_liveness_guarded_experimental: 0.000575 Mbps (n=5; interval=[-0.0010751859235410555, 0.002333852248127921]).
- Versus reactive_threshold: -0.000145 Mbps (n=5; interval=[-0.0019880544656827983, 0.0016973619421961183]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_liveness_guarded_experimental / 137 | 0/5400 | 11/5425 |
| full_proposed_controller / 137 | 0/5411 | 9/5414 |
| reactive_threshold / 137 | 0/5412 | 13/5452 |
| full_liveness_guarded_experimental / 139 | 0/5421 | 9/5416 |
| full_proposed_controller / 139 | 0/5403 | 10/5423 |
| reactive_threshold / 139 | 0/5406 | 17/5417 |
| full_liveness_guarded_experimental / 149 | 0/5419 | 9/5423 |
| full_proposed_controller / 149 | 0/5410 | 9/5415 |
| reactive_threshold / 149 | 0/5399 | 14/5427 |
| full_liveness_guarded_experimental / 151 | 0/5405 | 10/5408 |
| full_proposed_controller / 151 | 0/5419 | 9/5424 |
| reactive_threshold / 151 | 0/5399 | 15/5419 |
| full_liveness_guarded_experimental / 157 | 0/5397 | 10/5425 |
| full_proposed_controller / 157 | 0/5397 | 10/5422 |
| reactive_threshold / 157 | 0/5423 | 14/5444 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_liveness_guarded_experimental / 137 | 0.607671 |
| full_proposed_controller / 137 | 0.529076 |
| reactive_threshold / 137 | 0.545811 |
| full_liveness_guarded_experimental / 139 | 0.523447 |
| full_proposed_controller / 139 | 0.548721 |
| reactive_threshold / 139 | 0.566164 |
| full_liveness_guarded_experimental / 149 | 0.523406 |
| full_proposed_controller / 149 | 0.474964 |
| reactive_threshold / 149 | 0.570806 |
| full_liveness_guarded_experimental / 151 | 0.665053 |
| full_proposed_controller / 151 | 0.476910 |
| reactive_threshold / 151 | 0.580258 |
| full_liveness_guarded_experimental / 157 | 0.624299 |
| full_proposed_controller / 157 | 0.600167 |
| reactive_threshold / 157 | 0.608005 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
