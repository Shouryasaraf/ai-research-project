# Controller Algorithm

## Candidate filtering and ranking

1. Reject candidates that are prohibited, unhealthy, over the maximum risk limit, outside CPU/memory/latency requirements, or unable to accommodate the forecast upper bound.
2. Normalize and log capacity, latency, carbon, risk, and uncertainty-headroom components for remaining candidates.
3. Rank feasible candidates with the configured weights. A weighted score never overrides a hard security constraint.

## Migration decision

```text
placement = rank(feasible candidates using forecast upper bound)
violations = validate_security_invariants(source, target, path, state, audit)
benefit = operational + carbon + risk_reduction
          - migration_cost - disruption - uncertainty - overhead
threshold = contextual_threshold(state_size, flows, uncertainty,
                                 failures, SLA, cooldown, headroom)

if violations:
    FALLBACK
elif no feasible candidate:
    WAIT
elif forecast upper bound is below the overload trigger:
    WAIT
elif forecast interval is too wide:
    PREWARM
elif target is not warm:
    PREWARM
elif state is not synchronized:
    SYNC
elif benefit <= threshold:
    WAIT
else:
    COMMIT
```

## Fallback

The fallback checkpoint is the last explicitly validated configuration. Activating a candidate does not overwrite that checkpoint. After post-commit validation succeeds, the active candidate may be promoted. On failure, restoration is idempotent and records the failed configuration, reason, and measured recovery duration.

## Complexity

For `n` candidate nodes, placement filtering and scoring are `O(n)` and sorting is `O(n log n)`. Benefit, threshold, invariant, and uncertainty-gate calculations are `O(1)` with respect to node count. Reference state synchronization is `O(f log f)` for `f` eligible flow records because canonical digest generation sorts the flow keys.

