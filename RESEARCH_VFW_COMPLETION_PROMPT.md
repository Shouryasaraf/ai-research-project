# Research vFW Project Completion Prompt

## Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement

Copy everything from **START OF COMPLETION PROMPT** through **END OF COMPLETION PROMPT** into the coding agent that will continue this repository.

---

## START OF COMPLETION PROMPT

You are the principal research engineer continuing an existing software-only, publication-oriented NFV research repository titled:

**Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement**

Work inside the existing `vfw-research-project` repository. Treat this completion prompt and the repository's existing master specification as authoritative. Preserve the exact seven-function scope. Do not restart the project, replace working components unnecessarily, fabricate data, invent citations, or describe unverified behavior as experimentally proven.

Your job is to complete the remaining engineering, evaluation, reproducibility, and publication work. Continue autonomously stage by stage. At each gate, run the relevant tests, save evidence, update traceability, and distinguish measured, derived, modeled, synthetic, emulated, and unverified results.

## 1. Locked research scope

The final system must integrate exactly these seven functions:

1. Dynamic Virtual Firewall Instance Scaling.
2. Uncertainty- and Security-Risk-Aware vFW Placement.
3. Traffic Distribution and Load Balancing.
4. State-Consistent Warm Migration with Flow Pinning.
5. Uncertainty-Gated Predictive Warm Migration.
6. Adaptive Migration-Benefit Threshold.
7. Security-Invariant Migration and Fallback Controller.

Functions 2, 4, 5, 6, and 7 are proposed research contributions only. Treat novelty as a hypothesis pending a documented prior-art review. Never claim novelty, superiority, state-of-the-art performance, seamless migration, or publication readiness without matching evidence.

## 2. Existing implementation: inspect and preserve

Before changing code, inspect the repository and verify the current state rather than trusting this summary blindly. The repository is expected to contain:

- typed domain models and deterministic controller logic;
- auditable placement, carbon, risk, benefit, and adaptive-threshold components;
- scaling hysteresis/cooldown and flow-affinity logic;
- a migration state machine and security-invariant validator;
- logical fallback and structured audit records;
- a transparent rolling-mean split-conformal forecasting baseline;
- a common interface for static, reactive, prediction-only, uncertainty-aware, cold-migration, fixed-threshold, carbon/risk ablation, and full-controller policies;
- an immutable experiment-record schema;
- a Linux namespace/nftables single-vFW testbed;
- kernel conntrack tuple discovery/insertion smoke testing;
- a dual-vFW proxy-based flow-affinity/fallback smoke test;
- unit tests that previously passed.

Current evidence boundaries are expected to include:

- real kernel-enforced firewall allow/default-deny behavior is smoke-verified;
- source conntrack state discovery and target tuple insertion are smoke-verified, but TCP continuity after route transition is not;
- new-flow selection and proxy flow affinity are smoke-verified, but transparent SDN steering is not;
- logical fallback and one new-flow fallback observation exist, but repeated recovery experiments and established-flow recovery do not;
- forecasting, carbon, risk, placement, scaling, migration, and baselines have controller-level implementations, but publication comparisons do not yet exist.

Do not delete or weaken existing evidence. Run the current unit tests and smoke commands first, record exact versions and outcomes, and create a baseline commit/checkpoint before invasive changes if the worktree is clean. If the worktree is dirty, preserve user changes and report them.

## 3. Non-negotiable scientific rules

1. Never fabricate measurements, datasets, citations, DOIs, results, screenshots, logs, or successful tests.
2. Never treat a single smoke run as a benchmark.
3. Never label synthetic carbon/risk/workload inputs as real-world measurements.
4. Never call metadata copying or tuple insertion seamless stateful migration.
5. Never allow a weighted score to override a hard security constraint.
6. Never tune the proposed method on held-out test data or weaken baselines intentionally.
7. Never manually type final result values into paper tables or figures; generate them from immutable run records.
8. Never run attack traffic against public or third-party systems. Keep all fault/risk scenarios isolated and defensive.
9. Never commit secrets, credentials, large raw datasets, generated environments, or machine-specific absolute paths.
10. A missing capability must be documented precisely; implement the closest defensible alternative and label it accurately.

## 4. First actions and audit

Perform these actions before implementation:

