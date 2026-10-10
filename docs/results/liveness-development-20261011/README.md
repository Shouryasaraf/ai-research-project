# Liveness-guarded controller: development-only result

The [development protocol](../../liveness_guard_development_protocol.md) was
committed at `768fd7f` before this 15-trial three-policy batch. The guard was
designed **after** observing the original controller's failure on Cyber4OT
PLC-port member 070; this source is not held out for the guard. All five seeds
(83, 89, 97, 101, 103) completed for original full, experimental guard, and
reactive. The [live table](live/results.md), [TCP-wire table](tcp/results.md),
and [validated transition-latency diagnostic](transition_latency.json) retain
trial-level records and hashes.

| Policy | Route commits / 5 | Mean goodput (Mbps) | Mean trial p95 successful-request RTT (ms) | Mean pre/post-transition p95 RTT (ms) |
|---|---:|---:|---:|---:|
| Original full | 0 | 0.907485 | 57.911 | no transition |
| Liveness-guarded experimental | 5 | 0.946494 | 51.629 | 54.974 / 0.668 |
| Reactive | 5 | 0.950008 | 0.743 | 4.434 / 0.708 |

The guard issued a supported-state SYNC after three consecutive observed
overload samples and three baseline uncertainty WAITs, then committed on the
next decision. It made one actual route commit per trial; the old full policy
made none. No guard decision had an invariant violation, and all five capture
and route records passed validation. The guard's paired mean goodput change
versus original full was +0.039009 Mbps; versus reactive it was **-0.003514
Mbps** (individual differences: -0.003370, -0.001412, +0.001822, -0.009714,
-0.004894 Mbps). Thus the guard recovered most of the original throughput gap
on this *development* workload but did not surpass reactive on average.

The trial-wide p95 RTT remained high because the delayed commit left roughly
228–229 completed requests per trial in the congested pre-transition phase.
Post-transition p95 RTT was below 0.8 ms in every guarded trial, but that does
not erase the early user-visible latency. The transition diagnostic excludes
requests in flight across the transition and is not an estimate of exact
downtime or causal effect. Completed goodput is an imperfect overload signal;
it can understate offered traffic when congestion prevents completion.

All 15 trials had zero application request failures and zero visible sender
RST. Reverse endpoint packet-instance deficits totaled 44 for the guard, zero
for original full (which never migrated), and 73 for reactive. Repeated
payload-sequence instances were 163, 278 and 160, respectively. These are
finite capture observations, not a packet-loss probability or proof of full
TCP state equivalence. This remains one WSL2 host, one alternate target,
modeled carbon/risk/resources, and a previously inspected workload.

The source-snapshot records in this batch retain the original post-route WAIT
reason text on some guarded steps. A later source-only reporting fix labels
those steps “already routed through the selected target”; it does not change
the 15 executed trials or their outcomes. The experimental three-slot guard
has **not** been calibrated or validated on an unseen workload. Do not merge
this development result with independent-publisher results as confirmation.
