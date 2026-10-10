# Transition-bracketing response-gap diagnostic

The sustained traffic runner records each successful request's monotonic completion time and each route-commit transition's monotonic start and finish in the same host clock domain. For each flow spanning a committed transition, the analyzer finds the last successful completion before transition start and the first after transition finish, then subtracts the timestamps. It reports the largest such same-flow gap in a trial. Missing or malformed transition windows produce `null`, never zero.

This is a **response-free bracket**, not exact migration downtime. It includes the programmed 50 ms request pacing, possible socket/queue delay, controller work, state synchronization, and the route change. If the service was unavailable for any shorter interval inside the bracket, the metric does not isolate that interval. Zero request failures do not imply zero packet deficits or zero downtime. The separate paired endpoint captures and application-failure counts must be reported alongside it.

The diagnostic was added after the synthetic and second-MAWI captured batches were already collected. The regenerated summaries validate the exact archived source and raw PCAP hashes but are **post-hoc analyses of development trials**, not a predeclared primary endpoint. They leave `migration_interruption_seconds` and `packet_loss_fraction` as `null`.

Reports: [synthetic three-seed batch](results/live-captured-pair-gap-20261010-v3/results.md) and [second-MAWI rate-derived batch](results/live-mawi2005-captured-pair-gap-20261010-v2/results.md). These use different workload shapes; neither six-trial result ranks the policies generally.
