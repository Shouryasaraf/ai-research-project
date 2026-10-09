# Claim boundaries and prior-art positioning

Primary-source check: 2026-10-10. This is a working comparison, not an exhaustive novelty certification. The project studies a particular controller integration; it does not introduce state migration, probabilistic placement, or migration cost-benefit reasoning themselves.

## Direct overlaps

- **F2, uncertainty/security placement:** Forti, Paganelli and Brogi's [original preprint](https://arxiv.org/abs/1906.00197) already considers probabilistic infrastructure behavior and security-constrained VNF placement. Our calibrated traffic intervals and controller gating are a candidate distinction, not evidence that all related methods lack them.
- **F4, state and flow transition:** [OpenNF](https://wisr.cs.wisc.edu/papers/opennf.pdf), sections 1 and 2, coordinates internal NF state and forwarding changes, addresses state-update races, and distinguishes movement from waiting for existing flows to drain. Our coarse conntrack-copy lab is weaker than its stated consistency mechanisms. Neither flow pinning nor state copying is claimed as new.
- **F6, benefit versus migration cost:** [Ibrahimpasic et al.](https://arxiv.org/abs/2101.09343) optimize migration operations cost and outage loss. Our contextual threshold must be evaluated as a specific rule, not a novel discovery of cost-benefit migration.
- **Carbon-aware relocation:** [ESSO](https://cs.uwaterloo.ca/~mfbari/files/j8.pdf) relocates service chains according to renewable-energy availability and reduces brown-energy consumption in trace-driven simulations. Our modeled carbon score is not a measured carbon-reduction result.
- **Flow migration correctness:** [Patowary, Barua and Sukapuram](https://arxiv.org/html/2404.07701v1) define Weak-O and prove a no-buffer/no-drop flow-migration algorithm under their model. Our coarse conntrack implementation does not establish that property; the new captured pilot actually observes packet-instance deficits.
- **Prediction errors and online placement:** [Shang, Liu and Yang](https://ieeexplore.ieee.org/document/9248649/) explicitly consider changing SFC demand, migration cost and prediction errors. Those ideas cannot be claimed as new; our exact uncertainty gate and empirical trade-offs require comparison.
- **Security-motivated state movement:** [Peretz, Shenzis and Hay](https://deepness-lab.org/wp-content/uploads/2023/06/201585_1.pdf) use active/passive VNF state migration for moving-target defense. [Mahyoub et al.](https://arxiv.org/html/2607.00471v1) jointly optimize security co-location risk and migration cost in a different satellite setting. A broad “security-aware migration” novelty claim would overlap both.

## Testable integration claim

The candidate contribution is an auditable ordering of uncertainty gating, feasible candidate ranking, synchronization checks, contextual benefit threshold and fail-closed decisions in a stateful firewall control loop. To support it, matched ablations must show what each component changes, including additional delay and rejected opportunities. The synthetic live and captured pilots favor reactive control on mean goodput in the tested conditions. One alternate target cannot demonstrate better placement selection. A defensible paper may instead characterize the situations in which gating helps, harms or safely abstains; this remains an empirical question.

F5 and F7 remain comparison hypotheses, not established novel contributions. A broader full-text/citation-chain search and independent review are still required. The working matrix retains unreviewed sources rather than treating absence from an abstract as absence of a mechanism.

## Prohibited wording at this evidence level

Do not describe this prototype as seamless, zero-loss, crash-safe, physically carbon-saving, state-of-the-art, or publication-ready. Short same-socket continuation is observed evidence, not general TCP-state equivalence. Repeated execution on one historical traffic segment does not provide independent workload replication.
