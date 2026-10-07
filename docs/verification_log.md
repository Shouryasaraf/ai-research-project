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

## 2026-10-06 — Reproducible synthetic experiment pipeline

Environment: Windows host with Codex bundled CPython 3.12.14.

- `python -m unittest discover -s tests -v`: 41 tests passed.
- `python -m compileall -q src tests`: passed.
- scenario plan validation declared 3 paired seeds, 9 policies and 27 records;
- `pilot-20261006-v1` produced 27 immutable completed records;
- the results pipeline regenerated `summary.json`, `policy_summary.csv`, and `commit_rate.svg` from raw records;
- the static policy waited in all three fixture repetitions; the other eight policies committed in this deliberately simple overload fixture.

This result validates configuration parsing, policy-interface parity, immutable records, evidence separation, aggregation and artifact generation. The decision durations are local controller-function timings. All benefit, carbon and risk values are modeled synthetic inputs. This pilot is not a network benchmark, baseline comparison, hypothesis test or publication result.

WSL environment re-inspection was attempted during this run but the execution sandbox returned `E_ACCESSDENIED`; no new privileged networking claim was added.

## 2026-10-06 — Repeated dual-vFW privileged regression

Environment: Ubuntu WSL2 kernel `6.18.33.2-microsoft-standard-WSL2`, Python 3.14.4, nftables 1.1.6, conntrack-tools 1.4.9 and iproute2 6.19.0. Docker, Open vSwitch and Mininet were not present.

Three consecutive isolated `dual_vfw_testbed.sh run` executions each verified:

- an established proxy connection returned `source:before` then `source:after` after target selection;
- a new connection returned `target:new`;
- source and target nftables paths each counted a permitted new TCP/9000 flow and established traffic;
- injected target-backend termination restored a new connection as `source:fallback`;
- cleanup removed every project-created namespace and PID file.

Observed fallback intervals were 57 ms, 115 ms and 57 ms (three smoke observations; median 57 ms, range 57–115 ms). These are not a benchmark or confidence interval. Transparent SDN steering and recovery of an established target flow remain unverified.

`conntrack_sync_smoke.sh` also passed again: the source entry was `ESTABLISHED` and `ASSURED`, and the inserted target tuple was `ESTABLISHED`, `ASSURED` and `UNREPLIED`. This remains tuple-insertion feasibility evidence, not complete TCP state transfer or seamless continuity.

After adding normalized policy and target-health validation, one further dual-vFW run produced matching source/target policy digest `a2bc7eb74005a34e381a52058d74e222315deb694bbfdfedfc32ce717e79f26b`, passed the health gate, preserved the source flow, admitted the new target flow, and restored new-flow fallback after 129 ms. A controlled target-only TCP/9999 allow rule then produced a different digest, caused pre-commit validation to fail, retained the source selection, and cleaned up all namespaces. This verifies policy-mismatch rejection in the proxy-based testbed; it still does not verify conntrack-state equivalence or transparent route migration.

The subsequent timing-instrumented smoke run observed 79 ms from the selection change to completion of the first new target response and 1001 ms from the selection change until the deliberately delayed source application flow completed. New-flow fallback after the injected target failure was 115 ms in that run. These are single-run functional observations affected by process startup/scheduling and the intentional client delay; they are not latency, downtime or migration-performance conclusions.

## 2026-10-06 — Telemetry freshness and final checkpoint regression

- a typed telemetry snapshot now validates units, ranges, counters, provenance and monotonic freshness;
- stale telemetry prevents `COMMIT` for every migrating policy and produces an explicit `telemetry_stale` violation;
- `python -m unittest discover -s tests -v`: 45 tests passed using a workspace-local temporary directory because the execution sandbox denied writes to its Windows temp mapping;
- `python -m compileall -q src tests`: passed;
- `bash -n` passed for all three privileged testbed scripts;
- `git diff --check`: passed.

This validates controller-side freshness enforcement. Live telemetry collection from the namespace testbed remains pending.

## 2026-10-06 — Kernel tuple comparison and live network telemetry

- `python -m unittest discover -s tests -q`: 49 tests passed (workspace-local temporary root).
- `scripts/conntrack_sync_smoke.sh`: source and target original/reply tuples, `ESTABLISHED` state, and `ASSURED` flag matched on the supported fields. The target remained `UNREPLIED`; TCP sequence/window and flow continuity were explicitly reported unverified.
- `scripts/dual_vfw_testbed.sh run`: both firewall namespaces emitted UTC/monotonic timestamps, interface RX/TX bytes, packets, drops and errors, conntrack entry count, and firewall-table presence. Each had one conntrack entry during the observed flow. Source pinning and new target admission passed; observed admission, source application drain and new-flow fallback were 197 ms, 1087 ms and 182 ms in this one smoke run.
- `scripts/dual_vfw_testbed.sh test-policy-mismatch`: the target-only policy change was rejected and source selection retained.

These remain isolated functional checks. The copied conntrack flow and the dual-vFW proxy flow are different topologies. There is no verified single operation that copies state, validates it, commits a route, and preserves that same TCP flow.

The live network telemetry JSON now has a matching controller-side `NetworkTelemetrySnapshot` parser that checks schema version, provenance, firewall-table presence, non-negative interface counters and monotonic freshness. `python -m unittest discover -s tests -q` passed 51 tests after this addition; `compileall` passed for source, tests and scripts. Feeding these snapshots into migration decisions and immutable run records remains pending.
