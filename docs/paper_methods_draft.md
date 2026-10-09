# Methods and limitations draft

## Research question

Does explicitly gating warm migration on predictive uncertainty improve the trade-off between migration overhead, service continuity and workload accommodation relative to simpler policies? This question remains open; controller complexity alone is not evidence of benefit.

## Prototype

The implementation separates typed controller decisions from an isolated Linux network-namespace actuator. Six namespaces represent client, ingress, source firewall, target firewall, egress and server. nftables enforces a default-deny path. Source and target egress capacity are shaped with tc. Persistent TCP echo sockets expose application-visible failures; connections are not silently reopened after migration.

The live controller consumes completed-interval goodput and forecasts the next interval using EWMA conformal intervals. Policy attestation precedes state copying and route commit. The supported state adapter copies original/reply tuples and selected established-connection status fields. Two route updates steer the traffic through the target. The target starts warm, so these experiments do not measure instance startup or exercise the separate dynamic-scaling path.

## Comparison design

The preregistered development pilot uses paired synthetic schedules and shuffled policy order across nine variants. A separate historical trace-derived pilot compares full, reactive, static and cold policies. All observations remain exploratory. Imported traffic rates determine generated payload demand; original capture packets, payloads and attack labels are not replayed. Repeated runs of one historical segment measure execution variation, not workload diversity.

The cold baseline deliberately omits conntrack import. Carbon/risk ablations remove modeled benefit credits and corresponding placement weights, but hard safety constraints stay active. A single candidate cannot establish placement-quality improvement. Static control remains on the lower-capacity source, so migration comparisons include access to extra capacity rather than an equal-resource optimization claim.

## Outcomes and reproducibility

Generated tables report completed-payload goodput, request failure fraction, successful-request RTT and paired goodput differences. The analysis verifies planned trial coverage and matching source fingerprints, retains failed outcomes and lists hashes of the raw records. Source data, environment versions, decisions and transition events are retained locally. Published summaries alone are insufficient to reproduce raw-event analysis; a reviewer needs the corresponding non-sensitive trial records.

## Threats to validity

Capacity limits censor observed demand. Synchronous echo traffic is unlike arbitrary production workloads. Successful-request latency excludes timeouts and must be interpreted with flow failures. Small samples and short runs do not support inferential superiority. Namespace isolation on one WSL host does not reproduce multi-host timing or failure domains. Sequential route updates are non-atomic; copying coarse conntrack fields does not prove state equivalence under racing packets. Power, emissions and attack risk are modeled rather than physically measured. The current live runner does not establish general crash recovery.

## Results entry points

Use the generated `results/*/results.md` and accompanying machine-readable summaries; do not manually replace values. The synthetic comparison supports a limited continuity demonstration and preserves a negative result against reactive control. Neither novelty nor publication readiness is established by these experiments. See `novelty_positioning.md` and `references.bib` for the current literature boundary.