1. Read `README.md`, all files in `docs/`, `configs/`, `src/`, `tests/`, and `scripts/`.
2. Inspect Git status, tracked files, ignored files, current branch, and recent commits.
3. Detect the host environment and record OS, WSL distribution, kernel, Python, nftables, conntrack, iproute2, Docker, Open vSwitch, Mininet/Containernet, and traffic-tool versions.
4. Run the current unit suite and existing smoke tests using documented commands.
5. Reconcile `docs/requirements_traceability.md`, `docs/limitations.md`, and `docs/verification_log.md` with observed evidence.
6. Produce a concise gap matrix with columns: requirement, current component, present evidence, missing implementation, missing experiment, acceptance gate, and paper artifact.
7. Freeze a practical implementation plan that prioritizes the smallest complete vertical experiment before broader evaluation.

Do not install software silently. Prefer available tools. If a dependency is required, document why, pin the version, and obtain authorization when the environment requires it.

## 5. Completion workstream A: reproducible execution environment

Create a reproducible local Linux execution path. Prefer Docker Compose plus Linux networking when Docker is available; otherwise retain and improve the WSL2 namespace implementation. Mininet/Containernet and Open vSwitch may be used if available, but do not make them mandatory without a documented fallback.

Required outputs:

- pinned Python dependencies and platform prerequisites;
- `Makefile` or cross-platform task scripts for setup, unit tests, smoke tests, one small experiment, analysis, and cleanup;
- configuration validation with actionable errors;
- graceful, idempotent cleanup after success, failure, or interruption;
- environment manifest stored with every experimental run;
- deterministic seed handling;
- a CI workflow for non-privileged tests and schema checks;
- a documented privileged local path for networking tests;
- no source code depending on developer-specific absolute paths.

Gate A passes only when a fresh documented environment can run all non-privileged tests and one isolated packet-path smoke test, and cleanup leaves no project-created namespaces, routes, rules, processes, or containers behind.

## 6. Completion workstream B: integrated multi-vFW scaling and load balancing

Connect the existing scaling manager and flow director to the executable testbed.

Implement and verify:

- at least two candidate vFW instances with health and capacity telemetry;
- controlled scale-out under sustained load and scale-in after sustained relief;
- hysteresis, cooldown, min/max instance limits, and anti-flapping behavior;
- new-flow placement across healthy instances;
- established-flow affinity or an explicitly defined safe drain policy;
- no path that bypasses all firewalls;
- default-deny and policy equivalence on every active vFW;
- per-instance CPU/load/flow/throughput telemetry;
- Jain fairness calculation over active vFW load;
- failure behavior when an instance becomes unhealthy during scale or balancing decisions.

Add unit, integration, and system tests. Use controlled reproducible traffic with declared flow counts, durations, and rates.

Gate B passes only when repeated scale-out and scale-in scenarios show correct controller actions, enforced firewall traversal, bounded flapping, healthy new-flow distribution, and preserved declared behavior for established flows. Report measured loss/interruption rather than describing it qualitatively.

## 7. Completion workstream C: Level 2 and Level 3 warm migration

Complete the migration evidence ladder defined in `docs/state_migration.md`.

### Level 2: validation before commit

Implement:

- parallel source and target vFW paths;
- target creation/prewarming and health checks;
- canonical firewall policy installation and normalized equivalence checks;
- supported conntrack/state snapshot and transfer;
- source-versus-target state comparison with missing, stale, duplicate, and mismatched entry reporting;
- timeout, retry, and idempotency behavior;
- refusal to commit when policy, state, health, capacity, route, or security validation fails;
- immutable audit records for every state transition and reason.

### Level 3: flow-pinned warm transition

Implement the safest feasible transition supported by the environment:

- keep pre-existing flows pinned to the source during drain when full kernel-state continuation cannot be guaranteed;
- direct new or explicitly eligible flows to the validated target only after commit;
- prevent duplicates and firewall bypass;
- measure active-flow behavior before, during, and after transition;
- drain and retire the source only after the declared completion condition;
- restore the last validated route/configuration after injected commit or target failure;
- make routing operations idempotent and restart-safe where feasible.

If true established TCP connection continuation through a changed network path is implemented, verify sequence/window/state completeness and application-level continuity. Otherwise, describe the mechanism accurately as source-pinned draining plus target admission, not seamless migrated-flow continuation.

Required measurements:

- state bytes and entry count;
- synchronization latency and retry count;
- mismatch rate;
- traffic-switch interruption;
- established-flow completion, reset, timeout, and disruption rates;
- new-flow success rate;
- packet loss and goodput around the transition;
- source drain time;
- rollback/fallback recovery time;
- controller and network overhead.

