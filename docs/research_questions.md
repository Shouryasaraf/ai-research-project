# Research Questions and Preregistered Hypotheses

These statements are fixed before final experiments. Thresholds for practical significance must be finalized after pilot variance estimates and before the held-out final runs.

## RQ1 — Uncertainty gating

Does calibrated uncertainty gating reduce unnecessary or harmful migrations compared with prediction-only migration?

**H1:** Across paired workload scenarios, the full uncertainty-gated policy reduces unnecessary migrations and does not increase SLA-violation duration beyond the preregistered non-inferiority margin.

## RQ2 — Stateful warm migration

Does warm state synchronization with flow pinning reduce disruption compared with cold/naive migration?

**H2:** Warm migration lowers established-flow reset/disruption rate and traffic-switching interruption under equal workloads and resource limits.

## RQ3 — Carbon and attack risk

Does carbon- and attack-risk-aware placement reduce modeled emissions and risky-node exposure without unacceptable service degradation?

**H3:** The full placement policy reduces both carbon-intensity exposure and time on risky nodes while remaining within preregistered latency and SLA bounds.

## RQ4 — Adaptive threshold

Does a contextual migration-benefit threshold outperform a fixed threshold across workload, state-size, and risk regimes?

**H4:** The adaptive threshold produces higher realized net benefit and fewer harmful migrations over the full scenario suite.

## RQ5 — Security fallback

Can invariant validation prevent unsafe traffic commits and restore a validated configuration after controlled failures?

**H5:** All injected invariant violations prevent commit; fallback success and recovery time are reported with confidence intervals.

