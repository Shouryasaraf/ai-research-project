# Predictive proxy lifecycle integration probe

This is a functional witness, not a comparative benchmark. Two persistent source connections supply observed flow occupancy. Each active flow is assigned a modeled 1 Mbps resource requirement, with a modeled 2 Mbps source capacity. An EWMA model is initialized on explicit synthetic training/calibration fixtures and updated only from observed occupancy-derived demand. This is not measured traffic forecasting or calibrated real-world demand estimation.

The scaling manager must request scale-out before a predictive PREWARM can start the target firewall/backend. The same loop advances through source-pin checkpoint validation and a benefit-gated COMMIT. The live policy/health/telemetry guard revalidates before balanced new-flow admission. Two existing flows must remain on source, a new flow must reach target, and all flows must drain before target deactivation. A post-scale-in request must still reach source.

Cold-target prewarm decisions use modeled candidate readiness inputs; they cannot activate traffic. Actual live attestation is mandatory before admission. In this source-pinning mode, SYNC means validating the pinned-state checkpoint, not copying conntrack state. Transparent transferred-flow migration remains the distinct route backend; do not conflate the two mechanisms.

Bounded flow delays and observations test sequencing only. Failure retains the source before admission or aborts the disposable lab; automated post-admission recovery remains separately evaluated. No claim of a complete production lifecycle is made by this witness.

Run in the isolated Linux/WSL lab as root, with no other vfwlab scripts running:

```sh
PYTHONPATH=src python3 scripts/live_lifecycle_probe.py --output artifacts/raw/lifecycle-new-trial
PYTHONPATH=src python3 -m vfw_research.lifecycle_report --records artifacts/raw/lifecycle-new-trial/record.json --output artifacts/processed/lifecycle-new-trial
```

The output path must be new. The report rejects missing actuation, live guards, pinned/new flow observations, cleanup, unsupported conntrack-transfer claims, or a mismatched source snapshot. Six development repetitions and their raw hashes are in `results/lifecycle-20261009-snapshotted/`. The first three retain code fingerprints only; the later three include verified executed-source archives. Each is an execution of the same small scenario, not an independent workload sample.
