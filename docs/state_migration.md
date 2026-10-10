# Stateful Migration Evidence Levels

The project uses explicit evidence levels to avoid treating metadata copying as seamless stateful migration.

## Level 0 — Reference metadata synchronization

`state_sync.py` copies typed established-flow records, calculates canonical SHA-256 digests, and reports missing or mismatched state. This validates controller logic only.

## Level 1 — Kernel conntrack tuple insertion

`scripts/conntrack_sync_smoke.sh` creates a live TCP/5201 flow through the source vFW namespace, confirms that the source tuple is `ESTABLISHED` and `ASSURED`, and inserts the same original/reply tuple into a separate target network namespace. Both namespaces load a firewall table. `scripts/validate_conntrack.py` compares the original and reply tuples, `ESTABLISHED` state, and `ASSURED` flag. It rejects missing or changed supported fields.

```bash
sudo bash scripts/conntrack_sync_smoke.sh
```

The script automatically deletes the exact temporary namespaces and test processes it creates. A pass proves that the host permits reading source kernel conntrack state, creating target kernel state, and matching the supported tuple fields. The imported target entry is still `UNREPLIED`. TCP sequence/window state, packet continuity, and route switching remain unverified.

## Level 2 — Policy and state validation before route commit

The dual-vFW proxy now makes one guarded decision before admitting new target flows: it checks normalized source/target nftables policy and an explicit approved default-deny rule shape, target process health, live source conntrack evidence for the flow that will remain pinned, absence of that flow on the target, and fresh, schema-valid telemetry from both firewall namespaces. The selector changes only if every check passes. Controlled policy mismatch, missing source conntrack state, and stopped target tests keep the source selected. This validates the source-pinned strategy for the proxy topology; no existing flow is transferred to the target.

The new isolated `route_migration_lab.sh` also exercises a *single established TCP connection* across an actual two-sided route change. It inserts the supported source original/reply tuple into the target with `ASSURED,SEEN_REPLY`, attests the exact default-deny nftables policies, rejects a still-`UNREPLIED` target entry, and only then changes routes. In short functional runs the same client socket received `server:before` and `server:after`, and the target firewall's established-accept counter increased. Separate controlled `UNREPLIED` and policy-mismatch faults were rejected before route change while the source connection finished. See `route_migration_lab.md` for topology, commands and limits.

The route lab also passed a controlled reverse-state-refresh rollback: the same socket returned through source after a target-policy fault, with source established-accept traffic observed. This advances Level 2 beyond tuple insertion, but the *full* gate remains open: TCP sequence/window state is not independently compared; bidirectional route changes are sequential, not atomic; packet loss and interruption have not been measured; automatic crash rollback and multi-flow repetition are not established. The successful same-flow route lab is separate from the uncertainty-gated proxy/controller path, so it is not yet a single end-to-end research workflow.

## Level 3 — Flow-pinned warm transition

Proxy-based source pinning and guarded target admission have been smoke-verified, including completion of one delayed source application flow. The route lab separately shows one specific copied-state, same-socket route transition. These two paths have not been integrated into one controller-driven, flow-pinned warm-migration operation. Repeated flow-level statistics, packet capture, full source retirement, and route-level rollback remain pending. The proxy test uses different backend addresses and cannot itself be treated as proof that a copied conntrack entry preserves its flow.

Only after all Level 3 acceptance checks pass may the project describe the result as verified state-consistent warm migration with flow pinning; that gate has not passed yet.

2026-10-10 wire-visible follow-up: the [validated TCP diagnostic](tcp_wire_diagnostic.md) inspected endpoint captures from six synthetic and six historical-rate-derived full/reactive migration trials. None contained a sender-side RST at the two capture points, while repeated payload-sequence instances were visible in every trial. This narrows observed reset behavior but does not compare the kernels' internal TCP sequence/window state or close the Level 3 acceptance gate.
