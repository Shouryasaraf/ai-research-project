# Recovery and packet-observation evidence

exploratory repeated supervised fault probes; not independent confirmatory evidence

## All attempts

| Batch | Recorded | Failed | Not executed | All six completed |
|---|---:|---:|---:|---|
| active-recovery-20261008-v1 | 3 | 1 | 3 | False |
| active-recovery-20261008-v2 | 6 | 0 | 0 | True |
| active-recovery-capture-20261008-v1 | 1 | 1 | 5 | False |
| active-recovery-capture-20261008-v2 | 6 | 1 | 0 | False |
| active-recovery-capture-20261009-v3 | 6 | 0 | 0 | True |

## Trial evidence

Routes-restored time includes supervisor operations, not exact downtime. Packet deficits count missing matched instances at the receiver.

| Batch / trial | Status | Resumed original flows | Disrupted flows | Fault to routes restored (s) | Forward missing/sent | Reverse missing/sent | Capture valid |
|---|---|---:|---:|---:|---|---|---|
| active-recovery-20261008-v1 / r0-controller_exit | completed | 3 | 0 | 0.846577 | unverified | unverified | False |
| active-recovery-20261008-v1 / r0-target_state_loss | completed | n/a | 3 | not restored | unverified | unverified | False |
| active-recovery-20261008-v1 / r1-controller_exit | failed | 3 | 0 | 0.868501 | unverified | unverified | False |
| active-recovery-20261008-v2 / r0-controller_exit | completed | 3 | 0 | 0.665696 | unverified | unverified | False |
| active-recovery-20261008-v2 / r0-target_state_loss | completed | n/a | 3 | not restored | unverified | unverified | False |
| active-recovery-20261008-v2 / r1-controller_exit | completed | 3 | 0 | 0.645640 | unverified | unverified | False |
| active-recovery-20261008-v2 / r1-target_state_loss | completed | n/a | 3 | not restored | unverified | unverified | False |
| active-recovery-20261008-v2 / r2-controller_exit | completed | 3 | 0 | 0.796758 | unverified | unverified | False |
| active-recovery-20261008-v2 / r2-target_state_loss | completed | n/a | 3 | not restored | unverified | unverified | False |
| active-recovery-capture-20261008-v1 / r0-controller_exit | failed | 3 | 0 | 0.761157 | unverified | unverified | False |
| active-recovery-capture-20261008-v2 / r0-controller_exit | completed | 3 | 0 | 0.470985 | 6/1754 | 3/883 | True |
| active-recovery-capture-20261008-v2 / r0-target_state_loss | completed | n/a | 3 | not restored | 21/618 | 3/309 | True |
| active-recovery-capture-20261008-v2 / r1-controller_exit | completed | 3 | 0 | 0.656318 | 7/1746 | 3/880 | True |
| active-recovery-capture-20261008-v2 / r1-target_state_loss | completed | n/a | 3 | not restored | 21/618 | 3/309 | True |
| active-recovery-capture-20261008-v2 / r2-controller_exit | completed | 3 | 0 | 0.476578 | 6/1761 | 3/888 | True |
| active-recovery-capture-20261008-v2 / r2-target_state_loss | failed | n/a | n/a | not restored | unverified | unverified | False |
| active-recovery-capture-20261009-v3 / r0-controller_exit | completed | 3 | 0 | 0.410975 | 6/1749 | 3/882 | True |
| active-recovery-capture-20261009-v3 / r0-target_state_loss | completed | n/a | 3 | not restored | 21/618 | 3/309 | True |
| active-recovery-capture-20261009-v3 / r1-controller_exit | completed | 3 | 0 | 0.398759 | 6/1771 | 1/888 | True |
| active-recovery-capture-20261009-v3 / r1-target_state_loss | completed | n/a | 3 | not restored | 21/618 | 3/309 | True |
| active-recovery-capture-20261009-v3 / r2-controller_exit | completed | 3 | 0 | 0.508779 | 6/1761 | 3/888 | True |
| active-recovery-capture-20261009-v3 / r2-target_state_loss | completed | n/a | 3 | not restored | 21/616 | 3/305 | True |

Target-state-loss containment deliberately sacrifices availability. Surviving target state is required for the tested failback.
No reconnects are used. Capture verification checks raw PCAP hashes and recomputes packet matching.
These probes do not prove full TCP-state equivalence, general host-crash recovery, or exact service downtime.
