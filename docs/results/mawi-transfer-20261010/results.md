# Second historical MAWI workload: exploratory transfer result

Protocol and timing: [second_mawi_trace_protocol.md](../../second_mawi_trace_protocol.md). These are post-development diagnostics, **not** independent confirmatory experiments. The January 1 capture is a holiday sample from the same MAWI samplepoint-B as the earlier December 2000 capture. It is a different time segment, not a second measurement site or a modern vFW workload.

## Provenance and integrity

The source is the [official 2005-01-01 14:00 JST MAWI capture](https://mawi.wide.ad.jp/mawi/samplepoint-B/2005/200501011400.html), used under the [WIDE research/privacy guidelines](https://mawi.wide.ad.jp/mawi/guideline.txt). The locally downloaded compressed file is 86,166,098 bytes, SHA-256 `894b23c03a8ee9166298bb83ff9bc7076b500704b15d9c54ed8928ad6e849a20`. The existing header-only converter read 3,103,414 packets and 1,562,599,468 original-length bytes, both exactly matching the official summary. It generated 901 one-second Mbps samples, CSV SHA-256 `891910016d63705c1e34c6207de9fc30f67c0b27b11d9e0ece94665a79c58179`. Original capture and derived CSV/sidecar are local and ignored by Git; neither packet contents nor addresses were used.

## Offline forecasting and decisions

The chronological split was 540 training, 180 calibration, 181 held-out seconds. No capacity normalization was asserted for forecasting. All numbers below are from the immutable local `forecast.json` and `decisions.json`; the assumed capacity of 15.38236 Mbps is the training-only 90th percentile, **not** measured vFW capacity.

| Forecaster | MAE (Mbps) | 90% interval coverage | Mean interval width (Mbps) | Full COMMIT / 181 | Reactive COMMIT / 181 |
|---|---:|---:|---:|---:|---:|
| Rolling mean | 0.612957 | 0.900552 | 2.488768 | 181 | 133 |
| Fixed EWMA | 0.548757 | 0.917127 | 2.222188 | 180 | 133 |
| Adaptive EWMA residual (exploratory) | 0.548757 | 0.878453 | 2.187916 | 181 | 133 |

Only one held-out second exceeded the hypothetical capacity. Under the evaluator's *independent ready-target opportunity* rule, the full policy therefore produced 180 (fixed EWMA: 179) COMMIT decisions without same-step exceedance. This is action propensity, **not 180 actual migrations, false-positive operational events, or measured harm**. The evaluator resets target readiness and migration state for every second, so it cannot quantify cumulative migration cost or anti-thrashing behavior.

The reproducible [action-run audit](action_episodes.json) groups adjacent COMMIT recommendations without inventing migration state. For fixed EWMA, the 2005 full policy's 180 COMMIT recommendations form **two contiguous episodes** (longest 117 seconds), while reactive's 133 form 11 episodes. On the 2000 sample, fixed-EWMA full has no COMMIT episode and reactive's 109 recommendations form 25. An episode is still only a run of recommendations: neither 2 nor 11 is an executed migration count or a cost estimate. The audit validates raw test indices and policy/model counts, and records hashes of its two input decision files.

For comparison, the earlier 2000-12-28 samplepoint-B decision record (`mawi-200012281400-decision-exploratory-v4.json`) had 146 held-out seconds; the full policy returned WAIT at all 146 for all three forecasters, while reactive COMMIT occurred in 109. The two samples have different traffic distributions and independently training-derived hypothetical capacities, so the contrast demonstrates **strong scenario sensitivity of this offline decision rule**, not a causal effect of year or a generalization statistic. The earlier adaptive method was already developed on the 2000 trace; the 2005 results cannot be presented as a clean external test of a pre-registered model.

## Captured Linux pilot on scaled trace-derived payloads

The [validated six-trial report](../live-mawi2005-captured-pair-20261010-v1/results.md) covers paired seeds 47, 53 and 59. Each policy completed all three trials, made one route commit per trial and had zero application request failures. Mean goodput was 0.834172 Mbps for the full policy and 0.834740 Mbps for reactive; the paired full-minus-reactive difference was -0.000568 Mbps. In each of the six trials, endpoint matching found zero forward missing packet instances and 15 reverse missing instances; raw capture hashes and the executed-source snapshot passed the batch validator. A [post-hoc response-gap report](../live-mawi2005-captured-pair-gap-20261010-v2/results.md) also brackets each transition with successful responses; the full policy's gaps were 0.560–0.616 seconds and reactive's 0.408–0.515 seconds, **including programmed pacing and synchronization**, not exact outage. This is bounded lab traffic generated from *scaled and capped* trace values, not replay of MAWI packets or full MAWI demand. The three seeds reuse one held-out trace segment; the descriptive interval in the linked report is not inferential evidence of general performance.

Physical carbon, attack likelihood, complete TCP-state equivalence, exact migration outage and independent modern-network replication remain unmeasured. The negative and mixed results preclude a superiority claim over reactive control.

## Reproduction inputs

Local, Git-ignored source paths: `artifacts/raw/mawi-20050101-v1/{200501011400.dump.gz,traffic-1s.csv,traffic-1s.provenance.json,forecast.json,decisions.json}` and `artifacts/raw/live-mawi2005-captured-pair-20261010-v1/`. Tracked generated live metrics are in `../live-mawi2005-captured-pair-20261010-v1/`. Obtain the capture independently under MAWI's terms; do not redistribute the raw capture.
