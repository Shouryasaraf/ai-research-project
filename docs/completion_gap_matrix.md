# Completion Gap Matrix

This matrix was refreshed from the repository on 2026-10-06. “Implemented” means code exists; “verified” is used only when the listed evidence was actually observed.

| Requirement | Current component/evidence | Missing implementation | Missing experiment | Acceptance gate | Paper artifact |
|---|---|---|---|---|---|
| Reproducible non-privileged pipeline | 41 unit tests; scenario validation; nine-policy paired runner; immutable records; JSON/CSV/SVG regeneration; CI workflow | Cross-platform task wrapper and dependency lock if dependencies are added | CI must run on GitHub after push | Gate A partial | Artifact appendix and environment manifest |
| Executable packet path | Namespace/nftables smoke evidence recorded in `verification_log.md` | Optional container/OVS packaging | Fresh privileged reproduction | Gate A/Stage 2 | Testbed description |
| Integrated scaling/load balancing | Core managers and proxy-affinity smoke evidence | Wire scaling actions to repeatable multi-vFW lifecycle and telemetry | Repeated scale-out/in, fairness, loss and anti-flapping trials | Gate B | F1/F3 results |
| Level 2 migration | Kernel tuple insertion, supported-field comparison, plus separate normalized nftables policy-equivalence and target-health pre-commit checks | Combine state and policy checks for the same path and reject mismatches before selection | Repeated success plus state mismatch/timeout trials | Gate C Level 2 | State transfer table |
| Level 3 warm transition | Proxy-based source pin/new-target flow, application drain timing and new-flow fallback smoke | Transparent route/flow transition, restart-safe rollback and packet capture | Established/new-flow continuity, loss, reset and recovery trials | Gate C Level 3 | F4 comparison |
| Unified telemetry | Typed unit-validated telemetry snapshot, explicit freshness gate, live timestamped interface/conntrack snapshots from two vFW namespaces, and a validated controller-side parser | Feed live snapshots into controller decisions and immutable records; add CPU, memory, loss, latency and freshness evaluation | Fresh/stale real-telemetry experiments | Gate D | Measurement methodology |
| Forecasting/calibration | Rolling-mean split-conformal baseline and unit tests | Trace adapters and at least one justified comparator | Held-out chronological accuracy/calibration and shift experiments | Gate E | F5 figures |
| Carbon/risk provenance | Explainable models and units exist | Machine-readable trace provenance and sensitivity ranges | Paired placement trade-off experiments | Gate F | F2 objective plots |
| Adaptive benefit | Auditable formula and boundary tests | Full units/ranges registry and parameter-grid runner | Fixed-versus-adaptive paired sensitivity experiments | Gate G | F6 results |
| Invariants/fallback | Core validation, logical fallback, one smoke observation | Real route restoration and restart handling | Repeated fault injection with recovery intervals | Gate H | F7 safety table |
| Comparative evaluation | Nine policies share one interface; 27-record synthetic pilot executed | Multi-scenario orchestration, checkpoint/resume and full metric capture | Repeated packet-path baselines/ablations with preregistered statistics | Gate I | Main results tables |
| Prior art/novelty | Proposed contributions identified | Verified primary-source search and comparison matrix | Not applicable | Gate J | Related work and claim boundary |
| Publication package | Architecture, protocol, metrics and limitations drafts | Generated research plots/tables, validity analysis, artifact guide and paper draft | Only after confirmatory evidence | Final | Submission package |

## Immediate dependency order

1. Preserve the non-privileged experiment pipeline as the controller/evaluation reference.
2. Add a real timestamped telemetry schema and connect it to the dual-vFW testbed.
3. Complete Level 2 policy/state validation before any route commit.
4. Complete Level 3 source-pinned draining and target admission, then measure it repeatedly.
5. Use those measurements in the unified runner before drawing comparative conclusions.

The generated `pilot-20261006-v1` artifacts are deliberately excluded from research conclusions: they validate plumbing with synthetic controller inputs and do not measure a packet path.
