# Predeclared PDMFC independent-source transfer check

Frozen in commit `3b8d057` on 2026-10-13 **before downloading or inspecting the selected capture**. A later text-only addition gives evidence-packaging commands; it changes no source choice, workload, policy, seed, endpoint or stopping rule. This checks the unchanged controller on one newer, independently published traffic source and on the owner's separate native-Linux device. It is not a production firewall deployment, an attack-replay experiment, or a statistically representative sample of network sites. The existing controller, experimental liveness guard and full/reactive outcomes on other sources have already been inspected; this is therefore a predeclared *transfer check*, not a pristine blinded confirmation of the original research hypothesis.

## Source and immutable selection

- Dataset: [PDMFC, Zenodo record 16943481](https://doi.org/10.5281/zenodo.16943481), published 2025. Select **only** `packetcapture-em3-20250514160400.pcap` (the file named in the committed converter). Publisher MD5: `1029af538dee0e645f0b5ce1fc7464fd`. Record computed SHA-256. If unavailable, malformed, out of order or too short, preserve the failed attempt; do not substitute another member or change the slice under this protocol.
- The record does not state a redistribution license. Keep original packets and derived rates Git-ignored and local; do not include either in public artifacts without a separate rights review. Ordinary HTTPS retrieval discloses a connection IP to Zenodo. The converter examines classic-PCAP timestamps and original wire lengths, not packet contents, addresses or attack labels. No original traffic, endpoints or attacks are replayed.
- Convert to one-second sums of the PCAP's original packet-length field, expressed as Mbps, filling only internal empty seconds with zero. This field is not a direct measurement of physical-link overhead. Use the existing chronological 60/20/20 train/calibration/test split and training-only scaling. The **first 30 held-out seconds**, with no result-based change, drive generated TCP echo payload rates. Require at least 30 valid held-out bins. All five repetitions reuse that same time slice and are not independent workloads.

## Fixed native-Linux experiment

- Run after clean checkout, preflight and 152+ unit tests on the owner's separate native-Linux host. Use the existing six-namespace isolated lab, three persistent TCP flows, 30 one-second demand steps and endpoint captures.
- Main policies: `full_proposed_controller` and `reactive_threshold`, paired at seeds `211 223 227 229 233`. The batch runner shuffles within-seed execution order. A separate, clearly labeled exploratory third arm `full_liveness_guarded_experimental` is included to test whether its escape activates on this unseen source; it is not a replacement for full and does not redefine the main contrast.
- Primary descriptive endpoint: paired full-minus-reactive completed-request goodput (Mbps); report every seed difference, the mean and descriptive interval. Secondary: experimental guard-minus-full difference and activation/commit counts, failed requests, trial-wide p95 successful-request RTT, source/target route commits, forward and reverse endpoint packet-instance deficits, sender TCP RST, repeated payload sequences and safety/readback checks. No outcome-dependent early stopping or parameter adjustment.
- Required validity: all 15 trial records completed; exact source snapshot and config/trace hashes; valid paired endpoint captures with zero capture-kernel drops; no residual owned namespaces. Application failures remain outcomes. Infrastructure or safety failure stops the batch, preserves all files and requires a new named attempt after documented repair.
- This test cannot measure power/carbon, attack-risk reduction, complete TCP state equivalence, precise outage, or cross-machine migration. It cannot by itself establish general policy superiority or novelty. Report negative results prominently.

## Reproduction on the second Linux device

Run from a clean checkout containing this protocol. The URL and file name are fixed above. The source and generated data stay under ignored `artifacts/raw/`. No credentials or CAIDA access are needed.

```sh
mkdir -p artifacts/raw/pdmfc-2025-v1 artifacts/processed
curl --fail --location --retry 3 'https://zenodo.org/records/16943481/files/packetcapture-em3-20250514160400.pcap?download=1' --output artifacts/raw/pdmfc-2025-v1/packetcapture-em3-20250514160400.pcap
printf '%s  %s\n' 1029af538dee0e645f0b5ce1fc7464fd artifacts/raw/pdmfc-2025-v1/packetcapture-em3-20250514160400.pcap | md5sum --check
sha256sum artifacts/raw/pdmfc-2025-v1/packetcapture-em3-20250514160400.pcap
PYTHONPATH=src python3 -m vfw_research.pdmfc_trace --pcap artifacts/raw/pdmfc-2025-v1/packetcapture-em3-20250514160400.pcap --csv artifacts/raw/pdmfc-2025-v1/rates-1s.csv --provenance artifacts/raw/pdmfc-2025-v1/rates-1s.provenance.json
bash scripts/independent_host_preflight.sh
PYTHONPATH=src python3 -m unittest discover -s tests -q
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/pdmfc-2025-v1-captured-pair --seeds 211 223 227 229 233 --policies full_proposed_controller reactive_threshold full_liveness_guarded_experimental --steps 30 --flows 3 --capture --trace-csv artifacts/raw/pdmfc-2025-v1/rates-1s.csv --provenance artifacts/raw/pdmfc-2025-v1/rates-1s.provenance.json
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/pdmfc-2025-v1-captured-pair artifacts/processed/pdmfc-2025-v1-captured-pair
```

After a completed analysis, package only the trial evidence and sidecar (not the source capture or rate CSV):

```sh
tar -czf pdmfc-2025-v1-evidence.tar.gz artifacts/raw/pdmfc-2025-v1-captured-pair artifacts/processed/pdmfc-2025-v1-captured-pair artifacts/raw/pdmfc-2025-v1/rates-1s.provenance.json
tar -tzf pdmfc-2025-v1-evidence.tar.gz
sha256sum pdmfc-2025-v1-evidence.tar.gz
git rev-parse HEAD
```

Inspect the `tar -tzf` list before transfer: it must contain no original PCAP, derived CSV, secrets or unrelated files. Send the archive privately with the preflight/test output and Git revision for independent reanalysis. Do not put the original capture or derived rates into a public repository.
