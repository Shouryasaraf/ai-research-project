# External Trace Import Contract

No external dataset is currently bundled or claimed as evaluated. `vfw_research.trace_adapter.load_trace` provides an offline, strict import boundary for a trace the research team is authorized to use. It never downloads data.

The CSV must have exactly two columns, `timestamp_utc,value`, at a constant interval with explicit UTC ISO-8601 timestamps. Values must be finite and non-negative. A risk score must also be at most 1. The companion JSON provenance sidecar must contain:

| Field | Meaning |
|---|---|
| `kind` | `traffic`, `carbon`, or `risk` |
| `unit` | Exactly `Mbps`, `gCO2/kWh`, or `score_0_1`, corresponding to kind |
| `source` | Stable `https://`, `http://`, or `doi:` reference |
| `license` | Exact license/terms identifier reviewed by a human; a non-empty value is **not** proof of redistribution permission |
| `version` | Dataset release/date/version |
| `retrieved_utc` | Explicit UTC acquisition timestamp |
| `sha256` | SHA-256 of the exact CSV bytes |
| `sampling_interval_seconds` | Positive integer interval |
| `preprocessing` | Description of any conversion, aggregation, anonymization or filtering; write `none` if none |
| `missing_data_policy` | Description of gap handling; the current adapter rejects any gap |

The adapter rejects checksum mismatch, wrong units, malformed/missing metadata, duplicate or irregular timestamps, non-UTC time, and out-of-range values. These checks establish format and provenance completeness only. They do **not** validate a source's legal terms, the accuracy of a publisher's measurements, or whether a traffic trace represents a vFW deployment. External source selection, license review, preprocessing code, and a documented train/calibration/test split are still required before using one in a paper.

After independently reviewing the dataset and making a compliant CSV and sidecar, evaluate an imported **traffic** trace with:

```bash
python -m vfw_research.forecast_evaluation --trace-csv path/to/traffic.csv --provenance path/to/traffic.provenance.json --output artifacts/raw/imported-forecast-001.json
```

This uses chronological 60/20/20 train/calibration/test segments and a one-sample-ahead horizon at the declared sampling interval. The output retains source, license, version, retrieval timestamp, preprocessing, missing-data policy, and the exact CSV checksum. Carbon and risk traces are validated by the adapter but are not inputs to this traffic forecaster.
