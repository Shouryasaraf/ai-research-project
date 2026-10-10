# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_liveness_guarded_experimental | 5 | 0 | 0.946494 | 0.000000 | 51.629409 |
| full_proposed_controller | 5 | 0 | 0.907485 | 0.000000 | 57.910978 |
| reactive_threshold | 5 | 0 | 0.950008 | 0.000000 | 0.743312 |

## Paired goodput differences

Positive values favor the full controller. Paired bootstrap intervals are descriptive only.

- Versus full_liveness_guarded_experimental: -0.039009 Mbps (n=5; interval=[-0.04065496168389189, -0.037363401789180295]).
- Versus reactive_threshold: -0.042523 Mbps (n=5; interval=[-0.04587117116561266, -0.03913096945804857]).

## Captured endpoint packet-instance deficits

| Policy / seed | Forward missing/sent | Reverse missing/sent |
|---|---:|---:|
| full_liveness_guarded_experimental / 101 | 0/5383 | 10/5419 |
| full_proposed_controller / 101 | 0/5232 | 0/5228 |
| reactive_threshold / 101 | 0/5437 | 13/5536 |
| full_liveness_guarded_experimental / 103 | 0/5411 | 6/5439 |
| full_proposed_controller / 103 | 0/5235 | 0/5234 |
| reactive_threshold / 103 | 0/5434 | 10/5482 |
| full_liveness_guarded_experimental / 83 | 0/5402 | 9/5403 |
| full_proposed_controller / 83 | 0/5230 | 0/5229 |
| reactive_threshold / 83 | 0/5419 | 17/5449 |
| full_liveness_guarded_experimental / 89 | 0/5391 | 10/5420 |
| full_proposed_controller / 89 | 0/5228 | 0/5228 |
| reactive_threshold / 89 | 0/5387 | 16/5413 |
| full_liveness_guarded_experimental / 97 | 0/5408 | 9/5408 |
| full_proposed_controller / 97 | 0/5233 | 0/5232 |
| reactive_threshold / 97 | 0/5382 | 17/5399 |

## Transition-bracketing response gaps

Largest same-flow gap from the last successful response before transition start to the first after transition end. Includes deliberate pacing and synchronization; this is not exact migration downtime.

| Policy / seed | Gap (s) |
|---|---:|
| full_liveness_guarded_experimental / 101 | 0.611920 |
| full_proposed_controller / 101 | unmeasured |
| reactive_threshold / 101 | 0.396659 |
| full_liveness_guarded_experimental / 103 | 0.324702 |
| full_proposed_controller / 103 | unmeasured |
| reactive_threshold / 103 | 0.350865 |
| full_liveness_guarded_experimental / 83 | 0.524358 |
| full_proposed_controller / 83 | unmeasured |
| reactive_threshold / 83 | 0.543960 |
| full_liveness_guarded_experimental / 89 | 0.551004 |
| full_proposed_controller / 89 | unmeasured |
| reactive_threshold / 89 | 0.548738 |
| full_liveness_guarded_experimental / 97 | 0.528279 |
| full_proposed_controller / 97 | unmeasured |
| reactive_threshold / 97 | 0.560987 |

## Limits

- Observed packet-instance deficits are between two lab capture points, not a universal loss rate.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
