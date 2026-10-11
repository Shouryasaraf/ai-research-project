# Frozen second-host reproducibility check

Frozen on 2026-10-12 **before** access to the candidate second device and before any second-host outcome. This is a host-reproducibility check for the existing isolated namespace lab, not an independent real-world workload, a cross-machine vFW migration, or a confirmatory superiority study. The synthetic family definitions have already been inspected on the development host; only these particular seeds are newly fixed for this check.

## Prerequisites and scope

- Use a different physical computer or separately operated VM host, with a fresh private checkout of the exact committed revision. Record whether it is native Linux or WSL2, the kernel release, the Git revision, and the fact that it is a different device. Do not record private IP addresses, credentials or hardware serial numbers in published artifacts.
- Run `bash scripts/independent_host_preflight.sh` and `PYTHONPATH=src python3 -m unittest discover -s tests -q` before any privileged lab. A preflight failure is an infrastructure result; resolve it before starting a new, named attempt. Do not silently skip the failed check.
- Only after the device owner authorizes a disposable root-operated namespace/nftables/tc lab on that machine, run the captured batch below. It creates and removes `vfwlab3-*` namespaces and modifies only their lab network state; the preflight checks for a name collision. The owner retains control of the machine and output files.

## Fixed experiment

- Policies: `full_proposed_controller` and `reactive_threshold`; no retuning, guard substitution, threshold change or result-dependent selection.
- Families, in order: `step`, `bursts`, `flash`. Seeds for each: `191 193 197`. Three persistent TCP flows, 12 one-second demand steps, source/target path settings supplied by the existing runner, paired endpoint capture. This gives nine seed/family pairs and 18 policy trials. The same seed is paired within a family; families are not independent production sites.
- Primary descriptive endpoint: the full-minus-reactive completed-request goodput difference for each paired seed and the family mean. Secondary outcomes: request failures, trial p95 successful-request RTT, actual route commits, endpoint packet-instance deficits and capture validity. A higher mean on one family is not a general advantage. No formal superiority test or universal packet-loss claim is authorized by this small check.
- Preserve all attempts. Do not stop or replace a family because its outcome is unfavorable. Stop on an infrastructure or safety failure, retain its directory, diagnose it, and rerun only under a newly named attempt with the change documented. Do not use `--resume` to hide an incomplete trial.

From a clean checkout on the second host, after the prerequisites and authorization:

```sh
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/second-host-20261012-v1-step --family step --seeds 191 193 197 --policies full_proposed_controller reactive_threshold --steps 12 --flows 3 --capture
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/second-host-20261012-v1-step artifacts/processed/second-host-20261012-v1-step
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/second-host-20261012-v1-bursts --family bursts --seeds 191 193 197 --policies full_proposed_controller reactive_threshold --steps 12 --flows 3 --capture
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/second-host-20261012-v1-bursts artifacts/processed/second-host-20261012-v1-bursts
sudo env PYTHONPATH=src python3 scripts/live_experiment_batch.py --output artifacts/raw/second-host-20261012-v1-flash --family flash --seeds 191 193 197 --policies full_proposed_controller reactive_threshold --steps 12 --flows 3 --capture
PYTHONPATH=src python3 -m vfw_research.live_analysis artifacts/raw/second-host-20261012-v1-flash artifacts/processed/second-host-20261012-v1-flash
```

Each analyzer must independently verify the captured batch and its exact source snapshot. Preserve the raw batch directories, processed reports, preflight output, test output, Git revision, kernel/tool versions and failed attempts. Compare this host's outcomes with the same synthetic families on the development host as a **reproducibility** observation, not as an independent-traffic-source result. Do not copy third-party original PCAPs into the artifact. The journal-readiness gates in `publication_claim_ledger.md` remain open after this check unless separately satisfied.