Gate C passes only when repeated success and failure trials establish the declared Level 2/3 behavior and all negative cases safely abort or fall back. Update evidence-level documentation precisely.

## 8. Completion workstream D: telemetry and controller integration

Implement one timestamped telemetry schema shared by the testbed, policies, experiment runner, and results pipeline. It must include freshness and provenance.

Collect where feasible:

- node/vFW CPU and memory;
- link or interface bytes, throughput, drops, and errors;
- request/flow latency observations;
- active/new/completed/failed flow counts;
- conntrack/state size;
- vFW health and capacity;
- controller decision latency;
- policy, route, synchronization, and fallback events;
- workload prediction and uncertainty;
- carbon-intensity input and provenance;
- risk inputs, score components, and event provenance.

Use monotonic clocks for durations and UTC timestamps for identity. Mark stale or missing telemetry explicitly. Ensure stale telemetry changes controller behavior safely and is tested.

Gate D passes when every migration/placement/scaling decision can be reconstructed from its recorded inputs, configuration version, model version, reason, thresholds, invariant outcomes, and resulting action.

## 9. Completion workstream E: workload traces and forecasting

Implement a leakage-safe forecasting evaluation pipeline.

### Workloads

Provide deterministic generators for:

- steady load;
- periodic bursts;
- gradual trend;
- sudden overload/flash crowd;
- mixed short and long flows;
- varying state sizes;
- workload shift and out-of-distribution bursts.

Optionally add one appropriately licensed public workload trace only if its license, stable source, version/date, checksum, fields, preprocessing, and limitations can be verified. Do not invent labels the trace does not contain. Include a small legal fixture or deterministic generator so tests never depend on network downloads.

### Forecasters

Retain the transparent rolling-mean conformal baseline. Add at least one justified stronger but still reproducible model, such as quantile regression, conformalized regression, or a small ensemble. Avoid unnecessary deep learning.

Requirements:

- fixed forecast horizon and sampling interval;
- chronological train/validation/calibration/test splits;
- preprocessing fit only on training data;
- model-selection decisions restricted to training/validation data;
- held-out test data used once for final evaluation;
- MAE, RMSE, interval coverage, mean/normalized interval width, and calibration error;
- performance under shifts and bursts;
- persisted model/config/version metadata;
- explicit mapping from uncertainty to WAIT, PREWARM, SYNC, COMMIT, or ABORT;
- reactive and prediction-only baselines for causal attribution.

Include tests for split ordering, leakage, deterministic fitting, coverage calculations, malformed traces, drift/shift inputs, and model loading.

Gate E passes when held-out forecasts and intervals are reproducible, calibration is reported separately from accuracy, and controller actions demonstrably change as uncertainty changes.

## 10. Completion workstream F: carbon and attack-risk data

Create versioned trace adapters with strict provenance.

### Carbon

Support deterministic synthetic regional carbon-intensity traces. Optionally support a verified public source, but cache only permitted data and record source, license/terms, time resolution, timezone, units, checksum, preprocessing, gaps, and limitations.

Define and document:

- operational energy estimation assumptions;
- migration-related network/compute energy assumptions;
- conversion from energy and carbon intensity to estimated emissions;
- whether each value is measured, derived, or modeled;
- sensitivity ranges for uncertain power coefficients.

Never call estimated energy physical power measurement.

### Security risk

Keep the risk formula explainable. Define controlled defensive inputs such as exposure, vulnerability severity, anomaly indicator, trust state, patch posture, and recency. State normalization, bounds, missing-data policy, decay/recency behavior, and hard quarantine rules. Generate deterministic risk-event traces including transient and persistent changes.

Hard prohibited/quarantined-node constraints must remain separate from soft risk optimization.

Gate F passes when provenance is machine-readable, units and assumptions are validated, carbon/risk changes affect placement as designed, and unsafe nodes are rejected regardless of weighted benefit.

## 11. Completion workstream G: adaptive benefit and decision semantics

Make every term in the migration decision auditable:

`ExpectedNetBenefit = OperationalBenefit + CarbonBenefit + RiskReductionBenefit - MigrationCost - DisruptionPenalty - UncertaintyPenalty - OperationalOverhead`

Commit only when all hard invariants pass and:

`ExpectedNetBenefit > AdaptiveThreshold(context)`

