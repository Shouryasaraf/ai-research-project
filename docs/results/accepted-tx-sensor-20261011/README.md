# Socket-accepted signal diagnostic: no trigger advantage observed

The [sensor protocol](../../accepted_tx_sensor_protocol.md) was committed at
`6a9504c` before the 10 captured static-path trials. The five fixed synthetic
families (`step`, `steady`, `bursts`, `trend`, `flash`) each used seeds 173 and
179, 12 one-second steps and three generated TCP echo flows. All ten trial
records completed with no application errors, no route transactions, valid
paired endpoint captures and no residual namespaces. The [generated summary](summary.json)
retains source/manifest/trial hashes and an independently recomputed accepted
byte count for every one of the 120 [samples](samples.csv).

The planned source shaper was 1 Mbps. A **planned** overload means scheduled
rate >1 Mbps, not measured wire-offered demand. Each observed signal is tested
at the unchanged 0.8-Mbps controller trigger.

| Family | Planned overload / samples | Accepted TP/FN/FP/TN | Goodput TP/FN/FP/TN | Mean absolute planned-minus-accepted / planned-minus-goodput (Mbps) |
|---|---:|---:|---:|---:|
| Step | 18 / 24 | 18/0/0/6 | 18/0/0/6 | 0.348629 / 0.353525 |
| Steady | 0 / 24 | 0/0/0/24 | 0/0/0/24 | 0.002898 / 0.002898 |
| Bursts | 12 / 24 | 12/0/0/12 | 12/0/0/12 | 0.219688 / 0.234421 |
| Trend | 12 / 24 | 12/0/6/6 | 12/0/6/6 | 0.154811 / 0.160682 |
| Flash | 6 / 24 | 6/0/0/18 | 6/0/0/18 | 0.186182 / 0.195878 |
| **All** | **48 / 120** | **48/0/6/66** | **48/0/6/66** | **0.182442 / 0.189481** |

In planned-overload windows, socket-accepted minus completed goodput averaged
+0.013751 Mbps; in other windows, -0.003622 Mbps. The accepted rate is a
modestly closer proxy to this *planned schedule* in aggregate, but it did
**not** identify any additional overload sample at the fixed trigger. The six
shared false positives came from the trend family. The 48 positive windows
were repeated in a small deterministic single-host lab; they are not 48
independent workloads, nor a statistical validation of a detector.

The response-gated generator can reduce new sends while waiting for replies.
Socket acceptance is neither true unconstrained demand nor a wire-rate
measurement. This diagnostic does not calibrate the existing guard's
three-slot rule, and no controller policy or threshold is changed from these
results. Raw records, captures and source snapshots remain Git-ignored under
`artifacts/raw/accepted-tx-sensor-*-20261011-v1`. The full summary and sample
table are tracked to keep negative evidence visible.
