# External Dataset Candidate Screen and Pilot Selection

Screened 2026-10-07 using source-owner pages. A single MAWI samplepoint-B capture was subsequently downloaded and converted for a **forecast-only pilot**; it is not redistributed or committed. Other candidates remain unadopted.

| Candidate | Relevant content | Access/terms boundary | Decision |
|---|---|---|---|
| [MAWI Working Group Traffic Archive](https://mawi.nezu.wide.ad.jp/mawi/) | Anonymized packet traces from WIDE backbone links | [Research-only privacy guidance](https://mawi.nezu.wide.ad.jp/mawi/guideline.txt); packet traces require aggregation and careful treatment of capture limitations | [2000-12-28 samplepoint-B capture](https://mawi.nezu.wide.ad.jp/mawi/samplepoint-B/2000/200012281400.html) selected for a small forecast-only pilot; historical traffic is not representative of current vFW deployment |
| [CAIDA Anonymized Internet Traces](https://www.caida.org/catalog/datasets/request_user_info_forms/passive_dataset_request/) | Backbone packet traces | Requires a user request and acceptable-use agreement; [CAIDA FAQ](https://www.caida.org/catalog/datasets/data-usage-faq/) warns against unintended sharing | Do not acquire or place in this repository without the researcher's application/terms review |
| [NESO Carbon Intensity API](https://api.carbonintensity.org.uk/) | Great Britain carbon-intensity series | [Published API terms](https://github.com/carbon-intensity/terms/) require review; represent grid intensity, not vFW power or emissions | Candidate carbon input after endpoint, date range, terms and attribution review |

Using a real traffic trace does not make the network deployment “real-world”: this pilot runs offline forecasting, not packet replay through vFWs. The current vFW topology is isolated single-host emulation, and carbon and attack-risk values remain modeled. A combined evaluation must distinguish trace-driven input from packet-path measurement and model-derived emissions.
