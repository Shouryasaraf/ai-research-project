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

The separate conntrack smoke test copies and compares a supported kernel tuple. Combining that copied tuple with a real route change for the same end-to-end flow, TCP-level state validation, and safe route rollback remain pending. Thus the full Level 2 migration gate is not complete.

## Level 3 — Flow-pinned warm transition

Proxy-based source pinning and guarded target admission have been smoke-verified, including completion of one delayed source application flow. Repeated flow-level statistics, packet capture, full source retirement, and route-level rollback remain pending. The proxy test uses different backend addresses and cannot be treated as proof that a copied conntrack entry preserves its flow.

Only after all Level 3 acceptance checks pass may the project describe the result as verified state-consistent warm migration with flow pinning; that gate has not passed yet.
