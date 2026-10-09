# Predictive proxy lifecycle evidence

bounded proxy lifecycle functional repetitions; not a benchmark

| Trial | Controller actions | Active paths | Source / target flows at admission | Clean |
|---|---|---|---:|---|
| lifecycle-20261009-v1 | PREWARM → SYNC → COMMIT | 1 → 2 → 1 | 2 / 1 | yes |
| lifecycle-20261009-v2 | PREWARM → SYNC → COMMIT | 1 → 2 → 1 | 2 / 1 | yes |
| lifecycle-20261009-v3 | PREWARM → SYNC → COMMIT | 1 → 2 → 1 | 2 / 1 | yes |

Each row is validated against its raw JSON record; SHA-256 values are in summary.json.
The `SYNC` action verifies source pinning and policy equivalence in this proxy path; it does not copy conntrack state.
Traffic demand and carbon/risk/resource inputs are modeled, and this is not a comparative benchmark.
Post-admission recovery was tested separately; this witness does not establish a complete production lifecycle.
