# Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement

**Working research manuscript; not submission-ready.** Author information, venue, final protocol and independent confirmatory evaluation are intentionally unset. This draft describes a prototype and exploratory findings, not established novelty or superiority.

## Abstract

Stateful virtual-firewall orchestration must balance workload accommodation against migration disruption and security constraints. We implement an auditable controller that combines traffic-forecast intervals, constrained placement, a contextual migration-benefit threshold and guarded state/route transitions. A Linux namespace testbed exercises persistent application flows through kernel-enforced firewall paths. Comparative development pilots expose an important trade-off: the proposed controller can improve goodput over static placement while responding more slowly than a reactive baseline. Two historical time segments from one trace source produce sharply different offline migration-decision propensities, while captured rate-derived live pilots do not establish an advantage over reactive control. A conservative route journal separately addresses restart containment without assuming stale connection state is safe to restore. These observations motivate further study rather than establish general superiority. Carbon and risk remain modeled, and full transport-state equivalence and production recovery are outside the current evidence.

## 1. Problem and contribution boundary

The system has seven locked functions: dynamic instance scaling, uncertainty/security-aware placement, load distribution, stateful warm transition with flow affinity, uncertainty-gated migration, adaptive benefit threshold and invariant-driven fallback. The research question is whether their particular coordination improves service and migration trade-offs under calibrated uncertainty. Merely combining components does not establish novelty.

The present artifact contributes an executable experimental integration, auditable policy comparisons and explicit evidence boundaries. It does not claim that state movement, uncertainty-aware placement or cost-aware migration are new individually.

## 2. Related work

