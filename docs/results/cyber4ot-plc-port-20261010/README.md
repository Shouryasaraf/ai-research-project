# Cyber4OT PLC-port within-corpus extension

The [protocol](../../cyber4ot_plc_port_extension_protocol.md) and replay code
were committed at `4dda994` **before** opening or converting members 069–071.
These are the three normal PLC-port members preselected from the archive README.
All converted successfully, and all 30 declared captured live trials completed
on the same WSL2 host. Each member has its own [live](live-069/results.md) and
[TCP-wire](tcp-069/results.md) results; corresponding files for 070 and 071 are
in the sibling directories. The source is 2024-published simulated OT traffic,
not production Internet traffic. Only timestamp/length rates from the source
PCAPNGs informed generated TCP echo load; source packets were not replayed.

| PLC-port member | Full mean goodput (Mbps) | Reactive mean goodput (Mbps) | Paired full-minus-reactive mean (Mbps) | Descriptive 95% pair bootstrap interval (Mbps) | Full/reactive route commits |
|---|---:|---:|---:|---:|---:|
| 069 | 0.885515 | 0.890776 | -0.005261 | [-0.005565, -0.004919] | 0/5 |
| 070 | 0.907403 | 0.952542 | -0.045139 | [-0.047110, -0.043168] | 0/5 |
| 071 | 0.906875 | 0.946482 | -0.039607 | [-0.041601, -0.037464] | 0/5 |

All 30 trials had zero application request failures and passed endpoint capture
matching with zero capture-kernel drops. Full-policy mean trial p95 RTT was
51.612, 57.923 and 54.971 ms for 069–071, versus reactive 0.401, 0.407 and
0.419 ms. Every one of the 435 full-controller decision records (29 decisions
per trial) was `WAIT` with reason “target is warm; wait for lower uncertainty
before commit.” Its normalized interval widths were constant within each
member: 0.222692, 0.241013 and 0.229504, all above the frozen 0.20 commit
gate. The fixed split-conformal radius therefore produced an absorbing wait
condition on these three workloads. This is an observed failure mode of the
unchanged controller, not a parser or trial failure. Reactive committed once
per trial. No threshold was tuned after seeing these held-out outcomes.

The fixed `ewma_conformal` **offline modeled replay** agrees directionally:
for each of 069–071, full prewarms once but makes zero simulated migrations,
while reactive makes one. Modeled capacity-excess demand (Mbps-seconds) was
0.002440, 0.008736 and 0.013760 under full, versus zero under reactive.
These tiny mathematical amounts are **not** measured packet loss, actual
goodput or emissions. The replay's modeled action-cost utility is 0.05 for
full and 0.20 for reactive on each member, but comparing those unitless terms
to measured goodput is not a calibrated cost-benefit analysis.

All sender-side endpoint captures had zero visible TCP RST. Repeated payload
sequence instances did occur (full 334/281/268 versus reactive 75/144/161
across the three members). RST absence and application success do not prove
zero loss or full TCP-state equivalence. The five seeds per member reuse the
same 30-second held-out slice; the bootstrap intervals are descriptive and
cannot be treated as 15 independent network workloads. These three members
share one publisher and testbed, so this is **within-corpus replication**, not
independent-source or independent-host confirmation. It strengthens the case
that the fixed uncertainty gate can hurt this setting; it does not establish
universal reactive superiority.

## Source and output provenance

The 67,667,910-byte Cyber4OT archive SHA-256 is
`052565128073afcf2cc92d758be3dc644e842698c6d24ebe758aae3601bce6b6`;
the [source record](https://doi.org/10.5281/zenodo.13935639) and embedded
license are CC BY-NC 4.0. Members 069, 070 and 071 contained 4,081, 8,116 and
12,147 packets respectively, with 303, 603 and 903 one-second bins. The
derived CSV / provenance / offline replay SHA-256 values are:

| Member | Rate CSV | Provenance sidecar | Stateful replay |
|---|---|---|---|
| 069 | `dfc1f90c4bf47821c5b372f13c84b1a8050bdd8de9bf3fa6cce7df6e68f44dbf` | `a696d0b6393874fbfeb7b50bce91789cb1f441ba96ada870545e3b0918bfafdc` | `eaf2e963f267a3f36061222568afd71aa8f085b1c1c84775c97e8ba6fb359863` |
| 070 | `454d11691070f6c8df798ad47c876f6873275b374123710fba4f4498c9a7ed58` | `5b14e5ab4885fecd8e945311a174d5ff77d0332c3389b98c4cd52d109e49b357` | `b671a404b05640fe9f8ea1a577916f21843ff5f30cbdd7f3acad8892f3843bca` |
| 071 | `ee537e63d39b6fa3bfb9e8731b3152142c1f3c76790bb32391ad91b45ab4e157` | `fe389661bb5c6a0e487bd5ff79bd2d0272943598accf038779a797ff74f8ad1e` | `e0e40733af9b9d4fe5350093ff84290a17bbe8ebbcb209d943e89f80c866a5c1` |

Raw batch directories and large replay JSONs remain Git-ignored under
`artifacts/raw` and `artifacts/processed`. Tracked live/TCP summaries include
manifest and per-record hashes. The result does not close the independent
modern-workload, measured carbon/risk, multi-host or novelty-review gates.
