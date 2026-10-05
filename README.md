# Uncertainty-Gated Predictive Warm Migration for Carbon- and Attack-Risk-Aware Stateful Virtual Firewall Placement

This repository is a software-only, publication-oriented NFV/SDN research prototype. It is being built from the locked seven-function specification in `../RESEARCH_VFW_MASTER_BUILD_PROMPT.md`.

## Current verified status

- **Stage 0:** specification artifacts drafted and traceability established.
- **Stage 1:** deterministic controller core implemented with standard-library tests.
- **Stage 2:** Linux-namespace/nftables testbed implemented and smoke-verified on WSL2; see `docs/verification_log.md` for the evidence boundary.
- **Stage 3:** scaling and flow-affinity controller cores implemented; real multi-vFW integration remains pending.
- **Stage 4:** migration state machine, digest-verified reference state adapter, and kernel conntrack tuple insertion verified; route transition and seamless flow continuity remain pending.
- **Stage 5:** transparent rolling-mean split-conformal forecasting baseline implemented; research-trace training/calibration remains pending.
- **Stage 6:** carbon estimation, explainable risk scoring, constrained placement, and adaptive benefit core implemented; comparative experiments remain pending.
- **Stage 7:** invariant validation and idempotent logical fallback implemented; controlled target failure and new-flow source-path restoration smoke-verified, while established-flow recovery remains pending.
- **Stage 8:** common baseline-policy interface and immutable result schema implemented; repeated comparative experiments and publication figures remain pending.
- No comparative performance, carbon, migration, novelty, or publication result is claimed yet.

The repository contains both a deterministic decision harness and a real kernel-enforced single-vFW smoke test. It does not yet demonstrate complete state-consistent warm migration or flow continuity; see `docs/state_migration.md` for the evidence levels.

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

## Linux namespace packet-path test

The initial real networking gate intentionally uses transparent Linux primitives before container packaging. See `docs/testbed.md`:

```bash
sudo bash scripts/testbed.sh up
sudo bash scripts/testbed.sh test
sudo bash scripts/testbed.sh down
```
