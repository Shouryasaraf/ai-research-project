# Threat Model and Security Invariants

## Defensive scope

The research system defends placement and migration decisions against unsafe or degraded candidate nodes, stale/malformed telemetry, policy mismatch, incomplete state synchronization, and target failure. Attack-risk inputs are controlled indicators or trace replay inside an isolated lab.

Out of scope: offensive exploitation, scanning third-party systems, stealth, persistence, credential access, and claims of protection against unknown vulnerabilities.

## Machine-checkable invariants

Before COMMIT, all of the following must hold:

1. Source and target policy hashes match the expected policy.
2. The target is healthy and not prohibited/quarantined.
3. The enforced traffic path contains at least one validated vFW.
4. Required default-deny behavior is enabled.
5. Target capacity can accommodate the uncertainty-aware forecast.
6. State mismatch is at or below the configured tolerance.
7. The audit sink is available.
8. The calculated net benefit exceeds the adaptive threshold.

Failure of invariants 1–7 causes FALLBACK rather than a compensating weighted score. Failed benefit causes WAIT rather than an unsafe commit.

## Fallback objective

Fallback must retain or restore the last validated source path, remove any unvalidated target assignment, preserve an audit record, and expose recovery time. A fallback event is not counted as a successful migration.

