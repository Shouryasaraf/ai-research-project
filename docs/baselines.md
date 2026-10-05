# Baseline and Ablation Interfaces

`policies.py` exposes every policy through one `PolicyRunInput` and returns a structured `PolicyOutcome`. The current implementation supports:

1. static/no migration;
2. reactive utilization threshold;
3. prediction-only threshold;
4. uncertainty-aware without carbon or attack-risk placement terms;
5. risk-unaware placement;
6. carbon-unaware placement;
7. cold migration mode;
8. fixed benefit threshold;
9. full proposed controller.

The interface is implemented so identical scenarios can be passed to every policy. These are controller decisions only. It would be scientifically invalid to interpret them as performance comparisons until each outcome drives the same real or emulated workload under the same resource constraints and measured result schema.

Security invariants remain active for every migrating policy. A baseline may ignore a risk score for placement comparison, but it may not bypass mandatory policy/path health controls.

