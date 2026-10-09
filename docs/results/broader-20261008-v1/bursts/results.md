# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| full_proposed_controller | 1 | 0 | 0.930220 | 0.000000 | 77.051277 |
| reactive_threshold | 1 | 0 | 0.959192 | 0.000000 | 76.663911 |

## Paired goodput differences

Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.

- Versus reactive_threshold: -0.028972 Mbps (n=1; interval=None).

## Limits

- No packet capture: packet loss is unmeasured.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
