# Frozen within-corpus PLC-port extension protocol

Frozen before opening or converting the selected packet members or examining
their rate series. This is a **within-Cyber4OT robustness extension**, not an
independent publisher/site, independent host, production-workload replication,
or confirmatory proof of controller superiority. Prior exploratory work used
normal central-switch member 003. The archive README, read before this freeze,
identifies members 069–071 as normal activity captured at the PLC port, at
approximately 5, 10 and 15 minutes. Their packet contents and rates have not
been inspected for this extension. Archive/license provenance is in
`docs/cyber4ot_transfer_protocol.md`.

## Fixed inputs and execution

1. In numeric order, convert exactly `traces/Cyber4OT_069.pcapng`,
   `traces/Cyber4OT_070.pcapng`, and `traces/Cyber4OT_071.pcapng` with the
   existing strict header-only PCAPNG converter to one-second Mbps CSVs. Record
   ZIP/member/CSV/provenance hashes. If a member fails validation, preserve the
   failure and exclude that member; do not replace it with a more favorable one.
2. Without changing forecasting, gates, placement coefficients or scenario,
   run `trace_decision_eval` and then `sequential_replay` with a two-slot
   cooldown on each converted member. The primary offline comparison is
   full versus reactive on simulated migration count, modeled capacity-excess
   Mbps-seconds, and modeled action-cost utility, for the fixed
   `ewma_conformal` forecaster. Report all three members, including negative
   outcomes, and the two other forecasters as sensitivity information. These
   cost/capacity outputs are mathematical proxies, not packet measurements.
3. If all three members convert and have sufficient data for the chronological
   split, run exactly five paired live seeds `83 89 97 101 103` per member:
   policies `full_proposed_controller` and `reactive_threshold`, 30 steps,
   three generated TCP echo flows, endpoint capture, fresh exclusive output
   directories. This is 30 policy trials. Use the existing train-only rate
   scaling and first 30 held-out seconds; no archived packet payload or attack
   action is replayed. Order is deterministically shuffled by seed. Do not
   stop based on interim outcomes.
4. The live primary descriptive endpoint is paired completed-request goodput
   difference (full minus reactive) per member. Secondary endpoints are
   failed requests, route commits, p95 successful-request RTT, packet-instance
   deficits, sender RST and repeated payload-sequence instances. Report every
   pair, member-level mean and descriptive interval without a superiority
   test. Do not pool trials as independent sites; five seeds reuse one member.

## Validity and failure handling

Each live record must pass source/config/trace hash checks, capture hash and
endpoint matching, zero capture-kernel drops, and no residual owned namespaces.
Preserve infrastructure failures and retry only as a separately versioned
attempt without selecting a substitute member. Keep application failures as
outcomes. If any parser or runner defect requires changing code, document it
before rerun; do not silently change the primary outcome or workload slice.
All runs remain on the same WSL2 host with modeled carbon, risk and target
resources. This protocol does not measure emissions, attack reduction, full
TCP-state equivalence, exact outage or production recovery.
