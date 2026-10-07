# Requirements Traceability Matrix

Status values: **specified**, **core implemented**, **testbed pending**, **experiment pending**.

| ID | Locked functionality | Implementation target | Required verification | Publication evidence | Current status |
|---|---|---|---|---|---|
| F1 | Dynamic vFW instance scaling | `scaling.py` manager with hysteresis, cooldown, capacity and health checks | Scale-out/in integration tests; anti-flapping workload | Active-instance count, overload duration, SLA and overhead comparison | Core implemented; multi-vFW testbed pending |
| F2 | Uncertainty- and security-risk-aware placement | `placement.py`, `carbon.py`, `security_risk.py` | Hard-constraint unit tests; identical-scenario baseline and sensitivity experiments | Per-objective metrics, feasibility, risk exposure, carbon estimate and trade-off plots | Explainable core models and synthetic paired-run interface implemented; testbed experiments pending |
| F3 | Traffic distribution and load balancing | `load_balancing.py` flow director with flow affinity | Fairness, overload and established-flow integration tests | Jain fairness, throughput, latency, drops and flow disruption | Core implemented; multi-vFW testbed pending |
| F4 | State-consistent warm migration with flow pinning | `migration.py`, `state_sync.py`, conntrack smoke adapter | Real established/new-flow continuity, state mismatch and rollback tests | Downtime, reset rate, state transfer size/time/mismatch | Kernel tuple insertion verified; route transition and flow continuity pending |
| F5 | Uncertainty-gated predictive warm migration | `controller.py`, `forecasting.py` and gate policy | WAIT/PREWARM/SYNC/COMMIT boundary tests; synthetic pilot and historical MAWI forecast plus offline decision pilot | Forecast accuracy, interval calibration, migration quality and count | Conformal baseline, exploratory adaptive residual model and paired policy decisions implemented; trace-derived packet-path migration experiments pending |
| F6 | Adaptive migration-benefit threshold | `benefit.py` | Formula/boundary tests; fixed-versus-adaptive seeded experiments | Net-benefit terms, sensitivity, effect sizes and objective metrics | Core and fixed/adaptive runner interface implemented; sensitivity experiments pending |
| F7 | Security-invariant migration and fallback | `invariants.py`, `migration.py`, `fallback.py`, dual-vFW health gate | Policy/path/health/state fault injection and recovery-time tests | Prevented unsafe commits, violations, fallback success/recovery | New-flow source-path restoration smoke-verified; established-flow recovery and repeated experiments pending |

## Gate audit

- Every locked function has a named implementation target.
- Every function has at least one testbed or experiment requirement.
- Every function has defined paper evidence.
- No row is treated as experimentally validated at Stage 0/1.
- All declared baseline and ablation policies share one typed decision interface.
- The synthetic-small scenario produces immutable paired records and generated summaries for pipeline verification only; outcome experiments on the packet path remain pending.
