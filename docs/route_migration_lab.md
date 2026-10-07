# Same-Flow Route Transition Lab

`scripts/route_migration_lab.sh` creates six project-labelled Linux network namespaces: client, ingress router, source vFW, target vFW, egress router, and server. Both vFWs have independent nftables forward chains with default drop; new TCP/9000 is allowed only when the packet is a SYN, and established packets require conntrack state. The source and target paths are distinct. The client and server keep the same IPs and TCP socket throughout the test.

In the supervised `run` scenario, a client sends `before`, keeps that TCP connection open, and waits three seconds. The harness observes an `ESTABLISHED`, `ASSURED` source conntrack tuple; inserts the same original/reply tuple into the target with `ASSURED,SEEN_REPLY`; attests both firewall policies; compares the supported tuple/state fields; requires that the target is not `UNREPLIED`; then replaces the two router routes. The client sends `after` on the **same socket**. A pass requires both server responses and an increase in the target firewall's established-accept counter. It always cleans up its exact namespaces on exit.

```bash
sudo bash scripts/route_migration_lab.sh run
sudo bash scripts/route_migration_lab.sh test-no-seen-reply
sudo bash scripts/route_migration_lab.sh test-policy-mismatch
sudo bash scripts/route_migration_lab.sh test-rollback
```

The optional `test-trace-payload` mode uses the first two held-out rates from an imported traffic CSV to size two bounded application messages (1% of each one-second rate, capped at 65,536 bytes). It sends both messages on **one TCP socket** across the same guarded route transition, validates each echoed payload, records round-trip times, and requires target established-accept packets to increase. It does **not** transmit the MAWI packet capture, preserve packet timing, reproduce the original traffic mix, or test full-rate load. After separately obtaining and converting a permitted trace as described in the README:

```bash
sudo bash scripts/route_migration_lab.sh test-trace-payload artifacts/raw/mawi-200012281400-1s.csv artifacts/raw/mawi-200012281400-1s.provenance.json
```

For an immutable, cleanup-checked three-trial functional batch, run `sudo python3 scripts/live_fault_batch.py --output-directory artifacts/raw/my-trace-route-batch --repeats 3 --scenarios route-trace-payload --trace-csv artifacts/raw/mawi-200012281400-1s.csv --provenance artifacts/raw/mawi-200012281400-1s.provenance.json`. The optional trace scenario is not part of the batch runner's default scenario set because it needs a separately acquired local trace.

The two negative scenarios refuse to change either route and require the source flow to finish: one imports a tuple without `SEEN_REPLY`, producing an `UNREPLIED` target entry; the other inserts an extra target-only allow rule. The latter is controlled policy fault injection inside the isolated testbed, not attack traffic against any external host.

The controlled `test-rollback` scenario uses one client socket for `before`, `after`, and `again`. After `after` traverses the target, the harness reads the target conntrack entry, refreshes the source tuple with `ASSURED,SEEN_REPLY`, verifies supported state fields, and confirms the source still has the approved policy. It then empties the target forward chain, leaving its default-drop policy in force, and restores both routes to source before `again`. A pass requires all three responses and a rise in source established-accept packets. Without the reverse refresh, a developmental run timed out on `again`; that failed run is recorded in `verification_log.md`.

For immutable repeated functional records, use `sudo python3 scripts/live_fault_batch.py --output-directory artifacts/raw/my-route-batch --repeats 3 --scenarios route-run route-no-seen-reply route-policy-mismatch`. The batch runner records each trial's stdout/stderr, exit code, selected observations and namespace-cleanup result; it stops on a failed trial.

Evidence boundary: these are short, single-flow functional tests on one WSL2 host. They show that a copied supported tuple plus reply-state flag can permit a particular TCP connection to continue through a different firewall path and return to the source after a controlled target-policy fault in this topology. The trace-derived variant is only a bounded-payload continuity smoke test. The rollback prepares source state *before* disabling the target policy; it is not recovery from a crashed target host. These tests do **not** establish complete TCP sequence/window equivalence, packet-loss bounds, zero downtime, transparent production steering, arbitrary application-state transfer, simultaneous many-flow behavior, atomic bidirectional route commit, crash-safe rollback, or statistically powered success/recovery rates. The earlier insertion-only test without `SEEN_REPLY` remains Level-1 feasibility evidence and must not be confused with this guarded route transition.
