# Independent-host gate

The completed namespace experiments run under one WSL2 Linux kernel on the
user's Windows computer. Additional namespaces or another WSL distribution
on this same computer do **not** provide independent-host replication. The
local inventory on 2026-10-11 showed one Ubuntu WSL2 distribution and no
accessible second Linux machine. This gate remains open.

The repository now includes a read-only candidate-host check:

```sh
bash scripts/independent_host_preflight.sh
```

It lists required tools, Python/kernel versions, root status, checkout state
and any existing `vfwlab3-*` namespace collision. It does not alter the host,
inspect private IP addresses, prove the host is physically independent, or
grant permission to run a privileged lab. Run it in a fresh private clone or
approved artifact extraction on a **different physical computer or separately
operated VM host**. WSL2 on a different computer is acceptable for a second
host check if that fact is independently recorded, but it is still not a
production multi-host deployment.
The checkout check normalizes Windows CRLF files when read through WSL; it
still flags substantive tracked or untracked changes.

Minimum handoff for the owner: identify one authorized second host and how
the private repository can be cloned there (normal GitHub authentication or
an approved source transfer). No CAIDA access or IPv4-whitelist form is
required for the synthetic workload. Do not send passwords, private keys or
IP-whitelist entries in chat. Do not redistribute third-party original PCAPs
in the artifact. Preserve the exact revision, source fingerprint, kernel and
package versions, raw batch records, captures and any failed attempts.

After a clean preflight and explicit approval to run a disposable privileged
lab there, run the non-privileged suite first. Then use a new, frozen seed and
workload protocol for a captured full/reactive batch, analyze it from its
records, and compare it with the current single-host evidence. Do not
retroactively label existing WSL runs “independent.” The current route lab
still places client, firewalls and server inside namespaces on that second
computer, so this would test *host reproducibility*, not a firewall migration
that crosses physical machines. A true cross-host migration requires a
separate transport/route architecture and security review.
