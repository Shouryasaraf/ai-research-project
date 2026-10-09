# Durable route intent and restart containment

`route_transaction.py` records exclusive ordered events and flushes files before route changes. On Linux it also flushes the journal directory. The controller reads each route back and rechecks the supplied validation predicate before each change and after the pair. This is a conservative transaction protocol, not an atomic update of two routers.

An exception during commit attempts to blackhole both controlled destination prefixes. Both directions are attempted even when one command fails. A containment failure is reported explicitly, never converted to success. The live controller now uses this transaction layer and rechecks policy plus supported conntrack fields; the isolated cold baseline intentionally skips state import as its negative-control definition.

## Restart contract

Recovery blocks both routes before reading the journal. A torn or inconsistent journal remains blocked. Restoration is allowed only with fresh source policy/state evidence supplied by the caller, rechecked throughout restoration. A saved pre-migration policy hash alone is insufficient. Uncertain established-flow state must remain unavailable until a safe recovery method has been demonstrated.

`scripts/route_restart_probe.py` forcibly exits a child process after the first or second real route change. A separate controller object then contains the routes, checks the resulting kernel routes, and restores the source only when both firewall policies are approved and both TCP state tables are empty. Three repetitions at each interruption point are the current probe design.

This verifies **no-flow restart containment and guarded restoration**. It does not prove established-flow recovery, losslessness, automatic crash detection or host-power-loss durability. The supervisor must invoke recovery; detection delay is not included in the recorded containment duration. Filesystem durability depends on host/filesystem guarantees, especially WSL-mounted storage. The caller must serialize access, as the lab entry points do with a lock.

## Reproduce

From the repository root in the isolated Linux environment:

```sh
sudo env PYTHONPATH=src python3 scripts/route_restart_probe.py --output artifacts/raw/reviewer-restart-probe
```

Use a fresh output path. No active lab may exist. The probe retains journal files and a result record, and cleans up the owned topology. Do not run on a production host.
