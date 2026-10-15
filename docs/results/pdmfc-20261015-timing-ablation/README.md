# PDMFC secondary-segment fixed-timing ablation on WSL2

This **exploratory development-host** run followed the protocol frozen in commit `820f5b0` (`docs/pdmfc_timing_ablation_protocol.md`). It used the second 30-second held-out segment (test offset 30) from the same PDMFC source, five predeclared seeds, four shuffled policies, three TCP flows and paired endpoint captures. It is not a new independent source or a native-Linux replication of this ablation. The source rate CSV SHA-256 was `d22b2316289c075fa5fb9ae8ce92ed369fb9534d8bfa13b287e25282560c15c3`; the sidecar SHA-256 was `1fc5d2970450dd0499968649b1ac9e9806ee00194c1911bc3c771a3fab7d5db7`. The manifest code digest was `efdaec052de2ee9f39a9057660feff9ba1921e8750610de1f303c6c4d3b31cce`, and the executed-source ZIP SHA-256 was `2491b163235fdba00bc4cc49de7b1a80f012e51948bc366319f4ffa89f2617eb`. The raw and processed directories under `artifacts/` are Git-ignored; no original PDMFC capture or derived rate CSV is committed.

The clean-checkout WSL preflight passed, and 156 unit tests passed before the experiment. All 20 trial records completed; `live_analysis` validated their captured endpoints and produced the metrics below. The separate `tcp_wire_diagnostic` validated all 20 raw trials. No owned namespace was left behind. The environment was Ubuntu WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, not the owner's separate native-Linux device.

| Policy | Mean completed-request goodput (Mbps) | Mean trial p95 successful RTT (ms) | Commits / 5 | Failed requests | Forward/reverse capture-point missing packet instances |
|---|---:|---:|---:|---:|---:|
| Original full controller | 0.929533 | 96.749 | 0 | 0 | 0/0 |
| Reactive threshold | 1.437896 | 0.590 | 5 | 0 | 0/44 |
| Experimental liveness guard | 1.383162 | 79.160 | 5 | 0 | 0/56 |
| Experimental fixed-timing reactive | 1.382058 | 79.163 | 5 | 0 | 0/57 |

The **predeclared guard-minus-fixed-timing-reactive** paired goodput differences (Mbps) were: seed 311 `+0.000609`, 313 `+0.000228`, 317 `-0.000603`, 331 `+0.000975`, and 337 `+0.004310`; mean **+0.001104 Mbps**. In every pair, both arms chose `SYNC` at decision step 2 and `COMMIT` at step 3, with two measured state-sync operations and one route commit. Their mean cumulative state-sync times were 0.08475 s (guard) and 0.08967 s (delayed reactive). Thus the protocol's timing-match interpretation condition was met on all five pairs.

Ordinary reactive committed at step 0 with one state-sync operation in all five runs. The experimental guard-minus-ordinary-reactive mean was **-0.054734 Mbps**; fixed-timing reactive-minus-ordinary-reactive was **-0.055838 Mbps**. This is consistent with timing and extra synchronization explaining much of the *small guard-versus-reactive gap in this particular segment*. It is not a general causal decomposition: this control changes the reactive schedule, the workload is closed-loop and response-gated, and both delayed arms were designed using timing seen on the already-inspected first segment.

The unchanged full controller made 145 `WAIT` decisions, never synchronized or committed, and averaged **-0.508363 Mbps** versus ordinary reactive. That large original-policy deficit is a distinct high-uncertainty liveness issue; it is not explained away by the close guard-versus-delayed-reactive match. No application requests failed and no sender RST was observed in these lab captures, but reverse capture-point packet-instance deficits and repeated payload sequences remain. Those observations do not prove lossless migration or complete TCP-state equivalence. Carbon and attack risk remained modeled, not measured.

The five seeds repeat one 30-second rate slice. Any narrow repeated-trial interval would describe run-to-run variation only, not uncertainty across network workloads. The next external gate is replication of this **frozen** ablation on the owner's separate native-Linux host without modifying code, protocol, source selection or seeds.
