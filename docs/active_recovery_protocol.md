# Active-flow recovery development probe

Defined before execution. Three repetitions of each of two faults, three persistent TCP echo flows and nine one-second intervals at 0.3 Mbps. The client never reconnects a failed socket. At the second completed interval, supported state is copied and routes commit to the target. At the fourth interval the supervisor injects a fault and contains both directions.

**Version 2 amendment, before rerun:** the first batch's second controller-exit repetition failed its target-traffic acceptance check because a slow commit consumed the fixed pre-fault interval; buffered step-3 telemetry triggered the fault immediately after commit. Its record remains in `active-recovery-20261008-v1`. Version 2 uses fifteen intervals and injects only after a sample timestamp is at least two seconds later than actual commit completion. This corrects experiment timing, not controller performance. All other acceptance rules remain unchanged.

1. Controller exit: the child process that committed the routes exits without cleanup. The independent supervisor blocks both routes, reads surviving target state, synchronizes supported fields back to the source and restores only after policy/state checks. Acceptance requires all original flows to have carried target traffic before the fault and to resume after restoration without request errors.
2. Target state loss: delete only the lab's target TCP entries. The supervisor must retain blocked routes rather than trust old source state. Acceptance requires all three connections to be disrupted and no successful request started after completed containment. This is a safety success and an availability failure, not seamless recovery.

Stopping rule: stop on any failed acceptance check or infrastructure exception and retain its record. Fault-to-containment and fault-to-route-restoration are supervisor timings, not exact service downtime. Packet loss remains unmeasured. In-flight replies from requests started before blocking may still arrive.

These are controlled migration-process interruption and targeted state-deletion probes, not full host crashes or loss of the entire target namespace. The source/target kernels and external supervisor remain alive. Supported conntrack-field equality does not establish TCP sequence/window equivalence. No production crash-recovery claim is authorized by this experiment.
