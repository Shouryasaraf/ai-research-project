# Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement

This repository is a software-only, publication-oriented NFV/SDN research prototype. It is being built from the locked seven-function specification in `../RESEARCH_VFW_MASTER_BUILD_PROMPT.md`.

## Current verified status

**2026-10-10 modeled placement grid:** the [generated candidate-choice report](docs/results/sensitivity-20261010-placement-v3/results.md) compares nine policies on 243 identical modeled opportunities. Relative to the full policy, removing the carbon term changed 81 candidate choices and removing the soft risk term changed 27; the prohibited node was never selected across 2,187 decisions. These are synthetic decision effects, not measured carbon savings or attack reduction.

**2026-10-10 captured migration pilot:** a new six-trial, three-seed paired batch compared the full and reactive policies while capturing generated TCP traffic at both endpoints. Both policies committed once per trial and had zero application request failures. The [generated captured results](docs/results/live-captured-pair-20261010-v2/results.md) show eight missing reverse packet instances in every trial despite completed requests; reactive control again had higher mean goodput. Windows and Linux suites now pass 121 tests each. These are short synthetic development runs, not a confirmatory superiority or universal packet-loss result.

**2026-10-10 capture-method controls:** two ordinary and two deliberate-drop trials completed inside the isolated firewall lab. The ordinary trials had zero matched endpoint packet deficits; each 1.5-second forced-drop trial exposed 12 missing forward packet instances while all application requests eventually completed. The [generated control report](docs/results/packet-validation-20261010/results.md) independently recomputes both captures and verifies the executed source. At this stage Windows and Linux passed 120 tests each. This validates sensitivity of the bounded capture method, not a migration loss rate.

**2026-10-09 lifecycle update:** six isolated proxy trials completed the modeled-demand → scale-out → PREWARM → source-pin validation → guarded COMMIT → balanced new-flow admission → drain → scale-in sequence. Two original TCP flows stayed on source and a new flow used target in each trial. The [generated lifecycle report](docs/results/lifecycle-20261009-snapshotted/results.md) validates all six raw records; the later three also verify an exact executed-source snapshot. This is a bounded functional witness: demand and candidate carbon/risk inputs are modeled, and proxy SYNC validates a pinning checkpoint rather than transferring conntrack. The Windows and Linux suites now pass 118 tests each.

**2026-10-09 recovery/capture update:** repeated active-flow failback and paired endpoint packet observation are now verified in the isolated lab. The six-case final batch passed; earlier failures are preserved in the [generated all-attempt report](docs/results/recovery-20261009/results.md). Surviving target state permits the tested original-flow recovery; lost target state remains fail-closed. Captures show packet deficits, so this is not a zero-loss claim. At this stage the Windows suite passed 115 checks.

**Latest completion pass:** 107 tests pass on both Windows and Linux. The live controller now uses a durable route journal with readback and commit-time policy/supported-state checks. Six revised no-flow process-interruption probes and eight additional steady/burst/trend/flash trials completed; separate integration smokes also passed. See [restart evidence boundaries](docs/restart_containment.md), [broader-workload protocol](docs/broader_live_protocol.md), [manuscript draft](docs/manuscript_draft.md), and [publication claim ledger](docs/publication_claim_ledger.md). This is still development evidence, not confirmatory publication readiness.

**2026-10-08 live-pilot update:** the closed-loop runner now uses measured application goodput to drive forecasts, policy decisions, conntrack synchronization and route changes. All 27 synthetic paired trials (nine policies, three repetitions) completed and cleaned up. See [generated results](docs/results/live-paired-20261008-pilot/results.md), [frozen pilot protocol](docs/live_experiment_protocol.md), and [reviewer reproduction guide](docs/artifact_reproduction.md). The full controller did not outperform reactive control in this pilot. Carbon/risk remain modeled; packet loss, atomic commit and complete TCP-state equivalence remain unverified. The stage history below predates this update where it describes live comparison as pending.

