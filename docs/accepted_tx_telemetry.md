# Socket-accepted transmit telemetry

The isolated TCP echo generator now records `accepted_tx_payload_bytes` and
`accepted_tx_mbps` for every one-second sample, alongside the existing
`scheduled_mbps` and completed-request `goodput_mbps`. A payload is counted
when `sendall` returns and the application has handed those bytes to the
local TCP socket, using a monotonic timestamp under the sample lock.
Intervals are half-open: `[previous_sample, current_sample)`. Failed sends
are not counted. Each final request event records
`accepted_by_socket_monotonic` so sample totals can be audited.

This is an observed **application-to-socket acceptance** rate. It is not
wire-offered rate, network-interface throughput, a TCP acknowledgement, or
true unconstrained offered demand. A blocked `sendall` is attributed when it
finishes, and request/response pacing can reduce attempts during congestion.
The scheduled rate is an experimental input, not a live measurement. The
new field is instrumentation only: the original controller and experimental
liveness guard still use the old decision logic; no threshold has been tuned
from the new measurement.

A post-change six-step, three-flow captured smoke run (seed 167, Zero-SWARM
v2, one full-controller policy) completed with a valid endpoint capture, one
route transaction, zero application errors and no residual namespaces. In
step 1 the scheduled, accepted and completed rates were approximately
0.992, 0.893 and 0.843 Mbps respectively. This demonstrates that these
quantities can diverge; one smoke run does not calibrate an overload detector.
An independent sum of all 347 final event timestamps and payload lengths
reproduced the accepted byte count in each of the six sample windows exactly.
The raw record and captures are Git-ignored under
`artifacts/raw/live-accepted-tx-smoke-20261011-v1`. The two older research
batches do not have this field and are not retroactively modified.

For any future guard revision, freeze a rule and test it on separate traffic
before comparing outcomes. Treat acceptance-rate lag and return-time
attribution explicitly; do not call this measured attack intensity or carbon.
