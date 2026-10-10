# Verification Log

## 2026-10-10 — Externally sourced carbon forecast replay

- Fetched two public NESO regional API responses (North Scotland region 1, London region 13) for 2025-01-01 UTC under the published CC BY 4.0 terms. Both 49-slot API responses include one interval ending at day start; `neso_carbon` retained exactly 48 consecutive half-hour slots inside the day and recorded publisher/derived hashes in ignored provenance sidecars.
- `carbon_signal_replay` paired full and carbon-unaware placement decisions with the same modeled scenario inputs and changed only the two candidate carbon intensities. Full chose the hypothetical North Scotland node 48/48 times; carbon-unaware chose London 48/48; the prohibited node was never chosen. Both policies recommended COMMIT in all slots. The raw replay SHA-256 is `d7e4e2c6f6edb587b302c7170bbda1feeec725ef691e2f86e02fc805634c04e2`; details and source attribution are in `docs/results/neso-carbon-replay-20261010/results.md`.
- This is sourced **forecast** input plus modeled placement, not online information availability, measured node power, actual emissions, security incidents or physical node deployment. Windows and Linux each passed 128 tests, and `ip netns list` was empty after Linux verification.

## 2026-10-10 — Fresh-extraction artifact check

- Built `artifacts/raw/research-mawi2005-lab-artifact-20261010-v2.zip`: 251 allowlisted files, 2,007,472 compressed bytes, SHA-256 `b1cc1782bb2c7deef8991dd12298b09f7d075c93039e4653a82a999be8d8ff93`. It includes 12 attested generated lab endpoint captures but no external original MAWI capture, derived CSV, or sidecar.
- Extracted it into a new local directory with no Git checkout, passed 124 Windows tests, then regenerated the second-MAWI live summary from the packaged batch. Regenerated and tracked `summary.json` SHA-256 values both equal `e145f9fa03e39c80d076475cc67dfb28f4517aefe502d95ad527056ad869d9f9`. This is same-host artifact QA, not independent-host confirmation.

## 2026-10-10 — Post-hoc transition response-gap analysis

- Added a same-flow success-gap bracket around recorded route-commit transition windows to `live_analysis`; the exact-outage field remains null. A unit test checks the bracket and its explicit pacing caveat.
- Regenerated the two captured three-seed reports in new, exclusive output directories while rechecking raw records, source snapshots, PCAP hashes and endpoint matching. In the second-MAWI batch, full-policy brackets were 0.559720–0.615986 s versus 0.408014–0.515048 s reactive. In the synthetic batch, full-policy brackets were 0.373313–0.385530 s versus 0.418947–0.503368 s reactive. These post-hoc, pacing-inclusive brackets cannot be called exact downtime or a general policy effect.

## 2026-10-10 — Second historical MAWI workload transfer

- Downloaded the research-only 2005-01-01 samplepoint-B capture to ignored local storage; compressed size 86,166,098 bytes, SHA-256 `894b23c03a8ee9166298bb83ff9bc7076b500704b15d9c54ed8928ad6e849a20`. Header-only conversion read 3,103,414 packets and 1,562,599,468 original bytes, matching the official publisher page; derived CSV SHA-256 `891910016d63705c1e34c6207de9fc30f67c0b27b11d9e0ece94665a79c58179`.
- Offline fixed-EWMA forecast on the 181-second held-out segment: MAE 0.548757 Mbps, interval coverage 0.917127, mean width 2.222188 Mbps. All models and decision results, including almost-all-COMMIT full-policy behavior, are in `docs/results/mawi-transfer-20261010/results.md`.
- The `decision_episode_analysis` audit recomputed maximal contiguous COMMIT runs from both immutable offline decision files, checked complete test indices and policy/model counts, and saved hashes in `docs/results/mawi-transfer-20261010/action_episodes.json`. On the second trace, 180 fixed-EWMA full recommendations form two runs, not 180 migrations. No migration execution or cost is inferred from these runs.
- After a written live protocol, six paired, captured trace-derived Linux trials completed. The generated `docs/results/live-mawi2005-captured-pair-20261010-v1/` report passed source-snapshot, raw record, capture-hash and packet-matching checks; `ip netns list` was empty. Full goodput was slightly lower than reactive, and each policy had 15 missing reverse packet instances per trial. This is scaled/capped generated traffic, not direct MAWI packet replay or an independent site.
- A separate allowlisted local archive, `artifacts/raw/research-mawi2005-lab-artifact-20261010.zip`, contains code/docs and the attested generated **lab** captures/records, not the external MAWI capture or derived CSV. It has 241 files, 1,989,630 compressed bytes, SHA-256 `afd5424c7319c008e1ca10b9888fa98cd4b5b1ca6c915972da754108b1b0cb8c`. Redistribution still requires an owner license/terms decision.