- **Stage 0:** specification artifacts drafted and traceability established.
- **Stage 1:** deterministic controller core implemented with standard-library tests.
- **Stage 2:** Linux-namespace/nftables testbed implemented and smoke-verified on WSL2; see `docs/verification_log.md` for the evidence boundary.
- **Stage 3:** scaling and flow-affinity controller cores are connected to the proxy testbed. Three isolated runs verified telemetry-driven activation and deactivation of a second nftables vFW path, plus pinned source and new target flows. Broader load, fairness and SLA evaluation remains pending.
- **Stage 4:** migration state machine, reference state adapter and supported kernel conntrack copying verified. A sustained controller-driven namespace pilot now exercises same-socket route transition with multiple flows. Complete TCP-state equivalence and seamless continuity are not established.
- **Stage 5:** rolling-mean and EWMA split-conformal forecasters plus chronological synthetic-trace evaluation implemented. One historical MAWI trace supports offline forecasting and 12 live rate-derived trials; these generate echo demand, not original packet replay.
- **Stage 6:** carbon estimation, explainable risk scoring, constrained placement, and adaptive benefit core implemented; comparative experiments remain pending.
- **Stage 7:** invariant validation and idempotent logical fallback implemented; the live proxy automatically restores the source for the next new flow after a target connect failure. Established target-flow recovery and proactive detection remain pending.
- **Stage 8:** common baseline-policy interface, validated scenario loader, immutable result schema and paired runners implemented. In addition to controller-only experiments, 27 synthetic live trials and 12 MAWI-rate live trials have generated summaries. Confirmatory publication experiments remain pending.
- Comparative application-level pilot observations are available; no confirmatory superiority, physical carbon savings, novelty certification or publication readiness is claimed.

The repository contains a deterministic decision harness and real kernel-enforced vFW testbeds. It does not yet demonstrate complete state-consistent warm migration or general/quantified flow continuity; see `docs/state_migration.md` for the evidence levels.
The isolated route lab and sustained controller pilot show bounded established TCP continuation after guarded conntrack import and two-sided route changes. This is not proof of seamless migration, packet-loss bounds, crash recovery or a fully integrated scaling-plus-migration lifecycle.

## Seven locked functionalities

1. Dynamic Virtual Firewall Instance Scaling
2. Uncertainty- and Security-Risk-Aware vFW Placement
3. Traffic Distribution and Load Balancing
4. State-Consistent Warm Migration with Flow Pinning
5. Uncertainty-Gated Predictive Warm Migration
6. Adaptive Migration-Benefit Threshold
7. Security-Invariant Migration and Fallback Controller

Functions 2, 4, 5, 6, and 7 are proposed research contributions pending prior-art review and experimental validation.

## Run the deterministic smoke scenario

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m vfw_research.demo
```

Run tests without installing dependencies:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

On this Codex host, `python` was not on the regular PATH. The bundled runtime used during development was:

```text
C:\Users\SHOURYA\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

That absolute path is development evidence only; scripts and source code do not depend on it.

## Research workflow

1. Freeze the protocol, hypotheses, metric definitions, and traceability matrix.
2. Validate the deterministic controller and failure behavior.
3. Build the isolated Linux container/network testbed.
4. Add scaling/load balancing, real state synchronization, and flow continuity checks.
5. Train and calibrate the workload forecaster using leakage-safe time splits.
6. Integrate carbon/risk placement and adaptive benefit gating.
7. Fault-inject invariant failures and validate fallback.
8. Run identical seeded baselines, ablations, sensitivity studies, and statistical analysis.

See `docs/` for the precise gates and research definitions.

## Run the synthetic evaluation-pipeline smoke test

This checks experiment plumbing only. It does **not** benchmark the network or establish a research result.

```powershell
$env:PYTHONPATH = "src"
python -m vfw_research.experiment_runner plan configs/scenarios/synthetic_small.json
python -m vfw_research.experiment_runner run configs/scenarios/synthetic_small.json --output-root artifacts --batch-id my-pilot-001
```

The command creates 27 immutable raw records (three paired seeds across nine policies), then derives a JSON summary, CSV table, and SVG action chart. Batch IDs cannot be reused, preventing silent overwrite. Raw and generated artifacts are ignored by Git; the scenario, schemas, code, and tests are tracked.

The JSON summary also reports seed-paired differences in **decision rates** between the full controller and each baseline. Those differences are not QoS or migration-benefit measurements.

To rebuild outputs independently from existing raw records:

```powershell
python -m vfw_research.experiment_runner summarize artifacts/raw/my-pilot-001 artifacts/processed/my-pilot-001-rebuilt
```

