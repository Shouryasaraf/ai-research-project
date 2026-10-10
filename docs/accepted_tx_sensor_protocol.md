# Frozen socket-accepted signal diagnostic

Freeze this protocol before examining outcomes from the new telemetry. It is
an **engineering sensor diagnostic**, not a controller-performance study or
a calibration of a deployable overload threshold. The source-path shaper is
1 Mbps and no migration is allowed, so both observed signals can be compared
under the same congestion. The schedule is generated before traffic starts
and is not fed to the controller as a live observation.

- Use the five existing synthetic live demand families in this fixed order:
  `step`, `steady`, `bursts`, `trend`, `flash`.
- For each family run exactly seeds `173 179`, policy
  `static_no_migration`, 12 one-second steps, three TCP echo flows and paired
  endpoint captures. Use fresh versioned raw paths, no outcome-based retries
  or family selection. Verify 10/10 trial records, source hashes, captures,
  no remaining namespace and zero application errors before aggregating.
- For each of the 120 samples, classify the **planned** overloaded interval
  as `scheduled_mbps > 1.0` (the modeled source shaper). Separately classify
  socket-accepted and completed-goodput trigger hits using the existing
  controller value `>= 0.8 Mbps`. Tabulate TP/FN/FP/TN against the planned
  label for each signal, by family and overall, plus per-family mean absolute
  scheduled-minus-signal gap. Also show accepted-minus-completed means in
  planned-overload and planned-nonoverload samples.
- Do not optimize the 0.8 cutoff on these data or call the schedule actual
  wire arrival rate. A response-gated client can stop attempting new sends
  while an earlier request blocks; even `accepted_tx_mbps` can understate
  latent demand. Capture packet deficits and repeats, if any, are finite
  endpoint observations, not packet-loss probabilities.

Keep all source, raw records and captures Git-ignored; track a generated
summary with hashes and an interpretation that acknowledges same-host,
synthetic, repeated-seed limitations. Do not change the guard in response to
this diagnostic without a separate frozen specification and new data.
