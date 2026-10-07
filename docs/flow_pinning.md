# Dual-vFW Proxy Flow-Pinning Test

The dual-vFW testbed exercises real traffic through two independent nftables firewall namespaces. A Python TCP director chooses the backend/vFW path when a connection is accepted and never changes that backend for the life of the connection.

During the test:

1. the active backend begins as `source`;
2. one client connection sends `before` through the source vFW and stays open;
3. the target is already warm and the control file changes to `target`;
4. a new client connection is directed through the target vFW;
5. the original connection sends `after` and must still report `source`;
6. nftables counters from both vFW namespaces are printed.
7. the target backend is stopped as controlled fault injection;
8. the health check restores the last validated source selection and verifies a new flow;
9. recovery duration is printed in milliseconds.

Run:

```bash
sudo bash scripts/dual_vfw_testbed.sh run
sudo bash scripts/dual_vfw_testbed.sh test-policy-mismatch
```

The supervised `run` command keeps all local services alive in one WSL invocation and always executes cleanup on exit. The separate `up`, `test`, and `down` commands are retained for interactive Linux debugging, but should not be split across independent `wsl.exe` invocations because WSL may terminate background processes when an invocation ends.

This verifies application-proxy flow affinity across two real stateful software-firewall paths. It is not transparent SDN/Open vSwitch steering, not kernel connection-state migration, and not evidence that an existing TCP connection can move from source to target without disruption.

The fallback check verifies restoration for newly opened flows after target failure. It does not verify recovery of an established flow that was already using the failed target.

Before changing new-flow selection to the target, the script calculates normalized SHA-256 digests of the loaded source and target nftables policies, ignoring runtime handles and counters, and checks target-backend liveness. A mismatch or unhealthy target refuses the selection change. This is pre-commit policy/health validation; it is not conntrack-state equivalence.

The controlled mismatch command inserts an extra target-only allow rule, requires pre-commit validation to fail, and confirms that the source remains selected. It does not send traffic to TCP/9999 or outside the isolated namespace topology.
