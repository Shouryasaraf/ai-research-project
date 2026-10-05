# Stateful Migration Evidence Levels

The project uses explicit evidence levels to avoid treating metadata copying as seamless stateful migration.

## Level 0 — Reference metadata synchronization

`state_sync.py` copies typed established-flow records, calculates canonical SHA-256 digests, and reports missing or mismatched state. This validates controller logic only.

## Level 1 — Kernel conntrack tuple insertion

`scripts/conntrack_sync_smoke.sh` creates a live TCP/5201 flow through the source vFW namespace, confirms that the source tuple is `ESTABLISHED` and `ASSURED`, and inserts the same original/reply tuple into a separate target network namespace.

```bash
sudo bash scripts/conntrack_sync_smoke.sh
```

The script automatically deletes the exact temporary namespaces and test processes it creates. A pass proves that the host permits reading source kernel conntrack state and creating target kernel state. It does not prove that TCP sequence/window state is complete, that the target has seen reply traffic, that route switching preserves the connection, or that no packets are lost.

## Level 2 — Policy and state validation before route commit

Pending: create a parallel target vFW path, load identical nftables policy, transfer supported kernel state, compare normalized state, and refuse route commit on mismatch.

## Level 3 — Flow-pinned warm transition

Pending: preserve existing flows on the source during drain while new flows use the validated target; measure completion, resets, loss, downtime, synchronization overhead, and rollback.

Only Level 3 may be described as verified state-consistent warm migration with flow pinning.

