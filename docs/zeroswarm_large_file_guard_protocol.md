# Preselected larger Zero-SWARM normal-file guard check

Frozen before downloading/opening `ZeroSWARM Normal data_v2.pcap`. This file
is **unseen by the experimental liveness guard so far**, but comes from the
same publisher/record as the smaller v2b file already inspected with the
unchanged controller. The two files may overlap; no file-level independence
or confirmatory status is assumed. This is an exploratory within-record
generalization check, not an independent host or production study.

- Publisher [Zero-SWARM record](https://doi.org/10.5281/zenodo.15082260),
  CC BY 4.0; exact preselected classic PCAP name
  `ZeroSWARM Normal data_v2.pcap`, 232,217,247 bytes, publisher MD5
  `eee8b87e62c482fd574b6e78d32cb12b`. Use the committed checksum-
  checked header-only converter; store raw/derived data under Git-ignored
  `artifacts/raw` and record local SHA-256. No other source file may replace it
  if it fails parsing or is too short.
- Compare capture time range and the first 30 held-out rate bins with v2b
  before interpretation. If duplicated/overlapping, explicitly label the
  result as non-independent. Do not alter the slice or choose a favorable
  alternative.
- Run unchanged chronological 60/20/20 decisions and stateful offline
  replay. For the live lab, require at least 30 held-out one-second bins;
  otherwise report ineligibility. Use exactly seeds `137 139 149 151 157`,
  three policies `full_proposed_controller`,
  `full_liveness_guarded_experimental`, `reactive_threshold`, 30 steps,
  three generated TCP echo flows and endpoint capture. Use first 30 held-out
  bins and train-only normalization, with shuffled within-seed policy order.
- Report all paired completed-request goodput differences, route commits,
  request failures, trial-wide and strict pre/post-transition successful-
  request p95 RTT, packet-instance deficits, sender RST, repeated payload
  sequences and safety/route-journal checks. No outcome-based early stopping
  or threshold change. Preserve infrastructure failures and use a new
  versioned attempt if repair is required.

The guard's three-slot rule is uncalibrated and based on completed goodput,
which can understate offered load. Original packets/Modbus commands are not
replayed. Carbon/risk/resources remain modeled; no emissions, attack
prevention, zero-loss, exact downtime, full TCP-state or general superiority
claim follows from this check.
