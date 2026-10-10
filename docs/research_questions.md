# Research Questions and Original Hypotheses

These are the original intended hypotheses, **not a registered confirmatory protocol**. Development results already challenged H1: the original full policy underperformed reactive control on each of three preselected Cyber4OT PLC-port traces because its fixed uncertainty gate never permitted a route commit. The post-result liveness guard is a separate exploratory policy. A new independent confirmation must freeze the precise policy version, unseen workload selection, primary endpoints, practical margins, number of independent workload units and repetitions, exclusions, analysis and stopping rules **before** collecting that batch. Do not reuse inspected traces as unseen confirmation or relabel existing pilots as preregistered evidence. See `publication_claim_ledger.md` and `manuscript_draft.md`.

## RQ1 — Uncertainty gating

Does calibrated uncertainty gating reduce unnecessary or harmful migrations compared with prediction-only migration?

**H1 (original, unconfirmed):** Across paired workload scenarios, the full uncertainty-gated policy reduces unnecessary migrations without increasing SLA-violation duration beyond a prospectively fixed non-inferiority margin. The PLC-port development result contradicts any general service-improvement reading of this hypothesis.

## RQ2 — Stateful warm migration

Does warm state synchronization with flow pinning reduce disruption compared with cold/naive migration?

**H2 (original, unconfirmed):** Warm migration lowers established-flow reset/disruption rate and traffic-switching interruption under equal workloads and resource limits. Bounded completed-request continuity does not yet measure exact interruption or complete TCP-state equivalence.

## RQ3 — Carbon and attack risk

Does carbon- and attack-risk-aware placement reduce modeled emissions and risky-node exposure without unacceptable service degradation?

**H3 (original, unconfirmed):** The full placement policy reduces both carbon-intensity exposure and time on risky nodes while remaining within prospectively fixed latency and SLA bounds. Existing carbon/risk outcomes are candidate-choice proxies, not measured emissions or attacks.

## RQ4 — Adaptive threshold

Does a contextual migration-benefit threshold outperform a fixed threshold across workload, state-size, and risk regimes?

**H4 (original, unconfirmed):** The adaptive threshold produces higher realized net benefit and fewer harmful migrations over the full scenario suite. Current modeled scores are not realized net benefit.

## RQ5 — Security fallback

Can invariant validation prevent unsafe traffic commits and restore a validated configuration after controlled failures?

**H5 (original, partially exercised):** All injected invariant violations prevent commit; fallback success and recovery time are reported with confidence intervals. Existing tests cover selected faults and bounded active-flow failback, not general host failure or arbitrary state loss.

