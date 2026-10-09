# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| cold_migration | 3 | 0 | 0.839446 | 0.000000 | 0.729701 |
| full_proposed_controller | 3 | 0 | 0.839678 | 0.000000 | 0.660525 |
| reactive_threshold | 3 | 0 | 0.839975 | 0.000000 | 0.653134 |
| static_no_migration | 3 | 0 | 0.839777 | 0.000000 | 0.684836 |

## Paired goodput differences

Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.

- Versus cold_migration: 0.000232 Mbps (n=3; interval=[-0.00041534764668027524, 0.0008108111186034828]).
- Versus reactive_threshold: -0.000296 Mbps (n=3; interval=[-0.0012911920819660416, 0.0003118770357334322]).
- Versus static_no_migration: -0.000098 Mbps (n=3; interval=[-0.0003595411290475692, 0.00017528680317380196]).

## Limits

- No packet capture: packet loss is unmeasured.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
