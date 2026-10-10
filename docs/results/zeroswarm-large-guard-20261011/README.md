# Larger Zero-SWARM normal-file guard check

The [frozen protocol](../../zeroswarm_large_file_guard_protocol.md) was
committed at `f34ae37` before download. This is an exploratory **within-record
unseen-file** check of the experimental liveness guard, not independent-publisher
or independent-host confirmation. The publisher's [Zero-SWARM record](https://doi.org/10.5281/zenodo.15082260)
identifies `ZeroSWARM Normal data_v2.pcap` (232,217,247 bytes) and MD5
`eee8b87e62c482fd574b6e78d32cb12b`; the downloaded file matched both.
Its local SHA-256 was
`6f9b3e9228cc60e7b1130b790c11b187c5562bee5363f34f2e2da59c133540a3`.
The header-only converter counted 2,840,579 packets over 27,490 one-second
bins, including 89 internal zero-packet bins. The PCAP and derived rates remain
Git-ignored. No original Modbus messages, payloads, or addresses were replayed.

The earlier v2b capture spans 2025-03-05 16:05–16:38 UTC; v2 spans 2025-03-11
13:30–21:09 UTC, so their packet time ranges do not overlap. Their fixed
60/20/20 held-out slices start at 2025-03-05 16:31:51 and 2025-03-11
19:37:26 respectively, and zero of the first 30 rate values match at the
same position. These checks establish different observed time windows, not
independent laboratories or populations.

## Live result

Exactly five frozen seeds (137, 139, 149, 151, 157) completed for each of
three policies: 15/15 trials, 30 steps, three generated TCP echo flows,
endpoint captures. The [validated live table](live/results.md), [TCP-wire
table](tcp/results.md), and [strict pre/post-transition diagnostic](transition_latency.json)
retain trial-level records, source hashes, and capture checks.

| Outcome | Original full | Experimental guard | Reactive |
|---|---:|---:|---:|
| Mean completed-request goodput (Mbps) | 0.952592 | 0.952018 | 0.952738 |
| Mean trial p95 successful-request RTT (ms) | 0.874 | 0.917 | 0.718 |
| Route commits / 5 | 5 | 5 | 5 |
| Application request failures | 0 | 0 | 0 |
| Reverse endpoint packet-instance deficits | 47 | 49 | 73 |
| Repeated payload-sequence instances | 172 | 178 | 176 |
| Sender-side visible TCP RST | 0 | 0 | 0 |

The guard-minus-original paired goodput differences were -0.003192,
+0.002489, -0.000038, -0.002054, and -0.000078 Mbps (mean **-0.000575**).
Guard-minus-reactive differences were -0.004266, +0.001690, +0.001998,
+0.000553, and -0.003575 Mbps (mean **-0.000720**). The generated report's
original-full-minus-reactive mean was -0.000145 Mbps with descriptive paired
bootstrap interval [-0.001988, +0.001697] Mbps. These tiny, mixed differences
on one reused trace slice do not establish an advantage for any policy.

The guard's high-uncertainty escape did **not** activate here: normal full
and guarded runs synchronized at step 0 and committed at step 1 under the
unchanged uncertainty gate. Thus this check exercises non-regression on a
different file, not generalization of the guard's PLC-port recovery behavior.
The executed source snapshot still recorded repeated post-route COMMIT
*decisions* for original full and reactive, though the live runner performed
only one physical route transaction per trial. A subsequent source-only
accounting fix labels those post-route decisions WAIT for all policies while
preserving security FALLBACK. It does not alter these 15 trials or their
measured outcomes. A separate ignored two-trial, six-step smoke check at seed
163 verified one route transaction per policy and only “already routed” WAIT
actions after the transition, with no residual namespaces; it is not added
to the frozen 15-trial comparison.
Mean strict pre/post-transition p95 RTT was 66.594/0.690 ms for original full,
67.929/0.679 ms for guarded, and 2.618/0.691 ms for reactive. The phase
diagnostic excludes in-flight successes and is not an exact outage measure.

## Offline decision and modeled replay

Chronological train/calibration/test counts were 16,494/5,498/5,498. The
training-only 90th-percentile assumed source capacity was 0.056808 Mbps.
For fixed EWMA, independent-opportunity decisions were 5,401 COMMIT and 97
WAIT for original full, 5,399 COMMIT and 99 WAIT for reactive, and 5,498 WAIT
for static. Rolling-mean gave 5,401/97 for full; adaptive residual EWMA gave
5,372/126. All five controller ablations with readiness gates matched full
counts under fixed/rolling EWMA; adaptive EWMA gave 5,372/126 for each.
Prediction-only gave 5,401/97 with fixed/adaptive EWMA and 5,400/98 with
rolling mean. Reactive was 5,399/99 under all three models. Static remained
WAIT throughout. These are repeated *independent opportunity* decisions, not
5,401 physical migrations.

Stateful replay modeled **one** migration for every non-static policy under
all three forecasters. Full and gated ablations used one PREWARM and one SYNC;
reactive and prediction-only used neither. Every policy, including static,
had zero modeled capacity-excess Mbps-seconds. This proxy therefore cannot
demonstrate migration benefit on this file; it uses fixed modeled resources,
capacity and action costs, not measured energy or risk.

Derived CSV SHA-256:
`93737ae78da4ff8e7900ecf56df40ec8254dc62ac8d2692162f81067aec6c86f`.
Sidecar SHA-256:
`b07f45f466cf180e764857ac432968ed384b42711fbadbdfb1b1ec0af109b7f3`.
Offline decision JSON SHA-256:
`b0f8d2b445a548f762b0be2fca0853f2b1e457fe785f9a0c5dfbb4219ef2b904`.
Stateful replay JSON SHA-256:
`55dc1c6aa5d71bf3dfd2ee4f248ec5236fe157e894843eba43122b22fdc74baa`.
The latter two large files are ignored, while the commands and all live
source/record/capture hashes are preserved in the protocol and summaries.

This remains a single WSL2 host with generated TCP echo traffic, not actual
stateful firewall traffic from the PCAP. Zero application failures and no
observed sender RST do not prove zero packet loss or full TCP state fidelity.
Carbon and attack risk are modeled. The original controller's negative
Cyber4OT PLC-port results and the guard's development-only recovery remain
part of the claim ledger; this file does not overturn either.
