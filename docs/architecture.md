# Architecture and Data Flow

## Control flow

1. Telemetry adapters produce timestamped node, vFW, link, flow, carbon, and risk observations.
2. The workload forecaster produces a point forecast and calibrated lower/upper interval.
3. Placement applies non-negotiable health, capacity, latency, allow-list, and risk constraints.
4. Feasible nodes are ranked by capacity, latency, carbon intensity, security risk, and uncertainty-aware headroom.
5. The benefit evaluator calculates each positive and negative term in normalized utility points.
6. The adaptive threshold changes with state size, flow count, forecast uncertainty, recent failures, SLA criticality, cooldown, and target headroom.
7. The uncertainty gate selects WAIT, PREWARM, SYNC, COMMIT, or FALLBACK.
8. The migration orchestrator executes only valid state transitions and records audit events.
9. Security invariants are rechecked before commit. Failure routes to fallback/abort.
10. The experiment runner persists raw inputs, configuration, decisions, transitions, network observations, and run status.

## Trust boundaries

- The management/control network must be isolated from generated experiment traffic.
- Telemetry is untrusted input: stale, missing, and out-of-range values must fail safely.
- Carbon and risk signals are modeled inputs unless their provenance demonstrates otherwise.
- A target node is not trusted merely because it obtains a favorable weighted score; it must pass hard constraints and invariant validation.

## What Stage 1 does and does not do

Stage 1 implements deterministic domain models, constrained placement, benefit and threshold calculation, invariant checks, uncertainty actions, state-machine validation, and structured audit records. It does not instantiate containers, enforce packet paths, transfer conntrack state, measure real downtime, or validate flow continuity.

