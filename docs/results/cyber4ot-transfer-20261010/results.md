# Cyber4OT independent-source transfer pilot

The [protocol](../../cyber4ot_transfer_protocol.md) was committed before converting the selected held-out member or running this batch. Dataset: Warsaw University of Technology [Cyber4OT v1.0.0](https://doi.org/10.5281/zenodo.13935639), a **simulated industrial network** captured in 2024, not a production Internet vFW workload. The dataset archive is 67,667,910 bytes, publisher MD5 `55510cbb43d8af72a69dfbcd6940daa5`, local SHA-256 `052565128073afcf2cc92d758be3dc644e842698c6d24ebe758aae3601bce6b6`, and embedded CC BY-NC 4.0. No IPv4-whitelisting or signup form was used. The archive and derived traffic are Git-ignored.

The converter read only packet timestamps and original wire lengths from `traces/Cyber4OT_003.pcapng`: 126,492 packets, 7,981,390 original-length bytes, 906 contiguous one-second bins from 2024-02-08 10:58:56 to 11:14:01 UTC, no internal empty bin. Derived CSV SHA-256 `df77225d7199f3228aadee1741400439b63957e363fb8f85a7e688344f6204a3`; sidecar SHA-256 `1a981bd03ff55612b52b8f14f8510bb1fbdf8754a99bfc51ab140ab31805dbf7`. It did not decode, export, execute, or replay archived packet payloads.

Exactly five predeclared seed pairs (61, 67, 71, 73, 79) completed on one Ubuntu WSL2 host, with no residual lab namespaces. Both policies made one route commit per trial and had zero application request failures. Captured endpoint matching validated every record. The generated [paired table](../live-cyber4ot-captured-pair-20261010-v1/results.md) and [TCP wire table](../tcp-wire-cyber4ot-20261010-v1/results.md) retain all per-trial outcomes.

| Outcome | Full controller | Reactive threshold |
|---|---:|---:|
| Mean completed-request goodput | 0.975867 Mbps | 0.974459 Mbps |
| Mean trial p95 successful-request RTT | 0.521668 ms | 0.508932 ms |
| Request failures across trials | 0 | 0 |
| Route commits across trials | 5 | 5 |
| Reverse missing packet instances across captures | 42 | 61 |
| Sender-side TCP RST across captures | 0 | 0 |

The paired mean full-minus-reactive goodput difference was **+0.001408 Mbps**; its descriptive five-pair bootstrap interval was **[-0.001321, +0.003336] Mbps**, spanning zero. Thus the slight mean edge does **not** establish a prediction advantage. Reverse packet-instance deficits and repeated payload-sequence instances occurred, so application success must not be described as zero-loss migration. The timing brackets include request pacing and are not exact outage estimates.

The result transfers the pipeline to a new publisher and more recent simulated workload, but five runs reuse **one** held-out member; seeds vary order, not network workload. The source was rate-derived and scaled to generated TCP echo traffic, not direct Modbus traffic or attack replay. The same WSL2 host, modeled carbon/risk, warm target and one alternate route remain. This is a protocol-frozen **development transfer pilot**, not an independent-host replication, multi-workload confirmatory experiment, or evidence of reduced emissions/attacks. Preserve the earlier negative MAWI/synthetic comparisons alongside this mixed result.

An allowlisted, local, Git-ignored lab artifact snapshot `research-vfw-lab-artifact-20261010-v5.zip` contains this batch's generated records and endpoint captures alongside the two earlier captured batches, but **not** the external Cyber4OT archive or derived traffic CSV. Its SHA-256 is `4f40a117349cf8d08c001b0c84c22cf58d7b6eb6ac204da92ab86fc55ff906b9`. A fresh same-host extraction without Git passed 137 non-privileged tests and regenerated this batch's live summary and TCP-wire summary byte-identically to the tracked files (SHA-256 `fcc6d81280098033401ce980f561aecff0b02548673c69050d939ede0899815d` and `2f4e932148cb703bd03fbba9fa72cb3799ba0a2aa13e1053f8ca6a191871b460`). This is package QA, not an independent-machine replication.
