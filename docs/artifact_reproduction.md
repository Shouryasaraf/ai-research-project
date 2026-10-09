# Reviewer reproduction guide

Run from the repository root. Python 3.11+ and the Python standard library suffice for the non-privileged tests. Raw outputs are intentionally ignored by Git; retain them separately when sharing an artifact. No software license is granted by this guide.

## Fast checks

PowerShell:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -q
```

Linux:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -q
```

## Live paired pilot

Use a disposable Linux/WSL environment with root permissions, network namespaces, nftables, conntrack, iproute2 (including tc), and Python. This manipulates only the named isolated lab topology, but must not run on a production network host. Do not run two lab scripts concurrently. The batch detects collisions and requires fresh output paths; it does not delete old evidence.

```sh
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/reviewer-live-pilot --seeds 7 11 19 --steps 12 --flows 3
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/reviewer-live-pilot artifacts/processed/reviewer-live-pilot
```

This runs nine policies on three identical paired synthetic demand schedules. Expect several minutes. Each trial retains traffic events, forecasts, actions, supported conntrack validation, interface/qdisc snapshots, environment versions and code/config hashes. Application failures are outcomes, not infrastructure failures. The cold baseline deliberately omits state copying inside the isolated lab.

For a trace-derived pilot, supply `--trace-csv PATH --provenance PATH` to the batch. The adapter validates provenance; scaling uses training data only. This replays demand rates as generated TCP echo payloads, not original packets or attacks. Respect the source's access and redistribution terms; do not publish raw MAWI captures.

## Interruptions and reproducibility

Use `--resume` with exactly the same arguments only when all existing trial directories contain completed records. Code/config/trace changes reject resume. Incomplete or failed trials are preserved: inspect them and start a newly named batch. The process watchdog and normal exit attempt cleanup; after an uncatchable host/process crash inspect `ip netns list` before manually cleaning only the owned `vfwlab3-*` lab with `bash scripts/route_migration_lab.sh down`.

Analysis output paths must also be new. Regenerate outputs from raw records, never edit a result to improve it. Preserve the batch manifest together with every trial directory. A Git revision alone is insufficient when the checkout is dirty; the recorded code digest identifies executed source bytes.

## Interpretation limits

Active recovery with generated-traffic captures:

```sh
sudo env PYTHONPATH=src python3 scripts/active_recovery_probe.py --output artifacts/raw/reviewer-active-recovery --capture
PYTHONPATH=src python3 -m vfw_research.recovery_report --batches artifacts/raw/reviewer-active-recovery --output artifacts/processed/reviewer-active-recovery
```

This additionally requires the already-used tcpdump and ethtool tools. The report reads both endpoint PCAPs and verifies recorded hashes. For local reproduction archives, `scripts/build_research_artifact.py --include-lab-captures` opts in only to matching, scope-attested generated lab captures. It never opts in to the original MAWI capture. The fault acceptance contract is in `active_recovery_protocol.md`; packet assumptions and invalid-attempt history are in `packet_capture_protocol.md`.

For the bounded proxy lifecycle, run `PYTHONPATH=src python3 scripts/live_lifecycle_probe.py --output artifacts/raw/reviewer-lifecycle` as root, then `PYTHONPATH=src python3 -m vfw_research.lifecycle_report --records artifacts/raw/reviewer-lifecycle/record.json --output artifacts/processed/reviewer-lifecycle`. The exact demand mapping and evidence limits are in `lifecycle_probe_protocol.md`.

Additional checks: `docs/restart_containment.md` describes real process-interruption probes, and `docs/sensitivity_protocol.md` describes the modeled parameter grid. `python scripts/live_campaign.py --output artifacts/raw/reviewer-campaign` prints a read-only multi-family plan; add `--execute` only in the isolated Linux/root environment. Use `--seeds`, `--families`, `--policies`, `--steps` and `--flows` to declare a campaign before running it. The latest batch runner archives executed source/config files as `executed-source.zip`; earlier pilots retain hashes only, so their exact uncommitted source snapshot is not recoverable from a hash alone.

These are short, single-host development pilots, not confirmatory or physical multi-host benchmarks. Carbon, risk and CPU/memory headroom inputs are modeled. Completed-request goodput can understate offered demand during congestion. Echo RTT is not one-way latency. Request failures are not packet loss; response gaps include pacing and are not exact migration downtime. Conntrack checks cover tuples and supported flags, not full TCP window/sequence equivalence. Both routes are updated sequentially, not atomically. See `live_experiment_protocol.md` before interpreting comparisons.
