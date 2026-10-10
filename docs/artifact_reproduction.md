# Reviewer reproduction guide

The current same-host local archive snapshot is `artifacts/raw/research-vfw-lab-artifact-20261010-v4.zip` (SHA-256 `773362de3921594217100536d2fcd5721ae49e7b16ca844311dfd509bf8ad44a`). It contains 329 allowlisted files, including the finite-placement audit code, tests and tracked result plus 24 generated lab PCAPs. It excludes original/derived MAWI traffic and NESO responses. A fresh extraction without Git passed 133 non-privileged tests on the same host. This is package QA, not independent-host reproduction or permission to redistribute the archive.

The newer Git-ignored local `artifacts/raw/research-vfw-lab-artifact-20261010-v5.zip` (SHA-256 `4f40a117349cf8d08c001b0c84c22cf58d7b6eb6ac204da92ab86fc55ff906b9`) adds the protocol-frozen Cyber4OT lab pair. It contains 440 allowlisted files and 44 generated lab endpoint PCAPs; no original/derived Cyber4OT, MAWI or NESO traffic is included. The larger captured batch used the artifact builder's explicit `--max-uncompressed-mib 300` override; the default remains 100 MiB, and the override requires attested lab captures. Same-host fresh extraction passed 137 tests, and regenerated Cyber4OT live and TCP-wire summaries matched the tracked JSON bytes. Neither archive is an independent-host reproduction or a redistribution license.

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

To validate capture sensitivity itself, run `sudo env PYTHONPATH=src python3 scripts/packet_capture_validation.py --output artifacts/raw/reviewer-packet-controls --repetitions 2`, then `PYTHONPATH=src python3 -m vfw_research.packet_validation_report --batch artifacts/raw/reviewer-packet-controls --output artifacts/processed/reviewer-packet-controls`. The script confines the deliberate drop to the owned firewall namespace and removes it before teardown. It stops on any invalid or failed control and preserves the raw attempt.

For paired captured migration, add `--capture --policies full_proposed_controller reactive_threshold --seeds 47 53 59` to a fresh `scripts/live_experiment_batch.py` invocation, then run the regular `vfw_research.live_analysis` command. The analyzer verifies the exact source snapshot, PCAP hashes and packet matching before generating tables. `docs/captured_live_protocol.md` records the development design and interpretation limits.

The local second-MAWI **lab-only** archive `artifacts/raw/research-mawi2005-lab-artifact-20261010-v2.zip` was tested after extraction into a fresh same-host directory. It contains 251 code/doc/evidence files and 12 attested generated endpoint PCAPs, but excludes the original MAWI capture, derived traffic CSV and sidecar. Archive SHA-256 is `b1cc1782bb2c7deef8991dd12298b09f7d075c93039e4653a82a999be8d8ff93`. In the extracted directory, all 124 non-privileged tests passed, and rerunning `PYTHONPATH=src python -m vfw_research.live_analysis artifacts/raw/live-mawi2005-captured-pair-20261010-v1 artifacts/processed/reproduced-mawi2005` produced a `summary.json` byte-for-byte identical to `docs/results/live-mawi2005-captured-pair-gap-20261010-v2/summary.json` (SHA-256 `e145f9fa03e39c80d076475cc67dfb28f4517aefe502d95ad527056ad869d9f9`). This is a **same-machine fresh-extraction** check, not independent-host reproduction or permission to redistribute the archive.

The newer combined local archive `artifacts/raw/research-vfw-lab-artifact-20261010-v3.zip` contains 326 allowlisted files, including 24 generated endpoint PCAPs from both three-seed captured batches; SHA-256 `a1f252a2e420e19d213672dc80f847430ac690f9aefff884b6b2ab0089d7812c`. It excludes original/derived MAWI traffic and NESO API responses/CSVs. After fresh same-host extraction, 129 tests passed; two live summaries and two TCP wire-diagnostic summaries were regenerated from packaged records/captures with hashes byte-identical to the four tracked summaries. This validates package completeness for those analyses only, not a second host or permission to release the archive.

For the bounded proxy lifecycle, run `PYTHONPATH=src python3 scripts/live_lifecycle_probe.py --output artifacts/raw/reviewer-lifecycle` as root, then `PYTHONPATH=src python3 -m vfw_research.lifecycle_report --records artifacts/raw/reviewer-lifecycle/record.json --output artifacts/processed/reviewer-lifecycle`. The exact demand mapping and evidence limits are in `lifecycle_probe_protocol.md`.

Additional checks: `docs/restart_containment.md` describes real process-interruption probes, and `docs/sensitivity_protocol.md` describes the modeled parameter grid. `python scripts/live_campaign.py --output artifacts/raw/reviewer-campaign` prints a read-only multi-family plan; add `--execute` only in the isolated Linux/root environment. Use `--seeds`, `--families`, `--policies`, `--steps` and `--flows` to declare a campaign before running it. The latest batch runner archives executed source/config files as `executed-source.zip`; earlier pilots retain hashes only, so their exact uncommitted source snapshot is not recoverable from a hash alone.

These are short, single-host development pilots, not confirmatory or physical multi-host benchmarks. Carbon, risk and CPU/memory headroom inputs are modeled. Completed-request goodput can understate offered demand during congestion. Echo RTT is not one-way latency. Request failures are not packet loss; response gaps include pacing and are not exact migration downtime. Conntrack checks cover tuples and supported flags, not full TCP window/sequence equivalence. Both routes are updated sequentially, not atomically. See `live_experiment_protocol.md` before interpreting comparisons.
