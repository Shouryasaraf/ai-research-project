# Completion Gap Matrix

This matrix was refreshed from the repository on 2026-10-06. “Implemented” means code exists; “verified” is used only when the listed evidence was actually observed.

| Requirement | Current component/evidence | Missing implementation | Missing experiment | Acceptance gate | Paper artifact |
|---|---|---|---|---|---|
| Reproducible non-privileged pipeline | 41 unit tests; scenario validation; nine-policy paired runner; immutable records; JSON/CSV/SVG regeneration; CI workflow | Cross-platform task wrapper and dependency lock if dependencies are added | CI must run on GitHub after push | Gate A partial | Artifact appendix and environment manifest |
| Executable packet path | Namespace/nftables smoke evidence recorded in `verification_log.md` | Optional container/OVS packaging | Fresh privileged reproduction | Gate A/Stage 2 | Testbed description |
| Integrated scaling/load balancing | Three live two-path runs verified telemetry-driven 1→2→1 firewall activation, least-utilized new-flow assignment and source-flow affinity | Generalize lifecycle beyond two paths and persistent controller recovery | Broader flow distributions, fairness, loss, SLA and anti-flapping trials | Gate B partial | F1/F3 results |
| Level 2 migration | Guarded proxy path plus six-namespace same-TCP-flow route lab: 9/9 route/fault trials and 3/3 controlled reverse-sync rollback trials | Integrate with controller, compare deeper TCP state, atomic/crash-safe rollback handling | Packet loss/interruption, multi-flow and broader failure trials | Gate C Level 2 partial | State transfer table |
| Level 3 warm transition | Proxy-based source pin/new-target flow, application drain timing and new-flow fallback smoke | Transparent route/flow transition, restart-safe rollback and packet capture | Established/new-flow continuity, loss, reset and recovery trials | Gate C Level 3 | F4 comparison |
| Unified telemetry | Typed unit-validated telemetry snapshot, explicit freshness gate, live timestamped interface/conntrack snapshots from two vFW namespaces, and a validated controller-side parser | Feed live snapshots into controller decisions and immutable records; add CPU, memory, loss, latency and freshness evaluation | Fresh/stale real-telemetry experiments | Gate D | Measurement methodology |
| Forecasting/calibration | Rolling-mean and EWMA conformal models; synthetic five-family pilot; strict imported-traffic path; one historical MAWI forecast and offline controller-decision pilot; exploratory adaptive residual model | Trace-derived traffic replay and live decisions; assess representative modern traces and calibrate gate on non-test data | Repeated confirmatory real-trace evaluation, packet-path outcomes and action sensitivity | Gate E partial | F5 figures |
| Carbon/risk provenance | Explainable models and units plus strict generic offline trace/sidecar adapter | Select and legally review actual trace; source-specific preprocessing and sensitivity ranges | Paired placement trade-off experiments | Gate F partial | F2 objective plots |
| Adaptive benefit | Auditable formula and boundary tests | Full units/ranges registry and parameter-grid runner | Fixed-versus-adaptive paired sensitivity experiments | Gate G | F6 results |
| Invariants/fallback | Explicit approved default-deny policy guard, live automatic new-flow restoration after target failure, fail-closed unsafe-source fault, and 12-trial functional batch | Proactive detection, established-target-flow recovery and restart handling | More repetitions and controlled recovery interval design | Gate H partial | F7 safety table |
| Comparative evaluation | Nine policies share one interface; 27-record synthetic pilot and seed-paired decision contrasts | Multi-scenario orchestration, checkpoint/resume and full metric capture | Repeated packet-path baselines/ablations with preregistered statistics | Gate I partial | Main results tables |
| Prior art/novelty | Dated primary-source screening protocol and working overlap matrix | Full-text/citation-chain two-reviewer screen and final claim audit | Not applicable | Gate J partial | Related work and claim boundary |
| Publication package | Architecture, protocol, metrics and limitations drafts | Generated research plots/tables, validity analysis, artifact guide and paper draft | Only after confirmatory evidence | Final | Submission package |

## Immediate dependency order

1. Preserve the non-privileged experiment pipeline as the controller/evaluation reference.
2. Add a real timestamped telemetry schema and connect it to the dual-vFW testbed.
3. Complete Level 2 policy/state validation before any route commit.
4. Complete Level 3 source-pinned draining and target admission, then measure it repeatedly.
5. Use those measurements in the unified runner before drawing comparative conclusions.

The generated `pilot-20261006-v1` artifacts are deliberately excluded from research conclusions: they validate plumbing with synthetic controller inputs and do not measure a packet path.
