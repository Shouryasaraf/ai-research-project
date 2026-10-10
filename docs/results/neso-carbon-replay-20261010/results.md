# NESO regional carbon-signal placement replay (exploratory)

This is an offline preference check with **externally sourced carbon forecasts** and otherwise modeled vFW candidates. It is not a deployment, measured power draw, actual emissions, or a security-risk reduction experiment.

## Source and conversion

The [National Energy System Operator Carbon Intensity API](https://api.carbonintensity.org.uk/) supplied 2025-01-01 UTC regional **forecast** values for [North Scotland (region 1)](https://api.carbonintensity.org.uk/regional/intensity/2025-01-01T00:00Z/2025-01-02T00:00Z/regionid/1) and [London (region 13)](https://api.carbonintensity.org.uk/regional/intensity/2025-01-01T00:00Z/2025-01-02T00:00Z/regionid/13). NESO's [site and terms](https://www.carbonintensity.org.uk/) identify the API as CC BY 4.0; this report attributes the source. The regional values are forecasts of grid carbon intensity in gCO₂/kWh, **not metered actuals or vFW electricity use**.

Two local API JSON responses were stored in ignored `artifacts/raw/neso-carbon-20250101-v1/`. SHA-256: North Scotland `1486322de86ec7bffdf6be38ecc5506d6f3c35d2c7ceb0ea6b4920b4a1785831`, London `c8c3caa934c9cbebb1d767b44c06481db0ff63484067eece600de05b1d43e160`. The strict converter selected exactly 48 consecutive half-hour UTC intervals for the requested day from each response, rejecting gaps, duplicates, negative forecasts, wrong regions and non-UTC intervals. Derived CSV SHA-256: North Scotland `3e674bdfe598c276b68ea849b6d003d9691229543796bd890add91432cd3f241`; London `35a46ff551d08420e9eace129e6224151db9ecd3247ba9ad8ebcce9b16b15368`. The generic carbon trace adapter then revalidated units, spacing and hashes.

## Paired decision result

The existing `synthetic_small` scenario supplied hypothetical capacities, CPU/memory headroom, latency, risk, benefit, workload forecast and source capacity. Its first eligible node is *mapped only for this replay* to North Scotland; its second to London; the third remains prohibited. For each aligned carbon forecast slot, full and carbon-unaware policies saw the same non-carbon inputs. No candidate was actually deployed, and each slot resets to the same modeled state.

| Policy | North Scotland candidate | London candidate | Other/prohibited | COMMIT recommendations |
|---|---:|---:|---:|---:|
| Full controller | 48 | 0 | 0 | 48 |
| Carbon-unaware ablation | 0 | 48 | 0 | 48 |

Candidate choices differed in 48/48 slots. North Scotland's published forecast was 0 gCO₂/kWh for all 48 slots; London's ranged 36–101, mean 63.75 gCO₂/kWh. The full policy preferred the lower input under this stark two-region contrast, while the ablation preferred the modeled lower-latency/risk candidate. This is **not** a quantified carbon saving: no node power, placement duration, network transport energy, real geographic vFW site, or actual intensity was measured. The result was inspected during development and must not be described as confirmatory.

The [tracked compact summary](summary.json) records the two source CSV hashes and the exact raw replay hash. The full local replay JSON, including per-slot decisions, is ignored at `artifacts/raw/neso-carbon-20250101-v1/placement-replay.json` (an identical exclusive-write `placement-replay-v2.json` was used to produce the summary), SHA-256 `d7e4e2c6f6edb587b302c7170bbda1feeec725ef691e2f86e02fc805634c04e2`. A broader region/day sample and independent physical energy measurements are needed for emissions claims.
