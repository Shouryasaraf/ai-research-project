# Current Limitations and Evidence Status

## Verified in the current stage

- Deterministic calculations and state transitions can be exercised without external dependencies.
- Hard placement constraints are evaluated before weighted ranking.
- Security invariant failures block commit in the core controller.
- Decision records contain reasons and calculation components.
- A WSL2 namespace topology enforces an nftables default-deny packet path and exposes rule/conntrack evidence.
- Scaling decisions require hysteresis, sustained evidence, health, bounds, and cooldown.
- New flows choose a healthy least-utilized vFW; established pins are retained unless explicit recovery is required.
- A rolling-mean split-conformal forecasting baseline preserves chronological splits and reports accuracy separately from interval calibration.
- Carbon estimates preserve explicit units and provenance; node-risk scores expose every weighted contribution.
- The reference state adapter validates flow-record digests but remains emulated metadata.
- Live source conntrack discovery and target tuple insertion are smoke-verified. An isolated route lab has also shown short same-socket continuity after copying `ASSURED,SEEN_REPLY` state and separately shown controlled rollback after reverse-state refresh; full TCP sequence/window equivalence and broader reliability remain unverified.
- The fallback core restores a prior configuration object; one isolated route lab has shown controlled path rollback, but automatic target-host-crash recovery and a recovery-time distribution remain unverified.
- Dual-vFW smoke testing verifies proxy flow affinity and new-flow fallback to the source path. Transparent SDN steering and recovery of established flows on a failed target remain unverified.

## Not yet verified

- Docker/container launch and cleanup.
- Mininet/Containernet or Open vSwitch topology.
- transparent flow pinning, migration downtime, packet loss, or general state continuity beyond the short isolated same-socket observations.
- representative multi-trace forecasting and trace-derived live migration decisions; one historical MAWI forecast and **offline independent-decision** pilot has been run, but no trace-derived traffic was replayed through the firewall path.
- real-world carbon or attack-risk data ingestion.
- baseline/ablation experiments or statistical conclusions.

The Windows execution surface reports no `python` or `docker` on its normal PATH. Ubuntu WSL2 is available, and its Python plus installed Linux networking tools support the namespace testbed. Docker, Mininet, and Open vSwitch remain absent. These constraints must not be misrepresented as properties of another testbed.