## 2026-10-10 — Multi-candidate modeled placement audit

- The regenerated `sensitivity-20261010-placement-v3` grid evaluated 243 paired synthetic opportunities across nine policies (2,187 decisions), with zero hard constraint violations. The generated summary and raw hash are in `docs/results/sensitivity-20261010-placement-v3/`.
- Compared with the full controller, carbon-unaware placement chose a different eligible candidate 81 times; risk-unaware placement differed 27 times. This is candidate preference even when an action is WAIT, not an executed migration count. Carbon intensity and risk scores are scenario inputs, not physical measurements.

## 2026-10-10 — Paired captured migration pilot

- Single-seed captured development pilot (`live-captured-pair-20261010-v1`) completed both policies and is retained separately. After a written three-seed protocol, `live-captured-pair-20261010-v2` completed all six declared policy/seed trials with no residual namespaces.
- Each trial had one route commit, zero request failures, zero capture-kernel drops, and a valid paired endpoint comparison. Every trial had eight missing reverse packet instances; forward matched deficits were zero. These are bounded observed packet-instance deficits, not exact service downtime or a production loss probability.
- Generated analysis verified raw record identities, exact executed-source archive fingerprint, endpoint capture hashes and recomputed packet matching. Full mean goodput was 1.093041 Mbps versus 1.160598 Mbps reactive; the descriptive paired difference was -0.067557 Mbps (three synthetic seeds). This is negative development evidence, not a confirmatory superiority test.
- Windows bundled Python and Ubuntu WSL Python 3.14.4: 121 unit tests passed each. `ip netns list` was empty afterward.

## 2026-10-10 — Endpoint capture method controls

- Two ordinary and two deliberate-drop trials in `packet-validation-20261010-v1` completed with no residual lab namespaces or capture-kernel drops. The generated report verifies all endpoint PCAP hashes, recomputes matching, and checks the exact executed-source archive.
- Ordinary trials: 0/978 missing forward packet instances each. Forced-drop trials: 12/792 and 12/798 missing forward instances. Reverse deficits were zero. All application requests eventually completed, so request failure alone would not reveal the deliberate wire-level loss.
- The experiment validates a narrow capture method, not migration packet loss, exact downtime, or production behavior.
- Windows bundled Python and Ubuntu WSL Python 3.14.4: 120 unit tests passed each. `ip netns list` was empty after the control batch and final Linux suite.

## 2026-10-09 — Predictive proxy lifecycle witness

- `lifecycle-20261009-v1` through `v6`: all completed with no residual lab namespaces. In each run the recorded actions were PREWARM, pinned-state SYNC checkpoint, and guarded COMMIT; active paths were 1→2→1. Runs `v4`–`v6` include verified exact source snapshots; `v1`–`v3` have code fingerprints only.
- Two original TCP flows remained on the source; one new flow reached the target; all drained before scale-in and a final source request succeeded. The generated report validates record fields and retains SHA-256 hashes in `docs/results/lifecycle-20261009-snapshotted/summary.json`.
- Windows bundled Python and Ubuntu WSL Python 3.14.4: 118 unit tests passed each; `ip netns list` was empty after the final Linux run. Demand was modeled from active flow count; source capacity and carbon/risk/resource inputs were modeled. This is a functional witness, not measured forecasting or transparent conntrack transfer.

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

## 2026-10-07 — Combined source-pinned pre-commit gate

