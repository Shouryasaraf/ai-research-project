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
sudo bash scripts/dual_vfw_testbed.sh test-state-mismatch
sudo bash scripts/dual_vfw_testbed.sh test-target-unhealthy
sudo bash scripts/dual_vfw_testbed.sh test-unsafe-source-fallback
```

The supervised `run` command keeps all local services alive in one WSL invocation and always executes cleanup on exit. The separate `up`, `test`, and `down` commands are retained for interactive Linux debugging, but should not be split across independent `wsl.exe` invocations because WSL may terminate background processes when an invocation ends.

This verifies application-proxy flow affinity across two real stateful software-firewall paths. It is not transparent SDN/Open vSwitch steering, not kernel connection-state migration, and not evidence that an existing TCP connection can move from source to target without disruption.

The fallback check verifies automatic restoration for the next newly opened flow after target failure. The proxy detects the failed target connect, checks the live source nftables policy against the approved default-deny ruleset, atomically selects the source, and retries that new flow. If the source policy cannot be attested, it fails closed. It does not verify recovery of an established flow that was already using the failed target or proactive detection before a client arrives.

Before changing new-flow selection to the target, `scripts/guarded_selection.py` evaluates normalized source/target nftables policy digests, verifies that each ruleset is the explicitly approved default-deny policy, checks target-backend liveness, the established source conntrack flow that will stay pinned, absence of that tuple on the target, and fresh schema-valid network telemetry from both namespaces. The control file changes to `target` only after these checks pass. This verifies source pinning at commit; it is not transferred conntrack-state equivalence.

The unsafe-source fallback fault removes the source firewall rules after target selection and stops the target backend. The proxy refuses source fallback and the next flow fails closed. This controlled fault does not eliminate time-of-check/time-of-use races.

The controlled mismatch command inserts an extra target-only allow rule, requires pre-commit validation to fail, and confirms that the source remains selected. It does not send traffic to TCP/9999 or outside the isolated namespace topology.

The state mismatch command clears conntrack only in the project-created source firewall namespace, then confirms the selector stays on source. The unhealthy-target command stops only the project-created target backend before the commit attempt and also confirms source selection remains. Each supervised test cleans up its namespaces and processes.
