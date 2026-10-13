# Post-hoc PDMFC guard/reactive timing audit

This analysis was made **after** the 15-trial PDMFC WSL outcome was seen. It is a descriptive, step-index-aligned diagnostic, not the frozen primary endpoint or a causal decomposition. The same five seeds reuse one 30-second rate slice and the policies run as separate processes. Original full never committed and is excluded from this particular timing contrast.

Reactive committed after observation at decision step 0 in every seed; the experimental guard synchronized and committed at steps 2 and 3. For each step, subtract the reactive observed completed-goodput sample from the guarded sample. The lag window is samples 1--3, after reactive's commit decision and through guard's commit decision; post-both is samples 4--29. These are completion-rate differences in Mbps, not exact lost bytes or measured downtime.

| Seed | Guard − reactive mean rate, lag samples (Mbps) | Guard − reactive mean rate, post-both samples (Mbps) |
|---:|---:|---:|
| 211 | -0.562100 | -0.001464 |
| 223 | -0.595275 | -0.004875 |
| 227 | -0.604049 | -0.003180 |
| 229 | -0.595082 | -0.005395 |
| 233 | -0.612348 | -0.003851 |

The largest rate gaps fall in the three-slot delay between the two commits; once both routes are active, the step-aligned gap is small but still negative. This makes the guard's deliberately delayed admission a plausible contributor to its lower trial-wide goodput and high p95 RTT relative to reactive. It does not isolate the effect of forecast logic from source-link congestion, synchronization overhead, process scheduling or pacing. A future matched-timing ablation would be a new exploratory experiment, not a reinterpretation of this frozen batch.
