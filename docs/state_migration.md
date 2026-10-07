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

Partially implemented across two isolated tests: the dual-vFW path compares normalized nftables policy and target health before changing new-flow selection, while the separate conntrack smoke test copies and compares a supported kernel tuple. The two checks are not yet combined into one atomic pre-commit gate for the same traffic flow. State mismatch fault injection, TCP-level validation, and safe route commit remain pending.

## Level 3 — Flow-pinned warm transition

Proxy-based source pinning and target admission have been smoke-verified, including completion of one delayed source application flow. Repeated flow-level statistics, packet capture, full source retirement, and route-level rollback remain pending. The proxy test uses different backend addresses and cannot be treated as proof that a copied conntrack entry preserves its flow.

Only Level 3 may be described as verified state-consistent warm migration with flow pinning.
