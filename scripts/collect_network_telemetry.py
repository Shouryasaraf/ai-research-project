"""Collect a live, timestamped Linux namespace network snapshot as JSON."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone


ALLOWED_NAMESPACES = {"vfwlab2-fw-source", "vfwlab2-fw-target"}


def command(*args: str) -> str:
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def collect(namespace: str) -> dict[str, object]:
    if namespace not in ALLOWED_NAMESPACES:
        raise ValueError(f"unsupported testbed namespace: {namespace}")
    links = json.loads(command("ip", "-n", namespace, "-s", "-j", "link", "show"))
    interfaces = {}
    for link in links:
        if link.get("ifname") == "lo":
            continue
        stats = link.get("stats64") or link.get("stats")
        if not stats:
            raise ValueError("ip link output lacks interface counters")
        interfaces[link["ifname"]] = {
            direction: {
                field: int(stats[direction][field])
                for field in ("bytes", "packets", "dropped", "errors")
            }
            for direction in ("rx", "tx")
        }
    conntrack_count = int(command("ip", "netns", "exec", namespace, "conntrack", "-C").strip())
    policy = json.loads(command("ip", "netns", "exec", namespace, "nft", "-j", "list", "table", "inet", "vfw"))
    return {
        "schema_version": 1,
        "namespace": namespace,
        "observed_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "observed_monotonic_seconds": time.monotonic(),
        "source": "linux-ip-conntrack-nft",
        "interfaces": interfaces,
        "conntrack_entries": conntrack_count,
        "firewall_table_present": any("table" in item for item in policy["nftables"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("namespace", choices=sorted(ALLOWED_NAMESPACES))
    args = parser.parse_args()
    print(json.dumps(collect(args.namespace), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
