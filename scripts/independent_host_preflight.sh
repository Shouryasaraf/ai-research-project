#!/usr/bin/env bash
# Read-only readiness check. Run from a fresh Linux checkout on the candidate host.
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$root"

missing=0
for tool in python3 ip nft conntrack tc tcpdump ethtool sha256sum; do
    if command -v "$tool" >/dev/null 2>&1; then
        printf 'tool_%s=available\n' "$tool"
    else
        printf 'tool_%s=missing\n' "$tool"
        missing=1
    fi
done

printf 'python_version='
python3 --version 2>&1 || true
printf 'kernel_release='
uname -r
if grep -qi microsoft /proc/sys/kernel/osrelease; then
    printf 'wsl_kernel=yes\n'
else
    printf 'wsl_kernel=no\n'
fi

if command -v git >/dev/null 2>&1 && [[ -d .git || -f .git ]]; then
    revision="$(git -c "safe.directory=$root" rev-parse HEAD 2>/dev/null || true)"
    printf 'git_revision=%s\n' "${revision:-unavailable}"
    # Match the Windows checkout's text normalization when WSL reads NTFS;
    # otherwise Git reports unchanged CRLF result tables as modified.
    if [[ -n "$(git -c "safe.directory=$root" -c core.autocrlf=true status --porcelain 2>/dev/null)" ]]; then
        printf 'working_tree=dirty\n'
        missing=1
    else
        printf 'working_tree=clean_or_unavailable\n'
    fi
else
    printf 'git_revision=unavailable\n'
fi

if command -v ip >/dev/null 2>&1; then
    if ip netns list | awk '{print $1}' | grep -q '^vfwlab3-'; then
        printf 'lab_namespace_collision=yes\n'
        missing=1
    else
        printf 'lab_namespace_collision=no\n'
    fi
fi
if [[ "$EUID" -eq 0 ]]; then
    printf 'root_for_privileged_lab=yes\n'
else
    printf 'root_for_privileged_lab=no\n'
fi

if [[ "$missing" -eq 0 ]]; then
    printf 'read_only_preflight=pass\n'
else
    printf 'read_only_preflight=fail\n'
fi
printf 'independent_host_identity=not_verified_by_script\n'
exit "$missing"
