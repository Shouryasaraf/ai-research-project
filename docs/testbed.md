# Stage 2 Linux Namespace Testbed

## Purpose

The first executable packet-path testbed uses Linux network namespaces rather than containers. It provides a small, inspectable topology with real kernel packet forwarding, nftables filtering, connection tracking, deterministic addresses, and explicit cleanup.

```text
vfwlab-client                 vfwlab-source                    vfwlab-server
10.10.1.2/24  <---------->  10.10.1.1 | 10.10.2.1  <------>  10.10.2.2/24
                              nftables forward hook
                              default policy: drop
```

Allowed traffic:

- ICMP echo request from the client subnet to the server subnet;
- new TCP connections from the client subnet to server port 5201;
- established and related return traffic.

Other forwarded traffic is dropped. TCP port 8080 is deliberately used to verify default-deny behavior.

## Prerequisites inside Ubuntu/WSL2

```bash
sudo apt-get update
sudo apt-get install -y iproute2 nftables conntrack iperf3 tcpdump
```

## Commands

From the repository directory mounted inside WSL:

```bash
sudo bash scripts/testbed.sh up
sudo bash scripts/testbed.sh test
sudo bash scripts/testbed.sh status
sudo bash scripts/testbed.sh down
```

The `down` command deletes only these exact namespaces:

- `vfwlab-client`
- `vfwlab-source`
- `vfwlab-server`

It also stops only processes referenced by `/tmp/vfwlab-iperf3.pid` and `/tmp/vfwlab-http.pid`.

## Evidence boundary

A passing run verifies an enforced stateful software-firewall path, allowed and denied traffic, nftables counters, and observable conntrack state. It does **not** verify multi-vFW placement, scaling, state transfer, flow pinning, or warm migration.

