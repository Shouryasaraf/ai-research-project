# Live pilot results

Generated from immutable trial records; not a confirmatory study.

| Policy | Completed | Failed | Mean goodput (Mbps) | Mean request failure fraction | Mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| carbon_unaware | 3 | 0 | 1.134407 | 0.000000 | 75.204655 |
| cold_migration | 3 | 0 | 0.248467 | 0.013275 | 79.054630 |
| fixed_benefit_threshold | 3 | 0 | 1.134643 | 0.000000 | 75.078492 |
| full_proposed_controller | 3 | 0 | 1.135180 | 0.000000 | 75.079204 |
| prediction_only | 3 | 0 | 1.134405 | 0.000000 | 75.066335 |
| reactive_threshold | 3 | 0 | 1.172438 | 0.000000 | 15.966444 |
| risk_unaware | 3 | 0 | 1.134338 | 0.000000 | 75.176470 |
| static_no_migration | 3 | 0 | 0.865494 | 0.000000 | 77.215533 |
| uncertainty_without_carbon_or_risk | 3 | 0 | 1.135759 | 0.000000 | 75.124779 |

## Paired goodput differences

Positive values favor the full controller. Three-seed bootstrap intervals are descriptive only.

- Versus carbon_unaware: 0.000773 Mbps (n=3; interval=[-0.0019421080586732309, 0.002830147760798374]).
- Versus cold_migration: 0.886713 Mbps (n=3; interval=[0.8847915059710587, 0.887913326731109]).
- Versus fixed_benefit_threshold: 0.000537 Mbps (n=3; interval=[-0.0008506700206567519, 0.0018138466772790185]).
- Versus prediction_only: 0.000775 Mbps (n=3; interval=[-0.0020273539911424, 0.0023516606001841023]).
- Versus reactive_threshold: -0.037258 Mbps (n=3; interval=[-0.04055516115841651, -0.034617459777257276]).
- Versus risk_unaware: 0.000842 Mbps (n=3; interval=[-0.0007287151585464446, 0.0024065579694823036]).
- Versus static_no_migration: 0.269687 Mbps (n=3; interval=[0.2683329491291435, 0.2711190993657524]).
- Versus uncertainty_without_carbon_or_risk: -0.000578 Mbps (n=3; interval=[-0.001845196859613818, 0.0003153129331696647]).

## Limits

- No packet capture: packet loss is unmeasured.
- Response gaps include intentional pacing and are not downtime.
- One alternate target cannot isolate placement-quality effects.
- Carbon/risk are modeled and not physical observations.
- RTT summarizes successful requests only; failures must be read alongside it.
- Repeated external-trace trials reuse one trace segment and are not independent workloads.
