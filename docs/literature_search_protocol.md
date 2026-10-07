# Prior-Art Search Protocol (working review)

Search date: 2026-10-07. This is a reproducible *screening log*, not a claim of exhaustive systematic review. Search engines and publisher indexes can change; a final submission must rerun the queries and record counts and exclusion decisions.

## Question and boundary

Does existing research already combine (a) predictive uncertainty as an explicit wait/warm/synchronize/commit gate, (b) carbon and attack-risk-aware stateful vFW placement, (c) flow-pinned migration with checked security invariants and fallback, and (d) an adaptive cost-benefit threshold? Individual ingredients must not be represented as novel without further evidence.

## Search strings

Run in IEEE Xplore, ACM Digital Library, arXiv and publisher/author repositories, with title/abstract/keyword searches and backward/forward citation screening:

1. `("virtual firewall" OR VNF OR NFV) AND (stateful migration OR flow handover OR state transfer)`
2. `(VNF OR "service function chain") AND (carbon OR renewable OR energy) AND (placement OR migration)`
3. `(VNF OR NFV) AND (uncertainty OR probabilistic OR conformal) AND (prediction OR placement OR migration)`
4. `(VNF OR firewall) AND (attack risk OR security risk OR moving target defense) AND (placement OR migration)`
5. `(VNF OR NFV) AND (migration cost OR benefit threshold OR cost loss) AND prediction`
6. `(stateful VNF OR virtual firewall) AND (rollback OR fallback OR security invariant OR policy equivalence)`

Include primary research with a relevant method, protocol, or evaluation. Exclude secondary summaries from the evidence matrix unless used only to discover a primary paper. Read full texts before asserting that a paper *does not* contain a mechanism; abstracts support only positive overlap and tentative differentiation. Record the exact version and access URL. The working matrix in `prior_art_matrix.md` is deliberately conservative and does not establish priority.

## Review process before submission

Two reviewers should independently screen titles/abstracts, then full texts for shortlisted papers, reconcile disagreements, search citations, and save a dated export with inclusion/exclusion reasons. The current one-reviewer screen is incomplete. Re-run searches immediately before manuscript submission.
