# Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement

This repository is a software-only, publication-oriented NFV/SDN research prototype. It is being built from the locked seven-function specification in `../RESEARCH_VFW_MASTER_BUILD_PROMPT.md`.

## Current verified status

- **Stage 0:** specification artifacts drafted and traceability established.
- **Stage 1:** deterministic controller core implemented with standard-library tests.
- **Stage 2:** Linux-namespace/nftables testbed implemented and smoke-verified on WSL2; see `docs/verification_log.md` for the evidence boundary.
- **Stage 3:** scaling and flow-affinity controller cores are connected to the proxy testbed. Three isolated runs verified telemetry-driven activation and deactivation of a second nftables vFW path, plus pinned source and new target flows. Broader load, fairness and SLA evaluation remains pending.
- **Stage 4:** migration state machine, reference state adapter, and kernel conntrack tuple insertion verified. A live guarded selector checks policy, target health, source-pinned conntrack state, and telemetry before admitting new target flows. Transferred-flow route transition and seamless flow continuity remain pending.
- **Stage 5:** rolling-mean and EWMA split-conformal forecasters plus chronological synthetic-trace evaluation implemented; one historical MAWI trace has been processed for a separate offline forecast pilot, not replayed through the vFW testbed.
- **Stage 6:** carbon estimation, explainable risk scoring, constrained placement, and adaptive benefit core implemented; comparative experiments remain pending.
- **Stage 7:** invariant validation and idempotent logical fallback implemented; the live proxy automatically restores the source for the next new flow after a target connect failure. Established target-flow recovery and proactive detection remain pending.
- **Stage 8:** common baseline-policy interface, validated scenario loader, immutable result schema, paired synthetic experiment runner, and generated JSON/CSV/SVG summaries implemented. A 27-record controller-only pilot validates the pipeline; packet-path comparative experiments and publication results remain pending.
- No comparative performance, carbon, migration, novelty, or publication result is claimed yet.

The repository contains a deterministic decision harness and real kernel-enforced vFW testbeds. It does not yet demonstrate complete state-consistent warm migration or general/quantified flow continuity; see `docs/state_migration.md` for the evidence levels.
An additional isolated route lab has now shown one established TCP connection continuing through a target firewall after a guarded conntrack-state import and two-sided route change. This is a narrow functional result, not proof of seamless migration, loss bounds, or end-to-end controller integration.

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

## Linux namespace packet-path test

The initial real networking gate intentionally uses transparent Linux primitives before container packaging. See `docs/testbed.md`:

```bash
sudo bash scripts/testbed.sh up
sudo bash scripts/testbed.sh test
sudo bash scripts/testbed.sh down
```
