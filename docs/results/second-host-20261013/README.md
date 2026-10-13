# Native-Linux second-host reproducibility check

The design in `../../second_host_replication_protocol.md` was committed on 2026-10-12, before this second-host run. The owner reported using a different physical device running native CachyOS (`7.2.9-2-cachyos`), Python 3.14.8, nftables 1.1.7, iproute2 7.2.0 and conntrack 1.4.9. Device independence is owner-attested, not established by the preflight script or a hardware identity record. The checkout was clean at `3951e33e500c6281587630fd88491ead1ec1f581`; its 152 unit tests and read-only preflight passed after installation of `conntrack-tools`.

The owner supplied `second-host-20261012-v1-evidence.tar.gz` on 2026-10-13. Its SHA-256 is `01b2134367d27caa87078e248dab4b060c2cb157de1e6fa3ca459931672f4434`. The 4,644,651-byte archive contained 255 safe relative entries, including all three raw batches, 18 trial records and their paired endpoint captures, exact executed-source archives, and the three processed output sets. The raw archive is retained outside Git; neither original public trace captures nor credentials were included. The common source/config digest is `97809f78db7b0a064fe4065c31d839f3663374f89a9504d37638ad01b46ea81e`.

On the development computer, the archive was unpacked into an ignored evidence folder and `vfw_research.live_analysis` was rerun independently for each family. All three regenerations passed complete-record, source-snapshot, capture-hash and endpoint-matching checks. Their `summary.json`, `trial_metrics.csv` and `results.md` files matched the supplied processed files byte-for-byte. All 18 records were completed with no residual owned namespaces. Every capture reported zero kernel drops and zero receiver-only unmatched instances. This verifies internal artifact consistency; it cannot independently authenticate which physical computer executed the trials.

## Descriptive outcomes

Three fixed seeds (191, 193, 197), three flows and 12 demand steps were run for each synthetic family. Full and reactive each made one physical route commit in every trial, and all application requests completed. Means are across the three seed repetitions within each family; they are not independent workload samples. The bootstrap intervals below are descriptive, not confirmatory superiority tests.

| Family | Full goodput (Mbps) | Reactive goodput (Mbps) | Paired full − reactive (Mbps) | Descriptive paired interval (Mbps) | Full/reactive mean trial p95 RTT (ms) |
|---|---:|---:|---:|---:|---:|
| Step | 1.087176 | 1.154560 | -0.067384 | [-0.081195, -0.040493] | 76.591 / 22.459 |
| Bursts | 0.906415 | 0.966261 | -0.059846 | [-0.072976, -0.036311] | 76.586 / 18.115 |
| Flash | 0.765021 | 0.830272 | -0.065251 | [-0.069192, -0.062992] | 90.980 / 2.828 |

Endpoint matching found nonzero packet-instance deficits and repeated payload-sequence instances in all 18 trials despite zero application request failures. Across three repetitions per family, full/reactive forward and reverse *missing instance counts* were: step 19/19 forward and 12/12 reverse; bursts 9/18 forward and 8/11 reverse; flash 20/25 forward and 12/6 reverse. These are capture-point deficits under differing amounts of delivered traffic, **not** a universal packet-loss rate or a policy ranking on loss.

This second-device check reproduces the executable pipeline and another unfavorable full-versus-reactive comparison on synthetic workloads. Because both policies committed in every trial, the observed goodput/latency gap is not explained solely by the no-commit uncertainty-gate failure seen in the Cyber4OT PLC-port development traces. The exact cause of the gap is not isolated. It does not provide an unseen real workload, a physical cross-host migration, measured emissions or security benefit, complete TCP-state equivalence, or a general performance conclusion. Preserve this negative result in any manuscript or artifact release.