For every term define:

- raw inputs and provenance;
- unit or dimensionless normalization;
- valid range and clipping behavior;
- sign convention;
- default weight and rationale;
- missing-data behavior;
- sensitivity range.

The adaptive threshold must respond to state size, active-flow count, uncertainty, forecast horizon, SLA criticality, headroom, recent failures, cooldown, and migration history. Add anti-thrashing logic and tests around exact decision boundaries.

Produce decision traces demonstrating WAIT, PREWARM, SYNC, COMMIT, ABORT, and FALLBACK for controlled scenarios. Compare against fixed thresholds using identical inputs.

Gate G passes when each decision is reproducible from a saved record and sensitivity analysis shows how weights/thresholds alter individual objectives and migration frequency.

## 12. Completion workstream H: invariant enforcement and fallback

Implement machine-checkable pre-commit, commit-time, and post-commit invariants:

- source/target policy equivalence;
- default-deny preservation where configured;
- no vFW bypass path;
- management-plane isolation;
- no quarantined/prohibited target selection;
- target health and capacity;
- state consistency within a preregistered tolerance;
- route points only to validated vFW paths;
- audit completeness;
- rollback restores a known validated configuration.

Fault-inject at least:

- target crash before synchronization;
- target crash during/after commit;
- policy mismatch;
- partial or stale state transfer;
- stale/missing telemetry;
- insufficient target capacity;
- route-commit failure;
- controller interruption/restart where feasible;
- simultaneous load and risk change.

Measure fallback trigger, success, recovery time, new-flow availability, established-flow impact, and residual invalid state. Ensure repeated fallback calls are safe.

Gate H passes only when invariant violations prevent unsafe commit and the last validated configuration is restored or retained with measured evidence in repeated trials.

## 13. Completion workstream I: unified experiment runner

Build an experiment runner that drives every policy through the same scenario, constraints, traffic, telemetry interface, and result schema.

Mandatory policies:

1. static placement/no migration;
2. reactive utilization threshold;
3. prediction-only migration without uncertainty gating;
4. uncertainty-aware migration without carbon/risk terms;
5. risk-unaware placement;
6. carbon-unaware placement;
7. cold/naive migration without warm synchronization;
8. fixed migration-benefit threshold;
9. full proposed controller.

Mandatory ablations:

- remove uncertainty gating;
- remove carbon term;
- remove security-risk term;
- remove flow pinning/draining protection;
- remove adaptive threshold;
- remove invariant validation/fallback only in an isolated safety experiment that cannot affect external systems;
- vary uncertainty calibration quality;
- vary forecast horizon, state size, long-flow ratio, carbon volatility, risk intensity, and workload burstiness.

Runner requirements:

- YAML/JSON scenario files validated by schema;
- paired seeds and identical input traces across policies;
- run IDs, status, start/end timestamps, and interruption markers;
- atomic or exclusive creation of immutable raw run records;
- checkpoint/resume without counting partial runs as successes;
- timeouts and guaranteed cleanup;
- pilot and confirmatory run separation;
- dry-run plan output;
- explicit environment, Git revision, configuration digest, model version, and trace checksum;
- validation that measured and modeled fields are never conflated.

Gate I passes when one command runs a small paired experiment across all mandatory policies and another command reproduces its validated table/figure outputs from raw records only.

## 14. Preregister the final experiment protocol

Before examining confirmatory results, finalize and commit:

- research questions and directional/non-directional hypotheses;
- primary and secondary outcomes;
- scenario parameter ranges;
- baselines and ablations;
- number of seeds/repetitions justified by pilot variance or a documented practical constraint;
- warm-up rule and exclusion criteria;
- practical-significance margins;
- statistical tests and effect sizes;
- confidence-interval method;
- multiple-comparison policy;
- rules for failed/interrupted runs;
- sensitivity-analysis grid;
- stopping rule;
- known validity threats.

Do not modify this protocol after final runs without versioning and clearly labeling the change as exploratory.

## 15. Metrics and statistical analysis

Collect raw events needed to compute at least:

- throughput, goodput, p50/p95/p99 latency, and packet loss;
- SLA violations and overload duration;
- migration count, failed/unnecessary migrations, cooldown violations, and decision latency;
- traffic-switch interruption and service downtime;
- established-flow completion/reset/timeout/disruption;
- state-transfer time, size, bandwidth, mismatch rate, and retries;
- CPU, memory, interface/network, and controller overhead;
- active vFW count and Jain fairness;
- carbon-intensity exposure, modeled energy, and estimated emissions;
- risk exposure and invariant violations;
- forecast MAE/RMSE, coverage, interval width, and calibration error;
- fallback trigger/success rates, recovery time, and residual impact.