[OpenNF](https://wisr.cs.wisc.edu/papers/opennf.pdf) coordinates network-function state with forwarding updates and addresses races during state movement. Its guarantees are not implied by our coarse conntrack copying. [Forti et al.](https://arxiv.org/abs/1906.00197) study probabilistic infrastructure and security-aware VNF placement. [Ibrahimpasic et al.](https://arxiv.org/abs/2101.09343) balance stateful migration cost against outage loss. [ESSO](https://cs.uwaterloo.ca/~mfbari/files/j8.pdf) studies energy-aware service-chain relocation. Accordingly, our candidate distinction is the specific uncertainty-gated integration and its measured trade-offs. The full-text/citation-chain review remains incomplete; see the machine-readable prior-art matrix and bibliography.

The later primary-source screen adds [Patowary et al.](https://arxiv.org/html/2404.07701v1), who formalize a stateful flow-migration correctness property; [Shang et al.](https://ieeexplore.ieee.org/document/9248649/), who account for prediction errors and migration costs in online SFC placement; and [Peretz et al.](https://deepness-lab.org/wp-content/uploads/2023/06/201585_1.pdf), who use security-motivated VNF state movement. [Mahyoub et al.](https://arxiv.org/html/2607.00471v1) jointly address security risk and migration in a satellite SFC setting. These overlaps narrow the proposed claim and demand direct method comparisons before any novelty assertion.

## 3. Method

Candidates first pass hard policy, health, capacity and security restrictions. Only eligible candidates are ranked using configured resource, latency, carbon, risk and uncertainty-headroom weights. Soft-score ablations retain hard safety constraints.

The controller uses forecast uncertainty to decide whether to wait, prepare or synchronize a warm target. A commit requires supported state validation and a positive margin between normalized expected benefit and the contextual threshold. Benefits and penalties are logged separately. The current live experiment uses independently supplied modeled carbon/risk benefit credits, not a fitted causal emissions or attack-loss model.

The source-pinning proxy and transparent route lab are distinct mechanisms. The latter copies supported conntrack fields and changes both traffic directions. A durable journal records intent before each route change and verifies readback. On uncertain restart, containment precedes any restoration; stale source state is never assumed sufficient. This trades availability for conservative behavior and is not an atomic distributed commit.

## 4. Experimental setup

See `paper_methods_draft.md` for implementation details and `live_experiment_protocol.md` for the initial frozen development design. All live experiments use one Linux/WSL host, six namespaces, default-deny nftables and tc-shaped source/target links. Persistent TCP echo requests measure completed-payload goodput and request round-trip delay. Completed interval observations, not future scheduled demand, drive forecasts.

Nine policy variants share the same interface. Seed-paired schedules and shuffled execution order reduce avoidable comparison differences. Separate experiments examine modeled parameter sensitivity, real-process interruption and four additional workload shapes. These experiments answer different questions and must not be pooled as independent replications of one outcome.

## 5. Exploratory results

The original pilot numerical tables are generated from raw records in `results/live-paired-20261008-pilot/results.md` and `results/live-mawi-20261008-pilot/results.md`; the manuscript paraphrases them and points to the generated records for exact values. The synthetic pilot favors the proposed method over static placement but favors reactive control over the proposed method. Successful warm-path requests and failures in the cold baseline illustrate the importance of state handling in the tested conditions, not a general losslessness guarantee.

In the historical rate-derived segment, different commit decisions coexist with similar achieved goodput. The segment therefore does not demonstrate improved throughput from prediction. Repetitions reuse the same segment and cannot establish cross-workload generalization. The modeled sensitivity grid changes contextual decisions but does not measure emissions, attack reduction or temporal migration frequency.

A second, 2005-01-01 sample from the same MAWI samplepoint passed the publisher's packet and byte totals. Its 181-second held-out portion led the full policy to COMMIT on almost all independent ready-target opportunities, in contrast with all WAIT on the earlier 2000 sample. The evaluator resets state each second, so these are not realized repeated migrations or net-cost outcomes. A six-trial captured, scaled-payload lab pair on the second trace also favored reactive goodput slightly and observed reverse packet-instance deficits under both policies. The complete negative/mixed transfer result is documented in `results/mawi-transfer-20261010/results.md` and the validated live table in `results/live-mawi2005-captured-pair-20261010-v1/`. Neither time segment is an independent site or a modern vFW workload.

The expanded modeled grid pairs candidate choices across 243 identical opportunities for all nine policies. Removing the carbon term changes 81 choices and removing the soft risk term changes 27 relative to the full controller, while the hard-prohibited node remains excluded. Candidate choices are recorded even for `WAIT` actions, so these counts neither represent deployments nor quantify real emissions or attacks. The generated table is in `results/sensitivity-20261010-placement-v3/`.

Restart probes establish blocked-route containment followed by source restoration when no active TCP state exists. The journal-integrated live smoke separately checks ordinary migration operation. Neither result establishes automatic recovery of established flows after controller or target failure.

The later active-recovery study extends this boundary: a supervised migration-process exit with surviving target state allowed original-flow failback after reverse synchronization of supported fields. Target-state deletion instead retained blocked routes and disrupted the flows. Verified endpoint captures expose packet-instance deficits even where application requests recovered. The all-attempt report in `results/recovery-20261009/` preserves failed development attempts and the corrected final batch. This is still not full-host recovery, full TCP-state equivalence or zero-loss migration.

Six later proxy lifecycle repetitions functionally connect flow-occupancy-derived modeled demand, scale-out, predictive prewarm, pinned-state validation, guarded target admission, drain, and scale-in. The generated `results/lifecycle-20261009-snapshotted/` report reads their raw records and verifies exact source snapshots for the final three. This proxy mechanism does not transfer conntrack and is not a comparative benchmark or measured carbon/risk experiment.

Separate method controls checked the endpoint packet observation: two ordinary traffic trials showed zero matched packet deficits, while two isolated deliberate-drop trials showed 12 missing forward packet instances each. The same application requests eventually completed, demonstrating that request-success counts alone would conceal these temporary wire-level drops. The generated `results/packet-validation-20261010/` report recomputes the paired captures and source fingerprint. These controls validate the measurement method in one topology; they are excluded from migration outcome comparisons.

A later captured three-seed full-versus-reactive development batch recorded a route commit in every trial and no request failures. Endpoint matching nevertheless found eight missing reverse packet instances in every trial. Reactive control again achieved higher mean goodput in the same synthetic schedule. The `results/live-captured-pair-20261010-v2/` tables are generated from complete raw batch records and verified captures. Neither the repeated deficit count nor this small paired difference establishes a general loss rate or policy ranking.

A post-hoc timing diagnostic finds the last successful same-flow response before each recorded transition and the first after it. These brackets include pacing and synchronization, so they are not outage estimates. Their policy ordering reverses between the synthetic step and second historical rate-derived batches; see `results/live-captured-pair-gap-20261010-v3/` and `results/live-mawi2005-captured-pair-gap-20261010-v2/`. Exact interruption remains unmeasured.

A separate re-parse of those validated endpoint captures found no sender-side TCP RST in 12 migration trials, but repeated identical payload-sequence instances in all 12. These are bounded wire-visible observations, not proof that the two kernels held equivalent sequence/window state; see `tcp_wire_diagnostic.md` and its generated result tables.

An additional offline carbon-input check imports two aligned historical half-hourly regional **forecasts** from NESO's CC BY 4.0 Carbon Intensity API. When mapped to hypothetical candidates with all other inputs held modeled and fixed, full and carbon-unaware placement prefer different nodes in every slot. This demonstrates implementation sensitivity to a sourced carbon signal but does not estimate real power use or emissions. The provenance and decision boundary are in `results/neso-carbon-replay-20261010/`.

## 6. Validity, ethics and reproducibility

Short single-host experiments cannot represent production failure domains or multi-host timing. The synchronous client can censor offered demand under congestion. RTT includes only completed requests; failures must be reported alongside it. Local queue drops, request timeouts and end-to-end packet loss are different metrics. In-flight updates, complete TCP sequence/window consistency, packet-level disruption and independent reproduction remain open.

All traffic and faults stay inside the isolated local lab. No third-party attack traffic is generated. Raw public-trace captures are excluded from the repository. New batches archive executed source/config files; older pilots contain fingerprints but no recoverable exact source snapshot. Artifact instructions and the claim ledger distinguish measured, modeled and unverified quantities.

## 7. Conclusion and required final work

The prototype makes policy decisions and their safety checks inspectable on a real software-firewall path. Its current evidence is mixed and does not support universal benefit from uncertainty gating. A final paper requires independent, adequately repeated evaluation, complete relevant prior-art review, resolved artifact terms, stronger state/recovery measurements and conclusions confined to those results. The publication claim ledger is the acceptance checklist for that work.
