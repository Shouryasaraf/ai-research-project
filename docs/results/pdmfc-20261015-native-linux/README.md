# Frozen PDMFC transfer check on the owner's native-Linux device

The selection and endpoint were frozen in `docs/pdmfc_confirmatory_protocol.md` before the selected source was downloaded. This is a transfer check on one independently published traffic source, not a blinded confirmation of the original hypothesis or a sample of independent workloads. The device is reported by the owner as separate; physical independence is not established by the preflight script.

## Evidence received and independently checked

The private archive received on 2026-10-15 was `pdmfc-2025-v1-evidence.tar.gz`, 10,694,828 bytes, SHA-256 `53acfbb85f0b5303cf1cd2255f62bd6fee22a28a3c602ad9067c1bb4c6dea664`. It is not committed because it contains generated endpoint captures. The archive has 181 entries, including 15 trial records and 30 lab-generated endpoint PCAPs. Inspection found no symlinks, traversal paths, original PDMFC source capture, or derived source rate CSV. All 15 raw record hashes matched the archived summary. Every record carries the manifest code SHA-256 `afa8c44215e4ce5a0a772c9e022b587d901913c217c2299d880655c0f30e948f`; the manifest has the frozen five seeds, three policies, 30 steps, three flows, paired capture and source-rate SHA-256 `d22b2316289c075fa5fb9ae8ce92ed369fb9534d8bfa13b287e25282560c15c3`.

Re-running `vfw_research.live_analysis` from the extracted raw archive reproduced all 15 trials, the primary paired mean, and a byte-identical `trial_metrics.csv`. The attached screenshot reports a passing native-CachyOS preflight and 154 tests, zero capture-kernel drops, no residual owned namespaces, publisher MD5 match, and Git revision `9116e0b`; those host-side assertions are owner-supplied, not independently proven by the archive. The source sidecar in the archive reports PCAP SHA-256 `4941c3260d2df10ccfaa13fd0d43f848bc96e86a0b52f4ee53e478360dd15c2c`. The original source PCAP is absent, so its hash cannot be independently recalculated from this bundle.

## Frozen primary result

The original full controller had lower completed-request goodput than reactive threshold in every paired seed. The mean full-minus-reactive difference was **-0.574097 Mbps**, with the descriptive paired bootstrap interval **[-0.574993, -0.573375] Mbps**. These five executions reused one 30-second held-out source slice; the narrow interval is not an uncertainty interval across traffic sites or workload samples.

| Policy | Mean goodput (Mbps) | Mean trial p95 successful-request RTT (ms) | Route commits / 5 | Failed requests |
|---|---:|---:|---:|---:|
| Original full controller | 0.926871 | 93.235 | 0 | 0 |
| Reactive threshold | 1.500968 | 0.464 | 5 | 0 |
| Experimental liveness guard | 1.437630 | 84.529 | 5 | 0 |

The experimental guard improved goodput over original full by 0.510759 Mbps but remained 0.063337 Mbps below reactive. It is an ablation, not the original submitted policy. Raw decision records show 145 full-policy `WAIT`s and no full commit; reactive committed once per seed; the guard synchronized and committed once per seed. The result corroborates the predicted high-uncertainty wait/liveness failure mode on this finite slice. It does not show that the guard is generally safe or superior.

Archived endpoint-capture analysis recorded forward/reverse packet-instance deficits of 0/0 for full (which did not migrate), 27/22 for reactive, and 31/20 for guard. All policies had zero failed application requests in these runs. No sender RST was observed, but repeated payload sequences occurred. Capture-point deficits are not a universal packet-loss rate; absence of RST and request failure does not prove complete TCP-state equivalence or lossless migration.

## Claim boundary and next experiment

This result adds a native-Linux replication of a **negative** fixed-policy comparison on a preselected newer source. It does not establish general controller advantage, physical cross-host migration, measured carbon/emissions, attack-risk reduction, or complete TCP-state correctness. The most useful next controlled experiment is a predeclared matched-timing ablation that separates uncertainty-gate delay from state-sync and route-transition cost, using a fresh workload or held-out segment and reporting all arms, including failures. Do not retune this already inspected slice and call it confirmatory.
