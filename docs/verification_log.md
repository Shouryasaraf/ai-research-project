# Verification Log

## 2026-10-06 — Stage 0/1

Environment: Windows host with Codex bundled Python runtime.

- `python -m unittest discover -s tests -v`: 14 tests passed.
- `python -m compileall -q src tests`: passed.
- deterministic smoke decision: `COMMIT` to `node-green`;
- calculated net benefit: `0.76` normalized utility points;
- adaptive threshold: `0.305` normalized utility points;
- invariant violations: none.

This is calculation/state-machine evidence, not a network or migration result.

## 2026-10-06 — Expanded controller-core regression

- Windows bundled Python: the current suite has 36 passing unit tests; bytecode compilation passed.
- Ubuntu WSL2 Python 3.14.4: the same 36-test suite passed.
- Optional Ruff linting was attempted but not run because Ruff is not installed.

The expanded suite covers scaling hysteresis/cooldown, flow affinity, conformal forecasting, carbon units, risk attribution, reference state synchronization, and idempotent fallback. It remains controller-level evidence unless a testbed result is explicitly listed below.

## 2026-10-06 — Stage 2

Environment: Ubuntu under WSL2, kernel `6.18.33.2-microsoft-standard-WSL2`; Linux network namespaces, nftables 1.1.6, conntrack 1.4.9, iperf 3.20.

Observed from `scripts/testbed.sh up`, `test`, then `down`:

- three exact namespaces created with the documented addresses;
- nftables forward chain loaded with default-drop policy;
- two ICMP probes succeeded with 0% packet loss;
- controlled TCP/5201 workload succeeded;
- TCP/8080 connection timed out and the default-deny counter incremented;
- conntrack listed assured TCP/5201 flows;
- firewall counters recorded new allowed traffic, established traffic, and the denied packet;
- cleanup returned `testbed_down=true`.

The same-host iperf run reported approximately 48 Gbit/s. This value is a functional traffic-generation observation only and is excluded from performance claims because namespace-local throughput does not represent a physical or distributed deployment.

Stage 2 verifies a real kernel-enforced packet path. It does not verify warm state transfer, multi-vFW flow pinning, migration, scaling, or publication hypotheses.

## 2026-10-06 — Stage 4 kernel-state feasibility

Observed from a temporary isolated source/target namespace check:

- a live TCP/5201 flow using fixed client port 40000 appeared in the source conntrack table as `ESTABLISHED` and `ASSURED`;
- conntrack-tools created the same original and reply tuple in the separate target namespace;
- the target listed the tuple as `ESTABLISHED`, `ASSURED`, and initially `UNREPLIED`;
- the automatic cleanup removed the target and Stage 2 namespaces.

This verifies kernel conntrack tuple insertion only. It does not verify full TCP sequence/window synchronization, route switching, packet continuity, or warm migration.

## 2026-10-06 — Dual-vFW proxy flow pinning

Observed from the supervised dual-vFW namespace test:

- an established client connection returned `source:before` and remained on the source for `source:after` after the selection changed;
- a new connection opened after the change returned `target:new`;
- source and target nftables counters each recorded a new TCP/9000 flow and established packets;
- the test identified itself as proxy-based flow pinning and explicitly reported transparent SDN steering as unverified;
- supervised cleanup left no Linux network namespaces.
- after controlled target-backend termination, the health check restored the source selection and a new flow returned `source:fallback`;
- the single smoke run observed 101 ms from injected failure to successful fallback response.

This verifies application-proxy affinity across two real vFW paths. It does not verify transparent steering or moving an established connection between vFWs.

The 101 ms fallback observation is one functional smoke measurement, not a benchmark or publication result. Repeated fault-injection trials and confidence intervals are still required.
