# Data and Trace Provenance

## Current synthetic fixture

| Field | Value |
|---|---|
| Configuration | `configs/scenarios/synthetic_small.json` |
| Scenario ID | `synthetic-small-overload` |
| Origin | Deterministic project-authored synthetic fixture |
| Seeds | 7, 11, 19 |
| Workload values | Synthetic Mbps forecast with bounded seeded jitter |
| Carbon values | Synthetic node attributes in gCO2/kWh |
| Security-risk values | Synthetic dimensionless scores in [0, 1] |
| Labels | No external labels |
| Intended use | CI, schema validation, policy-interface parity and analysis-pipeline smoke testing |
| Prohibited interpretation | Real workload, physical energy, measured emissions, observed attack probability, network performance, or publication comparison |

The complete JSON configuration is hashed with canonical key ordering. Every run record stores that SHA-256 digest, seed, environment, scenario ID and an explicit synthetic-input flag.

## External data

The first historical [MAWI samplepoint-B capture dated 2000-12-28](https://mawi.nezu.wide.ad.jp/mawi/samplepoint-B/2000/200012281400.html) was incorporated for offline traffic forecasting and controller decisions, then for bounded rate-derived lab payloads. A later, separate [NESO regional carbon forecast replay](results/neso-carbon-replay-20261010/results.md) supplies externally sourced *forecast intensity*, not measured vFW power or emissions. No external vulnerability, anomaly, or attack dataset has been incorporated. Network downloads are not required for unit tests.

A separate [MAWI samplepoint-B capture dated 2005-01-01](https://mawi.wide.ad.jp/mawi/samplepoint-B/2005/200501011400.html) was later converted into 901 one-second rates and used for another offline decision evaluation and a six-trial captured Linux pilot with scaled/capped payloads. It is a second historical **time segment from the same samplepoint**, not an independent site or recent workload. The publisher's packet and original-byte totals match the local header-only conversion; hashes, metrics, and limitations are in [the transfer report](results/mawi-transfer-20261010/results.md). The original capture, derived CSV, and sidecar remain Git-ignored and are not redistributed. This does not supply attack, carbon, or actual vFW migration labels.

The NESO converter in `vfw_research.neso_carbon` imports only 48 aligned half-hourly regional forecasts per selected UTC day, with CC BY 4.0 attribution and publisher-response/derived-CSV hashes in ignored sidecars. The replay maps those regions to **hypothetical** scenario candidates and changes only their carbon-intensity attributes. It does not assert that WSL namespaces are hosted in Great Britain or that published forecast intensity is realized emissions.

The offline CSV adapter in `src/vfw_research/trace_adapter.py` enforces a minimal sidecar and strict UTC/unit/checksum/time-series validation; see `external_trace_contract.md`. It does not certify licensing or prove that any real trace has been evaluated.

`vfw_research.mawi_trace` streams the compressed classic pcap, reads only packet-record headers, and sums the original-length field into one-second UTC Mbps bins. It does not inspect or export addresses or payload. Raw capture, derived CSV, provenance sidecar, and result JSON are local and Git-ignored under `artifacts/raw/`. The exact source URL, SHA-256 checksums, packet count, byte count, retrieval time, preprocessing, and limitations are in the sidecar and verification log. The packet count and original-length byte count match the official capture page exactly. The [MAWI privacy guidelines](https://mawi.nezu.wide.ad.jp/mawi/guideline.txt) restrict use to research and prohibit privacy-invasive actions; raw data is not redistributed here. The [MAWI FAQ](https://mawi.nezu.wide.ad.jp/mawi/faq.html) notes capture loss and timestamp limitations. This is historical backbone traffic, not vFW demand telemetry, and has no migration, attack, carbon, or SLA labels.

## Synthetic forecast families

`src/vfw_research/workloads.py` deterministically generates five one-minute traffic-rate families: steady, periodic bursts, gradual trend, a short flash crowd, and a step change confined to the held-out test segment. Each value is a synthetic Mbps rate and is never represented as measured packet traffic. The family, seed, length, trace SHA-256, split counts and runtime are saved by `vfw_research.forecast_evaluation`. The evaluation observes a real next value before updating the model's point state; it does not create labels from its own forecasts. The conformal radius stays fixed after calibration.

`vfw_research.forecast_batch` writes separate exclusive-write records for every declared family/seed pair and a derived summary. The 2026-10-07 pilot used all five families and seeds 0–9 (50 records, 240 observations each). It is a descriptive synthetic pilot, not a confirmatory comparison or a real workload trace.
