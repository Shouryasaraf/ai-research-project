# Conditional liveness of the uncertainty-width gate

This is a source-level argument about the implemented decision function, not a proof of packet-level migration correctness or a claim that the experimental escape improves performance. The branch order is in `src/vfw_research/controller.py`; the escape is in `src/vfw_research/liveness_guard.py`. It was written after the adverse Cyber4OT results and is therefore explanatory, not preregistered theory.

Let the source capacity be \(C_s>0\), the one-step forecast interval be \([\ell_t,u_t]\), the configured overload fraction be \(\theta\), and the maximum commit-width fraction be \(\gamma\). Define \(w_t=(u_t-\ell_t)/C_s\). Suppose at every decision from some time \(t_0\):

1. Security invariants and telemetry freshness pass; at least one target satisfies hard placement constraints.
2. The target is already warm and \(u_t/C_s\geq\theta\).
3. \(w_t>\gamma\).

Then the original `decide` function returns `WAIT` at every such decision. This holds even if the target is synchronized, the point forecast is above the overload trigger, and net benefit exceeds the adaptive threshold. **Proof:** after invariants, feasibility and upper-utilization checks pass, the width check precedes the readiness and benefit checks. With a warm target and width above the gate, that branch returns `WAIT`; later checks are unreachable. Reapplying the same premises at the next decision yields the same result. This is a conditional indefinite-wait property; it does not say that all stochastic forecasts or workloads satisfy the premises forever.

The three preselected Cyber4OT PLC-port normal members instantiate this condition over their observed trial windows: fixed normalized widths 0.222692, 0.241013 and 0.229504 exceeded \(\gamma=0.20\), and all 435 full-policy decision records were uncertainty waits with zero route commits. This finite observation corroborates the branch argument but does not extend it to an unbounded workload or quantify how often the condition occurs in production.

The separately named development escape has a narrower conditional property. Once the baseline has produced at least three consecutive qualifying uncertainty waits and the observed-overload streak is at least three, it advances to `SYNC` if state is not marked synchronized, or to `COMMIT` if it is. It still requires no invariant violation, a feasible selected node, fresh telemetry, and net benefit strictly above the adaptive threshold. A subsequent `SYNC` must actually complete and the overload/wait premises must persist to permit a later commit. Any failure of these conditions may continue to wait or fall back. This is an action-level liveness escape under assumptions, not a safe-migration theorem; kernel state import, route readback and packet continuity require separate evidence.

The development comparison on PLC member 070 showed the escape making one physical commit in each of five trials, recovering much of the original goodput gap while remaining below the reactive mean and retaining high trial-wide p95 latency. The separately frozen Zero-SWARM normal-file check did not activate the escape. A new independent source that actually exercises the high-width condition is required to evaluate generality. No threshold calibration or outcome-driven substitution is justified by this argument.
