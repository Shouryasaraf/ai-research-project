# Direct comparator: Deng et al. (NDSS 2017)

[Deng et al., *On the Safety and Efficiency of Virtual Firewall Elasticity
Control*](https://cse.buffalo.edu/~hongxinh/papers/NDSS2017.pdf) is a direct
primary comparator for this project's architecture. This first-pass map is
based on its abstract, introduction, controller overview, migration and
scaling sections; it is **not** a certification that unmentioned mechanisms
are absent from the full paper.

| Submitted functionality | Verified overlap in Deng et al. | Our defensible boundary today |
|---|---|---|
| 1. Dynamic vFW scaling | Creates/deletes instances and computes scale-out/in assignments. | Scaling itself is prior art; our live namespace lab does not yet show general scale-in/out. |
| 2. Uncertainty/security-risk-aware placement | Ensures firewall semantic safety and analyzes resource feasibility. | Risk scoring and forecast uncertainty are candidate differences, but both need exact method comparison with other papers and measured inputs. |
| 3. Distribution/load balancing | Updates flow rules to redirect traffic as instances change. | Dynamic steering and balancing are prior art; our two-path route switch is narrower. |
| 4. State-consistent warm migration/flow pinning | Coordinates rule/state movement and flow updates with explicit in-flight buffering concerns. | Generic stateful transition is prior art. Our coarse conntrack copy and pinning do not meet its semantic or packet guarantees. |
| 5. Uncertainty-gated predictive warm migration | Predicts in-flight buffer cost, but the checked sections do not establish whether it has our specific traffic-forecast interval gate. | A specific WAIT/PREWARM/SYNC/COMMIT gate remains a comparison hypothesis only. Our own results show a liveness failure on three PLC-port members. |
| 6. Adaptive migration-benefit threshold | Optimizes resource/update/buffer costs for scaling choices. | Cost-aware decisions are prior art; only a clearly compared context-sensitive formula and empirical trade-off might distinguish ours. |
| 7. Security-invariant migration/fallback | Checks semantic consistency of firewall rules and correct forwarding during scaling. | Security-sensitive correctness is prior art. Our hash and route-journal checks are narrower; general fallback or rule-semantic guarantees remain unproved. |

The strongest defensible paper framing is not “seven novel functionalities.”
It is a bounded empirical study of a *particular* uncertainty-gated,
carbon/risk-scored decision sequence, including the conditions where it
abstains or hurts. Reproducing Deng et al.'s full system is not trivial; at
minimum, compare its actual objectives and assumptions in the manuscript,
and use honest component ablations and reactive baselines in the same lab.
Independent full-text/citation-chain review is still needed before any
novelty assertion or journal submission.