See `docs/data_provenance.md` and `docs/completion_gap_matrix.md` for the evidence boundary and remaining publication work.

On Ubuntu/WSL2, the supervised live scaling smoke test is:

```bash
sudo bash scripts/dual_vfw_testbed.sh test-scaling
```

It creates and cleans up only the project-labelled namespaces and test processes. Its reported `1 -> 2 -> 1` sequence is a controlled functional result, not a throughput benchmark.

The separate same-flow route-transition and refusal tests are documented in `docs/route_migration_lab.md`:

```bash
sudo bash scripts/route_migration_lab.sh run
sudo bash scripts/route_migration_lab.sh test-no-seen-reply
sudo bash scripts/route_migration_lab.sh test-policy-mismatch
sudo bash scripts/route_migration_lab.sh test-rollback
```

To repeat and preserve live success/fault/scaling smokes on Linux or WSL2 as root:

```bash
sudo python3 scripts/live_fault_batch.py --output-directory artifacts/raw/my-live-batch --repeats 2
```

Each trial writes its output, status and post-run namespace cleanup check to an immutable JSON file. This is functional regression evidence, not a statistically powered performance study.

## Reproduce a synthetic held-out forecast evaluation

```powershell
$env:PYTHONPATH = "src"
python -m vfw_research.forecast_evaluation --family held_out_shift --seed 7 --output artifacts/raw/forecast-held-out-shift-seed7.json
```

This creates one exclusive-write JSON record with a chronological 144/48/48 train/calibration/test split, trace digest, MAE, RMSE, interval coverage and width for each model. Choose a new output filename for each run. The trace is synthetic; this command does not produce a network or publication comparison.

For a descriptive multi-seed synthetic pilot:

```powershell
$env:PYTHONPATH = "src"
python -m vfw_research.forecast_batch --output-directory artifacts/raw/my-forecast-pilot --seeds 0 1 2 3 4 5 6 7 8 9
```

This saves every family/seed record and a derived paired summary. It is not a final statistical result or real traffic measurement.

For the separate historical MAWI forecast pilot, review the [MAWI research/privacy terms](https://mawi.nezu.wide.ad.jp/mawi/guideline.txt) and [exact capture page](https://mawi.nezu.wide.ad.jp/mawi/samplepoint-B/2000/200012281400.html). Download the `.dump.gz` into ignored `artifacts/raw/`, then run:

```powershell
$env:PYTHONPATH = "src"
python -m vfw_research.mawi_trace --pcap artifacts/raw/mawi-200012281400.dump.gz --source https://mawi.nezu.wide.ad.jp/mawi/samplepoint-B/2000/200012281400.dump.gz --csv artifacts/raw/mawi-200012281400-1s.csv --provenance artifacts/raw/mawi-200012281400-1s.provenance.json
python -m vfw_research.forecast_evaluation --trace-csv artifacts/raw/mawi-200012281400-1s.csv --provenance artifacts/raw/mawi-200012281400-1s.provenance.json --output artifacts/raw/mawi-200012281400-forecast.json
```

Outputs are exclusive-write and Git-ignored; use fresh names when repeating. This converts only packet-header lengths into a traffic-rate series. It does not replay traffic through the vFW or evaluate migration. See `docs/data_provenance.md` and `docs/verification_log.md` for the pilot's checksum, measured source counts, metrics and limits.

The [exploratory trace-driven decision pilot](docs/trace_driven_decision_pilot.md) passes the held-out MAWI rate series through each controller policy using modeled non-traffic inputs:

```powershell
python -m vfw_research.trace_decision_eval --trace-csv artifacts/raw/mawi-200012281400-1s.csv --provenance artifacts/raw/mawi-200012281400-1s.provenance.json --scenario configs/scenarios/synthetic_small.json --output artifacts/raw/mawi-decisions-new-run.json
```

It records independent decisions only; `COMMIT` in this output is a controller decision, not an executed migration. The fixed scenario uncertainty limit produced `WAIT` on every held-out opportunity for the already-warm full policy, so this pilot does **not** show a migration benefit.

## Linux namespace packet-path test

The initial real networking gate intentionally uses transparent Linux primitives before container packaging. See `docs/testbed.md`:

```bash
sudo bash scripts/testbed.sh up
sudo bash scripts/testbed.sh test
sudo bash scripts/testbed.sh down
```