- `scripts/guarded_selection.py` now reads normalized nftables policies, target process health, live source/target conntrack entries and live network telemetry before atomically changing the proxy's new-flow selector.
- The passing dual-vFW run reported `allowed=true`, matching policy digests, source-pinned established flow, and a new target flow. The one smoke run observed 495 ms from guarded decision start to completion of the first new target response, 1086 ms until the delayed source application flow completed, and 85 ms for new-flow fallback after target failure. These values include command and scheduling overhead and are not performance conclusions.
- Target-only policy mismatch reported `policy_mismatch`; clearing source conntrack reported `source_flow_not_pinned_or_state_mismatch`; stopping the target before commit reported `target_unhealthy`. All three refused the selector change and retained source.
- The final Python regression passed 56 tests; `compileall` and `git diff --check` passed. Isolated WSL tests left no project namespaces.

The guarded flow remains on the source. This does not demonstrate transferring that TCP flow to the target, transparent routing, complete TCP state equivalence or a publication-grade migration result.

## 2026-10-07 — Synthetic chronological forecasting pipeline

- Added deterministic steady, periodic-burst, trend, flash-crowd and held-out-shift rate generators.
- Added an EWMA split-conformal comparator to the existing rolling-mean split-conformal baseline.
- `python -m unittest discover -s tests -q`: 59 tests passed.
- The `held_out_shift`, seed 7 pilot produced 144 training, 48 calibration and 48 held-out one-minute observations. The rolling-mean model had MAE 4.22 Mbps and 85.4% interval coverage; EWMA had MAE 3.71 Mbps and the same 85.4% coverage. Both are below the nominal 90% coverage in this one synthetic shift trial.

These are generated traffic-rate calculations only. They do not establish general calibration, superiority, or network-level improvement. More seeds, trace families, and real workload provenance remain required.

## 2026-10-07 — Live two-path scaling smoke

The dual-vFW proxy now publishes live active-flow counts and uses the `FlowDirector` least-utilized assignment when both paths are active. A supervised scaling test consumed those counts through `ScalingManager` with two sustained observations, activated the target backend and nftables firewall, admitted a new target flow through the guarded selector, preserved the older source flows, drained all active flows, then deactivated the target firewall and backend. A new flow succeeded on the source after scale-in.

Three consecutive isolated WSL runs reported the same functional state sequence, `1 -> 2 -> 1` active vFW paths, with two source flows before scale-out and concurrent counts of source 2/target 1 after scale-out. Each run cleaned up its namespaces. This verifies the two-path activation/deactivation mechanism under a controlled three-flow fixture. It does not establish performance at larger scale, fairness under broad workload distributions, or production multi-host orchestration.

## 2026-10-07 — Automatic new-flow fallback

The proxy now detects a failed connection to the selected target backend, atomically restores source selection, retries that new flow on the source, and increments a fallback counter in its live metrics. In one isolated dual-vFW run the target process was stopped without the test script changing the selector. The next client received `source:fallback`, the selector became `source`, and the observed interval from failure injection to response was 57 ms. The older source flow had already completed. This does not show recovery of an established target flow, proactive failure detection, or a recovery-time distribution.

## 2026-10-07 — Approved-policy and fail-closed fallback gate

- The guarded selector now requires both firewall rulesets to match the explicitly approved four-rule, default-deny `inet vfw` forward chain, not merely each other. A unit fault with two identical allow-all policies is rejected.
- An isolated dual-vFW run passed target admission under the stronger gate and automatically restored a new flow to source after target-backend failure.
- A separate isolated fault stopped the target backend and removed source nftables rules after target selection. The next new flow failed, and the selector did not move to the unvalidated source (`unsafe_source_fallback_rejected=true`, `new_flow_failed_closed=true`). This is a single functional fault observation, not a recovery benchmark or proof against policy time-of-check/time-of-use races.
- The Python regression passed 63 tests at this checkpoint.

## 2026-10-07 — Paired synthetic decision and forecast pilot