For paired experiments:

- report sample count and failure count;
- show per-policy mean and median when informative;
- show standard deviation or robust dispersion;
- produce 95% confidence intervals, preferably paired bootstrap intervals when justified;
- report paired effect sizes and practical significance;
- use a justified paired test when inferential testing is appropriate;
- correct or explicitly scope multiple-comparison families;
- retain negative, null, and trade-off findings.

Generate tidy processed datasets, machine-readable summary tables, and publication figures through code. Add tests that recompute selected metrics from small fixtures and detect schema violations or duplicate run IDs.

## 16. Required experiment matrix

At minimum implement three tiers:

### Tier 1: fast deterministic CI experiments

- tiny generated traces;
- controller-only or non-privileged emulation;
- validates schemas, policy parity, calculations, and figure generation.

### Tier 2: local privileged smoke experiments

- real nftables/namespace packet paths;
- multi-vFW scaling/balancing;
- successful warm transition/drain;
- rejected unsafe migration;
- fallback after target failure.

### Tier 3: repeated research experiments

- all policies under paired scenario traces and seeds;
- workload, carbon, and risk variations;
- state-size and long-flow variations;
- fault injection;
- calibration and sensitivity studies;
- enough repetitions for the preregistered uncertainty estimates.

If compute/time limits prevent the complete Tier 3 matrix, implement the full runner and configs, execute a clearly labeled pilot subset, and document exactly which confirmatory runs remain. Do not manufacture the missing results.

## 17. Prior-art and novelty review

Conduct a structured literature search using primary sources and authoritative indexes. Focus on the intersection and individual components of:

- stateful VNF/vFW placement and migration;
- predictive VNF scaling/migration;
- uncertainty-aware orchestration or conformal forecasting for resource management;
- carbon-aware NFV/cloud/edge placement;
- security/attack-risk-aware VNF placement;
- connection-state transfer, flow affinity, draining, and service-function chaining;
- migration cost-benefit thresholds and anti-thrashing;
- invariant checking and rollback/fallback in network orchestration.

For every included paper record title, authors, year, venue, DOI or stable URL, exact relevant contribution, evaluation environment, limitations, and overlap/difference with this project. Verify metadata from the original paper/publisher. Never cite a search snippet as the source and never invent a citation.

Create:

- `docs/literature_search_protocol.md`;
- `docs/prior_art_matrix.csv` or equivalent machine-readable file;
- `docs/novelty_positioning.md` with cautious, evidence-based language;
- a bibliography file suitable for the eventual paper.

Separate component novelty from system-integration novelty. If prior work substantially overlaps a proposed contribution, narrow the claim rather than hiding the overlap.

Gate J passes when each proposed contribution has a traceable prior-art comparison and no novelty statement exceeds the evidence.

## 18. Publication artifacts

Create and maintain:

- updated reproducibility README;
- requirements/evidence traceability matrix;
- architecture and control/data-flow diagrams with editable source;
- algorithm pseudocode and complexity discussion;
- threat model and invariant catalog;
- frozen experiment protocol and statistical-analysis plan;
- workload/dataset/carbon/risk provenance sheet;
- baseline and ablation definitions;
- limitations, validity threats, ethical/safety notes, and negative results;
- automatically generated figures and tables;
- paper-ready method, implementation, and experimental-setup notes;
- a results narrative generated from verified summaries but manually checked for accurate interpretation;
- a demonstration script covering normal operation, predictive prewarming, successful migration/drain, rejected unsafe migration, and fallback;
- artifact-evaluation instructions for a reviewer.

Prepare a publication draft only after the evidence pipeline exists. A paper draft must clearly distinguish:

- direct measurements from modeled estimates;
- namespace/WSL emulation from physical multi-host deployment;
- source-pinned draining from true transferred-flow continuation;
- pilot results from confirmatory results;
- proposed novelty from validated contribution;
- limitations and threats from verified capability.

Do not select a venue or claim acceptance likelihood without a separate current venue search.

## 19. Repository quality and expected structure

Evolve the repository toward this structure without gratuitous rewrites:

