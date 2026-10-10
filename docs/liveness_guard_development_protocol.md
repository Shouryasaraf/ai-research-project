# Experimental liveness-guard development protocol

The preexisting full controller stalls on the three Cyber4OT PLC-port normal
members when the split-conformal interval width remains above its 0.20 gate.
This is a post-result **development response**, not a prespecified improvement
or confirmatory result. The original `full_proposed_controller` remains
unchanged. The separate `full_liveness_guarded_experimental` policy uses an
engineering three-slot rule. After three consecutive *observed completed-
goodput* samples at or above the overload trigger and three consecutive
baseline uncertainty WAITs, it can request SYNC and then COMMIT. It retains
hard security/telemetry validation, feasible target, benefit threshold, warm
target and state synchronization. Once routed to target, it suppresses
duplicate migration recommendations. Completed goodput can **understate**
offered load in congestion; the rule is not yet calibrated or proven live.

An initial one-trial development smoke on already-used PLC-port member 070
exercised the escape, passed supported state and capture checks, and revealed
that post-route decision reporting needed suppression. That reporting fix was
made before this protocol. Preserve the smoke record separately; it is not a
paired result.

## Frozen development batch

- Use **only** previously opened Cyber4OT normal PLC-port member 070. No
  independent confirmation can be claimed from it. Reuse the existing
  one-second rate CSV and provenance with unchanged train/calibration/test
  split, first 30 held-out seconds, three generated TCP echo flows, and
  isolated six-namespace topology.
- Run exactly five seeds `83 89 97 101 103`, each with three policies:
  original full, experimental liveness guard, and reactive threshold.
  Deterministically shuffle policy order within each seed, capture both
  endpoints and use a fresh exclusive batch directory. No outcome-based
  stopping or threshold adjustment.
- Main development checks: whether the experimental policy makes one valid
  route commit, whether its SYNC/COMMIT carries supported state and route
  journal validation, and whether every guard/invariant remains satisfied.
  Report paired goodput, failed requests, p95 successful-request RTT,
  capture deficits, sender RST, and repeated payload sequences as descriptive
  secondary outcomes. Every raw trial and negative observation stays visible.

The guard was designed after examining this member, so even a favorable result
would only establish a functional development pilot. An unseen source and
independent host remain separate gates. A three-observation rule is not a
calibrated optimum, and no energy, security-risk or general performance claim
follows from this batch.
