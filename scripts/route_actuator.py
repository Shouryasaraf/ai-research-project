"""Bounded route mutation/readback for the isolated vfwlab3 topology only."""
import json
import subprocess

NETWORKS = {"ingress": "10.50.5.0/24", "egress": "10.50.0.0/24"}
HOPS = {"source": {"ingress": "10.50.1.2", "egress": "10.50.3.1"},
        "target": {"ingress": "10.50.2.2", "egress": "10.50.4.1"}}

def apply_route(side: str, destination: str) -> None:
    network = NETWORKS[side]
    args = ["ip", "-n", "vfwlab3-" + side, "route", "replace"]
    args.extend(["blackhole", network] if destination == "blocked"
                else [network, "via", HOPS[destination][side]])
    subprocess.run(args, check=True, capture_output=True, text=True, timeout=5)

def verify_route(side: str, destination: str) -> bool:
    output = subprocess.run(["ip", "-n", "vfwlab3-" + side, "-j", "route", "show", NETWORKS[side]],
                            check=True, capture_output=True, text=True, timeout=5).stdout
    routes = json.loads(output)
    if len(routes) != 1:
        return False
    if destination == "blocked":
        return routes[0].get("type") == "blackhole"
    return routes[0].get("gateway") == HOPS[destination][side] and routes[0].get("type", "unicast") == "unicast"
