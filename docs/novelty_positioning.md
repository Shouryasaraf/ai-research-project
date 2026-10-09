# Claim boundaries and prior-art positioning

Primary-source check: 2026-10-08. This is a working comparison, not an exhaustive novelty certification. The project studies a particular controller integration; it does not introduce state migration, probabilistic placement, or migration cost-benefit reasoning themselves.

## Direct overlaps

- **F2, uncertainty/security placement:** Forti, Paganelli and Brogi's [original preprint](https://arxiv.org/abs/1906.00197) already considers probabilistic infrastructure behavior and security-constrained VNF placement. Our calibrated traffic intervals and controller gating are a candidate distinction, not evidence that all related methods lack them.
- **F4, state and flow transition:** [OpenNF](https://wisr.cs.wisc.edu/papers/opennf.pdf), sections 1 and 2, coordinates internal NF state and forwarding changes, addresses state-update races, and distinguishes movement from waiting for existing flows to drain. Our coarse conntrack-copy lab is weaker than its stated consistency mechanisms. Neither flow pinning nor state copying is claimed as new.
- **F6, benefit versus migration cost:** [Ibrahimpasic et al.](https://arxiv.org/abs/2101.09343) optimize migration operations cost and outage loss. Our contextual threshold must be evaluated as a specific rule, not a novel discovery of cost-benefit migration.
- **Carbon-aware relocation:** [ESSO](https://cs.uwaterloo.ca/~mfbari/files/j8.pdf) relocates service chains according to renewable-energy availability and reduces brown-energy consumption in trace-driven simulations. Our modeled carbon score is not a measured carbon-reduction result.

## Testable integration claim

The candidate contribution is an auditable ordering of uncertainty gating, feasible candidate ranking, synchronization checks, contextual benefit threshold and fail-closed decisions in a stateful firewall control loop. To support it, matched ablations must show what each component changes, including additional delay and rejected opportunities. The synthetic live pilot does not establish superiority over reactive control. One alternate target cannot demonstrate better placement selection.

F5 and F7 remain comparison hypotheses, not established novel contributions. A broader full-text/citation-chain search and independent review are still required. The working matrix retains unreviewed sources rather than treating absence from an abstract as absence of a mechanism.

## Prohibited wording at this evidence level

Do not describe this prototype as seamless, zero-loss, crash-safe, physically carbon-saving, state-of-the-art, or publication-ready. Short same-socket continuation is observed evidence, not general TCP-state equivalence. Repeated execution on one historical traffic segment does not provide independent workload replication.