- The synthetic experiment summary now pairs policies by scenario and seed, rejects incomplete/duplicate pairs, and reports full-minus-baseline commit-rate differences. These are controller decision contrasts, not QoS, packet loss, or causal benefit.
- A 50-record synthetic forecast pilot used five fixed workload families and seeds 0–9 (240 one-minute samples per record, chronological splits). The mean held-out coverage in the shifted family was 0.842 for rolling mean and 0.835 for EWMA against nominal 0.9, exposing a calibration limitation under this shift. Other family values and individual run hashes are in ignored local `artifacts/raw/forecast-batch-20261007-pilot/`.
- The complete Python regression passed 65 tests. No external workload data or publication claim is implied.

## 2026-10-07 — Repeated isolated fault-regression batch

`scripts/live_fault_batch.py` ran six declared dual-vFW scenarios twice each under Ubuntu WSL2 root, saving an exclusive-write JSON record with stdout, stderr, exit status, selected observations and post-run namespace leak check for every trial. All 12 functional trials passed, with no `vfwlab` namespaces remaining after any trial. The two observed new-flow fallback intervals in the normal scenario were 76 ms and 64 ms; process launch and scheduling are uncontrolled, so these are not a recovery-time distribution or benchmark. The recorded batch is local and Git-ignored at `artifacts/raw/live-fault-batch-20261007-pilot/`.

The Python suite reached 66 tests. One run briefly failed on a Windows/OneDrive atomic-file-replace permission error, then passed unchanged on immediate rerun; a bounded retry was added to the proxy's atomic metrics/selector file replacement. The bounded retry itself still needs a final regression pass.

Final checkpoint regression: the bounded-retry change passed 66 tests. Exact original-tuple matching was then added to the pre-commit source-flow check, including a nearby-address negative test; 67 tests passed. One further isolated dual-vFW run passed guarded target admission and automatic new-flow fallback. Python compilation, Bash syntax, and `git diff --check` passed before the final tuple-matching edit; the remaining checks must be repeated at checkpoint.

## 2026-10-07 — Offline external-trace import boundary

Added an offline CSV adapter requiring exact SHA-256, source URL/DOI, license text, version, UTC retrieval time, preprocessing, missing-data policy, unit, and fixed sampling interval. It rejects wrong units, non-UTC or irregular timestamps, checksum mismatch, and out-of-range values. The forecast evaluator can now run its chronological train/calibration/test process against an imported traffic trace and preserve its provenance. Tests use only a synthetic fixture; no actual external dataset was downloaded, licensed, or evaluated. The Python suite passed 71 tests.

## 2026-10-07 — Same-connection route-transition development and evidence

An isolated six-namespace route lab was added with separate source/target default-deny nftables paths and unchanged client/server IPs. Early runs importing only `ASSURED` copied the visible original/reply tuple but left the target conntrack entry `UNREPLIED`. The target firewall's default-deny counter rose by five packets, its established-accept counter stayed at zero, and the client's second response timed out. One additional run failed before the state step because the backend had not started listening; an explicit listening-readiness poll was added.

Importing both `ASSURED` and `SEEN_REPLY` removed the `UNREPLIED` marker in this kernel. The route lab then passed a same-socket `server:before` / `server:after` response across sequential ingress/egress route replacement, with six packets counted in the target firewall's established-accept rule. Three further consecutive isolated route runs passed the same checks, and no project namespaces remained. After adding exact approved-policy attestation, one more isolated route run passed. These are five short success observations, not a loss/latency or reliability estimate.

One negative `test-no-seen-reply` run rejected the `UNREPLIED` target state before changing routes and let the source connection finish. One negative `test-policy-mismatch` run observed different policy digests plus `target_policy_not_approved`, rejected route change, and let the source flow finish. The source/target policy attestation has unit tests against an identical broad-accept failure case. The Python suite passed 77 tests after those checks. Complete TCP sequence/window equivalence, packet capture, atomic two-sided route commit, rollback and multi-flow behavior remain unverified.

The recorded follow-up `artifacts/raw/route-batch-20261007-pilot/` ran each route scenario three times. All nine functional trials passed and reported no project namespace leftovers: three same-socket route transitions (each with six target established-accept packets), three `UNREPLIED` pre-commit refusals, and three target-policy-mismatch pre-commit refusals. These records remain local and Git-ignored. Trial counts are insufficient for reliability or downtime inference.

