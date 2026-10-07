# Working Prior-Art Matrix

Checked 2026-10-07 against primary publisher, author-hosted, or original-preprint pages. “Overlap” identifies subject matter already published; “unknown” means the full mechanism has not yet been established from an abstract. This is not an exhaustive survey or a proof of novelty.

| Primary work | Verified overlap | Implication for this project | Evidence page |
|---|---|---|---|
| Forti, Paganelli, Brogi, *Probabilistic QoS-aware Placement of VNF Chains at the Edge* (2019 preprint; 2022 journal) | Probabilistic variation in infrastructure plus security-aware eligible placements. | Uncertainty/security-aware placement alone is not a safe novelty claim. | [Original preprint](https://arxiv.org/abs/1906.00197) |
| Bari, Chowdhury, Boutaba, *ESSO: An Energy Smart Service Function Chain Orchestrator* (2019) | Migration and placement of SFCs to reduce brown-energy use and carbon footprint. | Carbon-aware SFC migration alone is not novel. Its objective and power model differ from ours and require full-text comparison. | [Author-hosted paper](https://cs.uwaterloo.ca/~mfbari/files/j8.pdf) |
| Ibrahimpasic, Han, Schotten, *AI-Empowered VNF Migration as a Cost-Loss-Effective Solution for Network Resilience* (2021) | Explicit balance of stateful migration operations cost and outage loss. | Cost-benefit migration decisions alone are not novel. | [Original preprint](https://arxiv.org/abs/2101.09343) |
| *Moving Target Defense for Virtual Network Functions* (NOMS 2020) | Security-motivated VNF state migration for co-residency attacks. | Security-risk-driven migration and state transfer are existing ideas. | [IEEE publisher record](https://ieeexplore.ieee.org/document/9110334/) |
| *Let the State Follow Its Flows: An SDN-Based Flow Handover Protocol to Support State Migration* (NetSoft 2018) | Flow handover to support network-function state migration. | Flow handover/flow pinning should be treated as prior art; exact packet/state guarantees need full-text comparison. | [IEEE publisher record](https://ieeexplore.ieee.org/document/8460007) |
| Yang, Chen, Yen, *Joint Carbon-Latency Optimization for Online Service Function Chain Deployment* (GLOBECOM 2025) | Time-varying carbon intensity, time-series forecasting, online SFC deployment. | Forecast-informed carbon-aware placement is already studied. | [University publication record](https://scholar.nycu.edu.tw/en/publications/joint-carbon-latency-optimization-for-online-service-function-cha/) |

## Working positioning, not a novelty claim

The testable contribution is the **specific integration and ordering** of calibrated traffic uncertainty, feasible carbon/security placement, warm-up/state checks, an adaptive decision threshold, and a fail-closed fallback in a stateful vFW controller. Whether that exact combination is absent from prior work remains unresolved until full-text and citation-chain review. Experiments must isolate each component with matched baselines and report trade-offs, including failures. Current code demonstrates a source-pinned proxy transition and live firewall paths, *not* transparent established-TCP route migration.
