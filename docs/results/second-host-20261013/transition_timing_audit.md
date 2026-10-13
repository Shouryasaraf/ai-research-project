# Post-hoc second-host transition-timing audit

This audit was performed on 2026-10-13 **after** the captured second-host synthetic outcomes were known. It is a mechanism diagnostic, not a predeclared outcome, randomized mediation analysis, or proof of causality. Input is the same owner-supplied archive and verified `record.json` files described in this directory's `README.md` (archive SHA-256 `01b2134367d27caa87078e248dab4b060c2cb157de1e6fa3ca459931672f4434`). No controller or trial data were changed.

For each of nine seed/family pairs, identify the first `COMMIT` decision step in each record. Both policies recorded one successful physical route commit and a supported three-entry conntrack synchronization at commit in every trial. Full additionally recorded an earlier `SYNC` decision and synchronization, yielding two sync operations per trial versus one for reactive. This is an observed control-path difference, not evidence that either state protocol is correct under all TCP races.

Define a paired one-second sample difference as full minus reactive observed completed goodput at the same numbered step. The **pre** window is steps 0 through the reactive commit step (the decision follows that step's observation); the **lag** window is the following step through the full commit step; **post-both** begins at the next step. These windows use step-index alignment and do not provide a causal decomposition of aggregate trial goodput, because the executions are separate and actual timing varies.

| Family | Seed | Reactive/full commit step | Mean pre difference (Mbps) | Mean lag difference (Mbps) | Mean post-both difference (Mbps) |
|---|---:|---:|---:|---:|---:|
| Step | 191 | 3/5 | -0.000001 | -0.396388 | -0.031490 |
| Step | 193 | 3/5 | -0.000032 | -0.386654 | -0.031081 |
| Step | 197 | 3/4 | +0.000005 | -0.371185 | -0.016815 |
| Bursts | 191 | 3/5 | +0.005766 | -0.408024 | -0.015945 |
| Bursts | 193 | 3/5 | +0.005785 | -0.386721 | -0.017265 |
| Bursts | 197 | 3/4 | +0.000001 | -0.301613 | -0.016799 |
| Flash | 191 | 6/7 | +0.000002 | -0.566895 | -0.065274 |
| Flash | 193 | 6/7 | +0.004051 | -0.589947 | -0.048738 |
| Flash | 197 | 6/7 | -0.000004 | -0.560936 | -0.050218 |

The full policy committed one or two decision slots later in all nine pairs. The largest negative step-aligned differences occurred in the intervening lag window, while smaller negative differences persisted after both routes had committed. Thus delayed target admission is a plausible contributor to the observed lower full-policy goodput, but not an isolated explanation. The full path also performs an extra pre-commit sync (approximately 0.070--0.078 seconds total state-sync duration per trial versus 0.035--0.042 seconds for reactive), and separate processes, pacing and shaped queues can affect the remaining gap. Neither this table nor the original small samples justifies changing the frozen independent-source protocol or asserting a general performance mechanism. A subsequent labeled development ablation could compare identical admission times and state-sync counts while retaining the safety checks.