## 2026-10-07 — Controlled reverse-state-refresh rollback

The first rollback development run changed routes back to the source without refreshing its conntrack entry. The client received `server:before` and `server:after` but timed out waiting for `server:again`; the source state had not observed target-path traffic. The harness was changed to read the live target conntrack entry, replace the source entry with an `ASSURED,SEEN_REPLY` tuple, verify supported fields and approved source policy, fault the target forward chain closed, and then restore both routes to source.

The next isolated run returned all three responses on the same TCP socket; source established-accept packets increased from 6 to 12 after rollback. A recorded batch at `artifacts/raw/route-rollback-batch-20261007-pilot/` repeated the controlled scenario three times: 3/3 functional passes and no project namespace leftovers. This is pre-synchronized route rollback after a controlled target-policy fault, **not** automatic detection/recovery of a target host crash. No packet loss, interruption interval, full TCP window equivalence, or multi-flow result has been established.

## 2026-10-07 — MAWI historical traffic forecast pilot

- Official [samplepoint-B 2000-12-28 capture page](https://mawi.nezu.wide.ad.jp/mawi/samplepoint-B/2000/200012281400.html) identifies a 50.62 MB compressed file, 1,998,060 packets, 1,155,330,124 original-length bytes, and an approximately 12-minute capture. The compressed file was downloaded once into ignored `artifacts/raw/`; SHA-256: `429c17006f51009a4a78ec4abf030df803f2dbd85a2ee5ef9c8ed03732a42e55`. The streaming converter independently counted exactly **1,998,060 packets and 1,155,330,124 bytes**, matching the publisher's page. This consistency check does not independently authenticate the capture.
- The converter ignored packet contents and aggregated original-length bytes into 727 one-second UTC Mbps bins from first to last observed packet, with no zero-packet bins. The derived CSV SHA-256 is `4923a96f8ba7e75a823c50b6517e1e987c98c6a2d8eca3ba817892e23cfe850a`; the local CSV, sidecar, raw pcap, and forecast result are Git-ignored. No raw packet data is redistributed.
- A fixed 60/20/20 chronological split yielded 436 train, 145 calibration, and 146 held-out test bins. At a one-second horizon, EWMA conformal had MAE **1.149 Mbps**, RMSE **1.467 Mbps**, interval coverage **0.897**, and mean width **4.834 Mbps**. Rolling-mean conformal had MAE **1.191 Mbps**, RMSE **1.503 Mbps**, coverage **0.897**, and mean width **4.913 Mbps**. The nominal interval coverage was 0.9. These are descriptive metrics from **one historical trace**, not confidence intervals, a vFW controller comparison, or evidence of migration benefit. The models were fixed before inspecting the MAWI test results.
- This trace reflects 2000-era backbone traffic, not present-day vFW traffic. Its 1-second fluctuations and duration differ from the 60-second synthetic workload families, so their raw MAEs or widths must not be treated as a fair cross-dataset ranking. MAWI warns of [capture and timestamp limitations](https://mawi.nezu.wide.ad.jp/mawi/faq.html). No packet-path replay, flow-state/migration outcome, attack-risk label, or carbon value was derived from it.
- `python -m unittest discover -s tests -q` passed **79 tests** after adding the converter tests. The test fixture covers little/big endian, micro/nanosecond pcap, gzip, truncated data, out-of-order timestamps, provenance/CSV round-trip, and immutable outputs. The real-capture conversion and forecast were separate local pilot runs.

## 2026-10-08 — Trace-driven offline controller decision pilot

- Added `vfw_research.trace_decision_eval` to run every policy against the same one-step forecasts and previous observed MAWI traffic values. It derives a hypothetical 14.50664 Mbps source capacity from the training-only 90th percentile and reveals each held-out next value only **after** all policy decisions. Its immutable local output has 146 test opportunities × 9 policies × 2 fixed-radius models = 2,628 decision rows, with source and scenario digests. All carbon, risk, state, readiness, and security inputs are modeled scenario values.
- In the initial fixed-radius run, the full controller returned `PREWARM` in all 146 opportunities for both models because the interval width fraction exceeded the scenario's 0.2 commit gate. This exposed a semantics bug: the modeled target was already warm. After correcting the controller to return `WAIT` for an already-warm target under high uncertainty, the final v4 run returned `WAIT` in all 146 opportunities for both fixed-radius models. The reactive policy returned `COMMIT` 109 times; prediction-only returned `COMMIT` 121 times with rolling mean and 123 with EWMA. There were 15 actual next-sample exceedances of the assumed training-derived capacity. These are offline decision counts, **not executed migrations, avoided overload, SLA measurements, or evidence of superiority**.
- After viewing that pilot, added a causally updated adaptive EWMA residual-window **exploratory** model. The repeated local forecast run measured MAE 1.149 Mbps, interval coverage 0.890 and mean width 5.417 Mbps on the same MAWI test segment. Under the corrected controller, the full policy returned `WAIT` for all 146 opportunities. This model/trace reuse is development exploration, not a confirmatory held-out test. See `trace_driven_decision_pilot.md` for the exact limitations.
- Unit regression passed **82 tests** after the adaptive-model and causal-decision tests. The current dataset was never replayed through the namespace packet path; migration and fallback effects remain to be measured separately.
- A separate local exploratory synthetic batch ran five workload families × ten seeds with the adaptive model. In the held-out-shift family, mean coverage was 0.915 for adaptive EWMA versus 0.835 for fixed EWMA, with mean interval widths 19.526 versus 8.721 Mbps and identical point MAE. This is a wider-interval trade-off, not a validated migration benefit or a confirmatory comparison. The batch is ignored under `artifacts/raw/forecast-batch-20261008-adaptive-exploratory/`.
- One WSL2 isolated `test-trace-payload` route run passed. It took the first two held-out MAWI rates (10.677584 and 11.843648 Mbps), scaled them to bounded payloads of 13,347 and 14,805 bytes, and verified both echoed responses on the same TCP connection across the route switch. Measured per-message round trips were 0.473 and 1.284 ms in this single smoke run; they are **not** migration interruption times or latency-distribution estimates. The target's established-accept counter rose from 0 to 14 packets. Source and target approved-policy digests matched; copied supported conntrack fields passed pre-commit checks. No `vfwlab3` namespaces remained afterward. Full TCP sequence/window equivalence and trace-rate replay remain unverified.
- A follow-up immutable batch at ignored `artifacts/raw/route-trace-payload-batch-20261008-pilot/` ran that bounded two-message route scenario three times. All 3/3 functional trials passed, each record showed the same source CSV checksum and both validated payload replies, and each reported zero leftover project namespaces; an independent post-batch namespace check was empty. Three short smoke trials do not estimate migration reliability, interruption, loss, or performance under a sustained trace-rate workload.
# 2026-10-08: sustained closed-loop live pilots

- Windows standard-library suite: 92 tests passed. Includes baseline causal-input checks, benefit-term ablations, live metric arithmetic, negative comparison retention and batch manifest completeness/code-digest validation.
- `scripts/live_experiment_batch.py --output artifacts/raw/live-paired-20261008-pilot --seeds 7 11 19 --steps 12 --flows 3`: all 27 trial records completed, each with no leftover namespaces. A separate Linux check found no residual lab namespaces or live experiment processes after this batch.
- Same batch runner with `--output artifacts/raw/live-mawi-20261008-pilot --policies full_proposed_controller reactive_threshold static_no_migration cold_migration --trace-csv artifacts/raw/mawi-200012281400-1s.csv --provenance artifacts/raw/mawi-200012281400-1s.provenance.json` and the same seed/step/flow arguments: all 12 records completed and cleaned up. Each repetition uses the same held-out trace segment; seeds randomize policy order, not independent trace samples.
- Generated summaries: `docs/results/live-paired-20261008-pilot/` and `docs/results/live-mawi-20261008-pilot/`. Each summary contains the experiment manifest and hashes of its raw records. The two batches have different code digests because analysis/report validation was added between them; policies within each batch match that batch's digest.
- Synthetic interpretation: full control preserved all tested application requests and exceeded static-source goodput, but reactive control had better goodput and lower successful-request RTT. Cold migration had application failures. MAWI interpretation: full/static/cold made no commits, reactive committed once per repetition; goodput was nearly identical. No superiority claim is supported.
- Environment boundary: one WSL Linux host, namespace/nftables paths, tc shaping, three persistent TCP echo flows, target already warm. Carbon/risk/headroom are modeled; packet loss and exact downtime are unmeasured. No full sequence/window transfer, atomic commit, independent workload replication or production recovery guarantee.
- Raw captures/records remain local and ignored. Small generated result tables are tracked candidates; neither these changes nor the raw artifacts were pushed remotely by the agent.
# 2026-10-08: recovery, sensitivity and broader-workload completion pass

- Windows and Linux unit suites each passed 107 tests. `git diff --check` reported no whitespace errors (Windows line-ending warnings remain informational).
- `restart-containment-20261008-v1` and the shared-actuator rerun `restart-containment-20261008-v2`: six process-interruption probes each passed. Both directions were blocked before guarded source restoration with empty TCP tables. No residual namespaces. These are two versions of development verification, not twelve independent production-recovery trials.
- `journal-live-20261008-v1`: one actual route commit, 674 application requests and no failed requests; topology cleaned. `final-integration-20261008-v1`: the final ownership-aware batch smoke completed after Linux tests. Current live commit checks policy and supported state before each route update and after the pair.
- `sensitivity-20261008-v1`: 243 paired modeled inputs across nine policies, yielding 2,187 decisions and no hard-constraint violations. The audit varies five factors. It is not measured throughput, emissions, attack loss or temporal migration frequency. Risk ablations now retain hard risk limits and normalize the scenario's actual weights.
- `broader-20261008-v1`: eight completed trials, pairing full/reactive control on steady, burst, trend and flash schedules with one seed. All had no failed application requests and no observed output-queue drops. This does not establish zero end-to-end packet loss. Generated summaries are under `docs/results/broader-20261008-v1/`.
- Reactive control had higher goodput on burst, trend and flash schedules. One pair per family has no confidence interval; the negative result is retained. No model was tuned against these outcomes.
- An initial shell-loop launch failed argument parsing before any trial; it was replaced with the argument-safe Python campaign runner. New batch source snapshots support exact code recovery; earlier hashes alone do not.
- Added a manuscript draft, publication claim ledger, restart/sensitivity protocols and local allowlisted artifact packaging with archive/content hash verification. Original packet captures and credentials are excluded by the exporter; no license is selected or public release performed.
# 2026-10-09: resumed active recovery and packet-capture verification

- Preserved every earlier attempt, including the fixed-step fault-timing failure, receiver-only closing-packet capture failure and one pre-traffic filesystem setup failure. No attempt was overwritten.
- `active-recovery-capture-20261009-v3`: all six trials completed, all endpoint comparisons valid, no capture-kernel drops and no residual namespaces. Three controller-exit cases resumed all three original flows without request errors after supported-state reverse synchronization. Three target-state-loss cases disrupted all three flows and retained blocked routes rather than restoring stale state.
- Packet-instance deficits were observed even in recovered runs; successful application recovery is not zero-loss migration. Fault-to-route-restoration timings are supervisor/control-plane intervals, not exact application downtime. See generated `results/recovery-20261009/results.md` for numbers recomputed from events and PCAPs.
- `python -m vfw_research.recovery_report` verified raw PCAP hashes, recomputed matching, and generated an all-attempt report covering five batch versions, including failed and unexecuted trials.
- Windows suite: 115 tests passed after adding capture parsing/validity, recovery acceptance, report integrity and artifact inclusion tests. The artifact exporter includes generated lab captures only with explicit opt-in, matching hashes and the expected synthetic-lab scope; external/original captures remain excluded.
- Remaining boundary: source/target kernels and an independent supervisor stay alive. No full-host crash, complete TCP sequence/window equivalence, or fully unified scaling/balancing/migration lifecycle is claimed.
