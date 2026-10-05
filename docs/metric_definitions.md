# Metric Definitions

All clocks use monotonic time for durations and UTC timestamps for event identity.

| Metric | Operational definition | Type |
|---|---|---|
| Throughput | Successfully delivered application bytes divided by measured interval | Measured |
| Goodput | Unique useful payload bytes delivered divided by interval | Measured |
| Latency p50/p95/p99 | Percentiles of end-to-end request/flow observations | Measured |
| Packet loss | `(sent - received) / sent`, with capture points declared | Measured |
| SLA violation duration | Sum of intervals violating a preregistered latency, loss, or capacity condition | Derived from measured |
| Traffic-switch interruption | Time from last successful pre-switch response to first successful post-switch response | Measured |
| Established-flow disruption | Reset, timeout, or failed established flows divided by established flows active at migration start | Measured |
| State mismatch rate | Missing or inconsistent required state entries divided by source entries at validation snapshot | Measured in testbed |
| Unnecessary migration | A committed migration with non-positive realized benefit over the declared evaluation horizon | Derived |
| Forecast MAE/RMSE | Standard error measures on a time-ordered held-out split | Measured from trace |
| Interval coverage | Fraction of targets inside the declared prediction interval | Measured from trace |
| Interval width | Mean upper-minus-lower forecast bound, also normalized by capacity | Measured from trace |
| Load fairness | Jain fairness index over active vFW loads | Derived |
| Risk exposure | Time integral of assigned-node risk score weighted by handled traffic | Modeled estimate |
| Carbon exposure | Time integral of estimated energy multiplied by carbon intensity | Modeled estimate unless power measured |
| Fallback recovery | Time from detected invariant failure to validated source-path restoration | Measured |
| Controller overhead | Controller CPU, memory, decision duration, and control bytes | Measured |

Metric thresholds and capture locations will be frozen before confirmatory experiments.

