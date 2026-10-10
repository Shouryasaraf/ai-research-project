# Independent-source Cyber4OT transfer pilot — frozen development protocol

Written before converting or analyzing `Cyber4OT_003.pcapng` or running its paired live trials. This is a **development transfer pilot**, not a journal confirmatory experiment. The one Linux host is Ubuntu WSL2 on the current Windows PC. The dataset is a different publisher and 2024 simulated industrial network, not a production Internet vFW workload or an independent host.

## Source and privacy

- Publisher: Warsaw University of Technology, *Cyber4OT* version 1.0.0, published 2024-11-05, DOI `10.5281/zenodo.13935639`.
- Archive: `Cyber4OT.zip`, publisher MD5 `55510cbb43d8af72a69dfbcd6940daa5`, locally computed SHA-256 `052565128073afcf2cc92d758be3dc644e842698c6d24ebe758aae3601bce6b6`.
- Embedded license: CC BY-NC 4.0. Cite dataset creators; keep the archive and derived trace under Git-ignored `artifacts/raw/`. Do not publish original packets in this repository.
- The public Zenodo file required no access form, whitelisted IPv4 submission or account. Ordinary HTTPS download still discloses a connection IP to its host. No live packet content or destination from the archive is transmitted or replayed.
- `Cyber4OT_001.pcapng` was used only to test the PCAPNG converter before this protocol. Its observed packet count and rate series are development information, excluded from held-out conclusions.

## Fixed workload and policies

1. Convert **only** `traces/Cyber4OT_003.pcapng` to one-second original-wire-length Mbps bins with `vfw_research.pcapng_rates`; record ZIP, member and CSV SHA-256. The dataset README identifies files 001–003 as normal traffic from the central switch; 003 is the approximately 15-minute member. If the parser fails strict validation, retain the failure and do not substitute a more favorable file under this protocol.
2. Use the existing runner's chronological 60/20/20 within-trace train/calibration/test split. Scale all segments using the training-only 90th-percentile reference as implemented; use the **first 30 held-out seconds** as generated TCP echo payload-rate demand. This is rate-derived traffic, not original Modbus or attack packet replay. Forecast and controller implementation remain unchanged after this freeze.
3. Run exactly five paired seeds `61 67 71 73 79`, policies `full_proposed_controller` and `reactive_threshold`, `--steps 30 --flows 3 --capture`, on the same isolated six-namespace topology. Order is deterministically shuffled by seed. A fresh exclusive batch path, source snapshot, raw records and endpoint captures are mandatory. No optional early stopping based on outcomes.

## Outcomes and validity

- Primary descriptive contrast: paired full-minus-reactive completed-request goodput (Mbps), reporting all five differences, mean and descriptive uncertainty interval. No superiority test or generalization claim is prespecified for this transfer pilot.
- Secondary: failed requests, route commits, p95 successful-request RTT, forward/reverse endpoint packet-instance deficits, sender-side TCP RST and repeated payload-sequence instances. Packet deficits are observed counts, not a general loss probability; response-free brackets include pacing and are not exact outage.
- Every trial must have a completed raw record, matching source/config/trace digests, valid capture hashes and endpoint packet matching, zero capture-kernel drops and no residual owned namespaces. An infrastructure failure stops the batch; preserve the attempt, then investigate and rerun only under a new versioned protocol/batch. Application failures are retained outcomes.
- Carbon, security risk, target resources and benefit values remain modeled. No emissions, attack-prevention, full TCP-state equivalence, zero-loss, or production-recovery claim follows from this experiment.

## Commands after source freeze

```sh
PYTHONPATH=src python3 -m vfw_research.pcapng_rates --archive artifacts/raw/cyber4ot-2024-v1/Cyber4OT.zip --member traces/Cyber4OT_003.pcapng --csv artifacts/raw/cyber4ot-2024-v1/normal-003-1s.csv --provenance artifacts/raw/cyber4ot-2024-v1/normal-003-1s.provenance.json
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/live-cyber4ot-captured-pair-20261010-v1 --seeds 61 67 71 73 79 --policies full_proposed_controller reactive_threshold --steps 30 --flows 3 --capture --trace-csv artifacts/raw/cyber4ot-2024-v1/normal-003-1s.csv --provenance artifacts/raw/cyber4ot-2024-v1/normal-003-1s.provenance.json
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/live-cyber4ot-captured-pair-20261010-v1 artifacts/processed/live-cyber4ot-captured-pair-20261010-v1
```

If `--steps 30` exposes an infrastructure-only runner bug, preserve the failed attempt; do not modify the controller, primary outcome or workload slice without publishing a protocol amendment first. The independently sourced workload still comes from a simulated testbed and a single selected trace, so a later journal study needs broader held-out sources and a separately frozen confirmatory analysis.