```text
vfw-research-project/
  README.md
  LICENSE
  pyproject.toml
  docker-compose.yml              # when used
  Makefile                        # or equivalent task runner
  configs/
    controller/
    experiments/
    scenarios/
  data/
    README.md
    fixtures/
    provenance/
  docs/
  src/vfw_research/
    telemetry/
    forecasting/
    carbon/
    security_risk/
    placement/
    scaling/
    load_balancing/
    migration/
    invariants/
    controller/
    experiments/
    analysis/
  tests/
    unit/
    integration/
    system/
  scripts/
  artifacts/
    raw/                           # immutable and normally gitignored
    processed/
    figures/
    tables/
    manifests/
```

Requirements:

- typed interfaces and validated configuration;
- structured logs and explicit error messages;
- separation of policy logic, infrastructure control, experiments, and analysis;
- no global mutable research state;
- timeouts, retries, and idempotent cleanup;
- tests assert actual actions, invariants, and reasons;
- documentation links remain valid inside the GitHub repository;
- a license is selected only with user authorization if none exists.

## 20. Testing requirements

Preserve existing tests and add coverage for:

- configuration and schema validation;
- telemetry freshness and missing values;
- formula units, normalization, clipping, and boundary conditions;
- placement hard constraints;
- adaptive-threshold boundaries and anti-thrashing;
- chronological forecast splits and preprocessing leakage;
- uncertainty calibration and action mapping;
- migration legal/illegal transitions;
- synchronization mismatch and partial-state cases;
- retry/idempotency behavior;
- policy equivalence and default-deny checks;
- flow affinity, draining, and established-flow behavior;
- scale hysteresis/cooldown;
- target crash, route failure, stale telemetry, timeout, and fallback;
- controller restart where feasible;
- experiment parity across policies;
- immutable results, interrupted runs, duplicate IDs, and configuration digests;
- metric recomputation and deterministic figure/table generation;
- end-to-end small experiment.

Run unit tests frequently. Run privileged tests only inside the isolated local lab and always clean up. Record commands and outcomes in `docs/verification_log.md` with dates and evidence boundaries.

## 21. Final definition of done

The project is complete only when all of the following are true or a precise documented environment limitation prevents a specific item:

- all seven functions operate through one integrated controller and experiment interface;
- real generated/replayed traffic traverses enforced software-firewall paths;
- scale-out, scale-in, and multi-vFW load distribution are repeatably demonstrated;
- target prewarming, policy/state synchronization, validation, route/flow transition, drain, abort, and fallback are implemented;
- the exact achieved migration evidence level is experimentally verified;
- uncertainty is calibrated on held-out traces and changes operational decisions;
- carbon and security risk change placement while hard security constraints remain absolute;
- the adaptive threshold is compared fairly with fixed-threshold control;
- fault injection demonstrates invariant enforcement and measured fallback behavior;
- all mandatory baselines and essential ablations use identical paired scenarios;
- final results use repeated trials, confidence intervals, effect sizes, and immutable provenance;
- a clean environment reproduces tests, a smoke demo, and one complete small experiment;
- figures and tables are generated from raw records;
- prior art and citations are verified;
- documentation and publication notes match the evidence exactly;
- no performance, carbon, security, novelty, or publication claim is fabricated.

## 22. Required working behavior and progress reports

Proceed autonomously through the workstreams in dependency order. Do not stop after writing plans or scaffolding. Implement, test, and document each vertical slice before expanding it.

Pause only when:

- a choice would materially change the locked research scope;
- credentials, paid services, or externally hosted infrastructure are required;
- installing privileged dependencies requires authorization;
- a safety or licensing issue cannot be resolved locally;
- a user decision is required to select a license, dataset with restrictive terms, or publication venue.

At the end of every gate, report:

1. files created or changed;
2. commands executed;
3. tests/scenarios passed and failed;
4. actual measurements, clearly labeled;
5. modeled or synthetic outputs, clearly labeled;
6. limitations and unresolved risks;
7. current traceability status;
8. next gate.

When a command fails, diagnose it, preserve the failure evidence, implement a safe fix, and rerun the smallest relevant check. Do not hide failures. Do not claim a gate passed based only on code inspection.

Begin now by auditing the repository, running existing tests, producing the gap matrix, and then completing Gate A followed by the smallest integrated multi-vFW experiment that advances Gates B, C, D, and H together.

## END OF COMPLETION PROMPT

