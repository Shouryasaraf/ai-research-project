# Independent-publisher Zero-SWARM transfer pilot

The [protocol](../../zeroswarm_transfer_protocol.md) and checksum-checked
converter were committed at `a8ac918` before downloading the selected file.
The source is the Centre for Research and Technology Hellas
[*Modbus Normal and Malicious Network Traffic*](https://doi.org/10.5281/zenodo.15082260)
record (CC BY 4.0). Only the preselected 18,119,840-byte
`ZeroSWARM Normal data_v2b.pcap` was downloaded. Its publisher MD5
`9f8235fcdbfcacb32e7a70db14fc6c74` matched; local SHA-256 was
`7ccdb3216007134eecaabf622eb2f2d6c09a06f2e4bbaec8b477a9906d52a7df`.
The strict parser counted 195,362 packets and 14,994,024 original-length
bytes over 1,996 one-second bins with no internal empty bin. It exported
rates, not original packet payloads or addresses.

Exactly five frozen seed pairs (107, 109, 113, 127, 131) completed on the
same isolated WSL2 host. The generated [live table](live/results.md) and
[TCP-wire table](tcp/results.md) contain all ten trials and validation hashes.

| Outcome | Full controller | Reactive threshold |
|---|---:|---:|
| Mean completed-request goodput | 0.922939 Mbps | 0.918691 Mbps |
| Mean trial p95 successful-request RTT | 0.597349 ms | 0.557152 ms |
| Application request failures | 0 | 0 |
| Route commits | 5 | 5 |
| Reverse missing packet instances in endpoint captures | 57 | 75 |
| Sender-side visible TCP RST | 0 | 0 |
| Repeated payload-sequence instances | 104 | 77 |

The paired mean full-minus-reactive goodput difference was **+0.004248 Mbps**;
the descriptive five-pair bootstrap interval was **[+0.001518, +0.006295]
Mbps**. This is a positive result on one independent publisher's preselected
normal trace, not a general superiority result: seeds vary execution order
but reuse the same held-out 30-second workload slice, and the absolute
difference is small. The member-003 Cyber4OT pilot was also slightly positive
with a descriptive interval crossing zero, whereas all three preselected
Cyber4OT PLC-port members were negative with no full-controller commits. Those
opposing results must be shown together. The unchanged controller has a clear
failure mode when fixed conformal interval width exceeds its 0.20 gate.

The fixed-EWMA offline stateful replay on this source modeled one migration
each for full and reactive, with one PREWARM and one SYNC for full. Both had
zero modeled capacity-excess demand after migration; static had 0.000528
Mbps-seconds. This is a proxy, not measured goodput or migration cost.

All captured trials passed source/config hash checks, endpoint matching and
zero capture-kernel drops, and no lab namespaces remained. Endpoint packet
deficits and repeated payload sequences occurred despite zero application
failures and no visible sender RST; zero loss and complete TCP state are not
established. Traffic was generated TCP echo traffic scaled from a Modbus-PCAP
rate series, not direct Modbus replay. Carbon, attack risk and node resources
remain modeled; emissions and attack reduction were not measured. This is
independent **publisher/workload** evidence, not an independent host, and
does not make the paper publication-ready.

Derived CSV SHA-256:
`e41cc1f40f150e6c91f79f3a07fa29c29231371488ef2a91d3d704037118852b`.
Provenance sidecar SHA-256:
`d737ea5475ab73e109c6ffbffd0970ebb1e8327aabdc24939f0b8fe6b03ae4c9`.
Offline replay SHA-256:
`f044398486702ce31fc4ca1369098a7bb76d631abedecf7b905304bb157c069e`.
Raw PCAP, derived rate CSV, live captures and full replay JSON remain
Git-ignored; tracked summaries include manifest and trial-record hashes.
