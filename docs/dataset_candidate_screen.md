# External Dataset Candidate Screen (not adopted)

Screened 2026-10-07 using source-owner pages. No data was downloaded, transformed, redistributed, or used for an experiment.

| Candidate | Relevant content | Access/terms boundary | Decision |
|---|---|---|---|
| [MAWI Working Group Traffic Archive](https://mawi.nezu.wide.ad.jp/mawi/) | Anonymized packet traces from WIDE backbone links, including daily samplepoint-F data | Site states research-only use and privacy restrictions; packet traces require aggregation to Mbps and careful treatment of sampling, link changes and known anomalies | Candidate for a future workload trace; review privacy guidance and select an exact dated capture before acquisition |
| [CAIDA Anonymized Internet Traces](https://www.caida.org/catalog/datasets/request_user_info_forms/passive_dataset_request/) | Backbone packet traces | Requires a user request and acceptable-use agreement; [CAIDA FAQ](https://www.caida.org/catalog/datasets/data-usage-faq/) warns against unintended sharing | Do not acquire or place in this repository without the researcher's application/terms review |
| [NESO Carbon Intensity API](https://api.carbonintensity.org.uk/) | Great Britain carbon-intensity series | [Published API terms](https://github.com/carbon-intensity/terms/) require review; represent grid intensity, not vFW power or emissions | Candidate carbon input after endpoint, date range, terms and attribution review |

Using real traffic and carbon series together would not automatically make the network deployment “real-world”: the current vFW topology is an isolated single-host emulation, and attack-risk values remain modeled unless a separately validated source is incorporated. A combined evaluation must distinguish trace-driven input from packet-path measurement and model-derived emissions.
