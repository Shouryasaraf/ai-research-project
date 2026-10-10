# Frozen independent-publisher Zero-SWARM transfer protocol

Frozen before downloading or opening the selected packet file. This tests the
**unchanged** controller after the negative Cyber4OT PLC-port extension; it
does not use those negative results to tune a gate. Zero-SWARM is a separate
publisher and Factory I/O Modbus-oriented testbed, but the run is still on the
same WSL2 machine with generated TCP echo traffic. It is not an independent
host or production-vFW validation.

## Source and preselected file

- Centre for Research and Technology Hellas, Lazaridis and Mpatziakas,
  [*Modbus Normal and Malicious Network Traffic*](https://doi.org/10.5281/zenodo.15082260),
  available 2025-03-25. The public Zenodo metadata identifies the license as
  CC BY 4.0. No account or IPv4-whitelisting form is required; an ordinary
  HTTPS download does expose the connection IP to the host.
- Select **only** `ZeroSWARM Normal data_v2b.pcap`, the 18,119,840-byte normal
  file. Publisher MD5 `9f8235fcdbfcacb32e7a70db14fc6c74` must match;
  record local SHA-256. The larger normal file and attack files are not
  substitutes under this protocol. Keep raw and derived files Git-ignored.
- Use the committed `zeroswarm_trace` converter, which reads classic-PCAP
  headers and original packet lengths only, rejects malformed/out-of-order
  captures, fills internal zero bins, and exports one-second Mbps. No source
  packet payload, IP address or Modbus command is copied to the derived CSV.
  If parsing fails, preserve the failure and do not switch files.

## Fixed evaluations

1. Run the existing chronological 60/20/20 forecast/decision evaluator and
   stateful replay with two-slot cooldown and unchanged scenario. Report all
   policies/forecasters but preselect fixed `ewma_conformal` and full versus
   reactive as the main offline comparison. Capacity and action-cost outputs
   are modeled proxies.
2. If the valid rate series has at least 30 held-out one-second observations,
   run five paired seeds `107 109 113 127 131`, policies
   `full_proposed_controller` and `reactive_threshold`, exactly 30 steps,
   three generated TCP echo flows, endpoint capture and fresh exclusive output
   path. Use train-only 90th-percentile rate scaling and first 30 held-out
   seconds exactly as the existing runner. Do not tune or truncate based on
   observed outcomes. If the file cannot support this setup, report the
   validity failure and do not replace it under this protocol.
3. Primary live descriptive contrast: paired full-minus-reactive
   completed-request goodput (Mbps), all five differences, mean and
   descriptive bootstrap interval. Secondary: route commits, decision reasons,
   failed requests, successful-request p95 RTT, captured packet-instance
   deficits, sender TCP RST and repeated payload-sequence instances.

Every trial must have a completed record, source/config/trace digests, valid
capture hashes and endpoint matching, zero capture-kernel drops and no residual
owned namespaces. Preserve infrastructure and application failures; rerun only
under a new versioned attempt, without favorable member selection. Five seeds
reuse one held-out trace segment and are not independent workloads. No
emissions, attack-prevention, zero-loss, full-state, exact-outage, or general
superiority claim follows. This is an independent-*publisher* transfer only.
