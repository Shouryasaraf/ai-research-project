# PDMFC independent-source, WSL development-host transfer

This result uses the [protocol frozen at `3b8d057`](../../pdmfc_confirmatory_protocol.md) before source download. The capture was independently published in the [PDMFC Zenodo record](https://doi.org/10.5281/zenodo.16943481). This particular execution was on the **development WSL2 host**, not the owner's separate native-Linux device required for the planned cross-device check. The record contains normal and attack-generated traffic, but only packet timestamp/original-length rates informed generated TCP echo demand; source payloads, endpoints, labels and attacks were not replayed. No inference about attack detection or risk reduction follows.

The exact selected file `packetcapture-em3-20250514160400.pcap` matched publisher MD5 `1029af538dee0e645f0b5ce1fc7464fd`; local SHA-256 was `4941c3260d2df10ccfaa13fd0d43f848bc96e86a0b52f4ee53e478360dd15c2c`. The strict classic-PCAP parser counted 682,166 packets and 111,106,112 summed original-length bytes between 2025-05-14 13:04:00.971935 and 13:17:12.040841 UTC. It produced 793 one-second bins with no internal zero-packet bins. The rate CSV SHA-256 was `d22b2316289c075fa5fb9ae8ce92ed369fb9534d8bfa13b287e25282560c15c3`; the sidecar SHA-256 was `1fc5d2970450dd0499968649b1ac9e9806ee00194c1911bc3c771a3fab7d5db7`. The chronological split yielded 475 training, 158 calibration and 160 held-out bins. The fixed live slice was 2025-05-14 13:14:33--13:15:02 UTC, the first 30 held-out bins. Original PCAP and derived rates remain ignored/private because the source record does not state redistribution rights.

The five-seed, three-policy, 30-step captured batch ran without outcome-based changes. The executed-source SHA-256 was `afa8c44215e4ce5a0a772c9e022b587d901913c217c2299d880655c0f30e948f`. All 15 records completed; endpoint capture hashes/matching and source/config digests validated, capture-kernel drops were zero and no owned namespaces remained. Windows reanalysis reproduced the 15 trial metrics byte-for-byte; JSON/Markdown presentations differed only in platform path separators and line endings. Both analyzers returned the same values. The ignored raw and processed directories are `artifacts/raw/pdmfc-2025-v1-wsl-development` and `artifacts/processed/pdmfc-2025-v1-wsl-development`.

A private 10,609,131-byte generated-evidence archive is retained at `artifacts/processed/pdmfc-2025-v1-wsl-evidence.tar.gz` (SHA-256 `8308f83b50a330fb185c949ec2104be24cf87170b0e21c3c2526ba8abfe7434b`). Its 178 entries include 30 **lab-generated** endpoint PCAPs required for packet reanalysis, but no original PDMFC capture or derived rate CSV. It is Git-ignored and must not be confused with public-release authorization.

## Descriptive outcome

| Policy | Mean completed goodput (Mbps) | Mean trial p95 successful RTT (ms) | Route commits / 5 | Request failures | Reverse endpoint missing instances |
|---|---:|---:|---:|---:|---:|
| Original full | 0.926898 | 93.157 | 0 | 0 | 0 |
| Experimental guard | 1.437022 | 84.414 | 5 | 0 | 48 |
| Reactive threshold | 1.500138 | 0.636 | 5 | 0 | 44 |

The paired full-minus-reactive mean was **-0.573240 Mbps** (descriptive five-seed bootstrap interval [-0.574408, -0.571485]); full-minus-guard was **-0.510124 Mbps** ([-0.510714, -0.509525]). Guard-minus-reactive mean was **-0.063116 Mbps**. These intervals quantify repeated execution on one 30-second rate slice, not independent workload uncertainty or a general superiority test.

| Seed | Full goodput | Guard goodput | Reactive goodput | Full / guard / reactive commits |
|---:|---:|---:|---:|---:|
| 211 | 0.926960 | 1.437918 | 1.496731 | 0 / 1 / 1 |
| 223 | 0.926871 | 1.436038 | 1.500416 | 0 / 1 / 1 |
| 227 | 0.926875 | 1.436989 | 1.500807 | 0 / 1 / 1 |
| 229 | 0.926893 | 1.437663 | 1.501072 | 0 / 1 / 1 |
| 233 | 0.926893 | 1.436505 | 1.501665 | 0 / 1 / 1 |

Each original-full trial recorded 29 uncertainty `WAIT` decisions and no transition. Its normalized interval width was fixed at approximately 1.3126 of source capacity, far above the 0.20 width gate. Each guarded trial recorded a `SYNC` and a `COMMIT` via the pre-existing liveness escape, committing at decision step 3; reactive committed at step 0. The guard therefore recovered a migration on an independently published high-width source that had not been used to design it, but it remained slower and lower-goodput than reactive in this lab. The extra three decision steps are a plausible contributor to trial-wide latency, not an isolated causal mechanism.

Full had no reverse packet-instance deficit because it never migrated; this is not evidence that it provides superior service or a general lossless path. Guarded and reactive trials recorded 48 and 44 reverse missing packet instances across five trials, respectively, and repeated payload-sequence instances occurred under all three policies. Zero application failures and zero capture-kernel drops coexist with these observations. Endpoint deficits are capture-point counts, not a general packet-loss probability, and the response gaps include pacing rather than exact migration downtime.

The separate native-Linux run and independent owner-supplied raw archive remain pending. This development-host result cannot establish cross-host migration, representative-workload generality, measured carbon or risk benefit, complete TCP-state equivalence, or publication readiness. Preserve this unfavorable original-full comparison and the guard's shortfall against reactive in subsequent reports.
