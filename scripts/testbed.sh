#!/usr/bin/env bash
set -euo pipefail

CLIENT_NS="vfwlab-client"
FIREWALL_NS="vfwlab-source"
SERVER_NS="vfwlab-server"
IPERF_PID_FILE="/tmp/vfwlab-iperf3.pid"
HTTP_PID_FILE="/tmp/vfwlab-http.pid"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

require_root() {
    if [[ "$(id -u)" -ne 0 ]]; then
        echo "error: run as root inside the isolated WSL test environment" >&2
        exit 2
    fi
}

namespace_exists() {
    ip netns list | awk '{print $1}' | grep -Fxq "$1"
}

stop_pid_file() {
    local pid_file="$1"
    if [[ -f "$pid_file" ]]; then
        local pid
        pid="$(cat "$pid_file")"
        if [[ "$pid" =~ ^[0-9]+$ ]]; then
            kill "$pid" 2>/dev/null || true
        fi
        rm -f -- "$pid_file"
    fi
}

down() {
    stop_pid_file "$IPERF_PID_FILE"
    stop_pid_file "$HTTP_PID_FILE"
    for namespace in "$CLIENT_NS" "$FIREWALL_NS" "$SERVER_NS"; do
        if namespace_exists "$namespace"; then
            ip netns delete "$namespace"
        fi
    done
    echo "testbed_down=true"
}

up() {
    down >/dev/null

    ip netns add "$CLIENT_NS"
    ip netns add "$FIREWALL_NS"
    ip netns add "$SERVER_NS"

    ip link add vfwlab-c type veth peer name vfwlab-fi
    ip link add vfwlab-fo type veth peer name vfwlab-s

    ip link set vfwlab-c netns "$CLIENT_NS"
    ip link set vfwlab-fi netns "$FIREWALL_NS"
    ip link set vfwlab-fo netns "$FIREWALL_NS"
    ip link set vfwlab-s netns "$SERVER_NS"

    ip -n "$CLIENT_NS" link set lo up
    ip -n "$FIREWALL_NS" link set lo up
    ip -n "$SERVER_NS" link set lo up

    ip -n "$CLIENT_NS" addr add 10.10.1.2/24 dev vfwlab-c
    ip -n "$FIREWALL_NS" addr add 10.10.1.1/24 dev vfwlab-fi
    ip -n "$FIREWALL_NS" addr add 10.10.2.1/24 dev vfwlab-fo
    ip -n "$SERVER_NS" addr add 10.10.2.2/24 dev vfwlab-s

    ip -n "$CLIENT_NS" link set vfwlab-c up
    ip -n "$FIREWALL_NS" link set vfwlab-fi up
    ip -n "$FIREWALL_NS" link set vfwlab-fo up
    ip -n "$SERVER_NS" link set vfwlab-s up

    ip -n "$CLIENT_NS" route add default via 10.10.1.1
    ip -n "$SERVER_NS" route add default via 10.10.2.1

    ip netns exec "$FIREWALL_NS" sysctl -q -w net.ipv4.ip_forward=1
    ip netns exec "$FIREWALL_NS" nft -f "$SCRIPT_DIR/firewall.nft"

    echo "testbed_up=true"
    status
}

status() {
    for namespace in "$CLIENT_NS" "$FIREWALL_NS" "$SERVER_NS"; do
        if namespace_exists "$namespace"; then
            echo "namespace=$namespace status=present"
            ip -n "$namespace" -brief address
        else
            echo "namespace=$namespace status=absent"
        fi
    done
    if namespace_exists "$FIREWALL_NS"; then
        echo "--- firewall rules and counters ---"
        ip netns exec "$FIREWALL_NS" nft list table inet vfw
    fi
}

test_path() {
    for namespace in "$CLIENT_NS" "$FIREWALL_NS" "$SERVER_NS"; do
        if ! namespace_exists "$namespace"; then
            echo "error: missing namespace $namespace; run up first" >&2
            exit 3
        fi
    done

    stop_pid_file "$IPERF_PID_FILE"
    stop_pid_file "$HTTP_PID_FILE"

    ip netns exec "$SERVER_NS" sh -c \
        "iperf3 -s -D --pidfile '$IPERF_PID_FILE'"
    ip netns exec "$SERVER_NS" sh -c \
        "python3 -m http.server 8080 --bind 10.10.2.2 >/tmp/vfwlab-http.log 2>&1 & echo \$! >'$HTTP_PID_FILE'"

    echo "--- allowed ICMP ---"
    ip netns exec "$CLIENT_NS" ping -c 2 -W 2 10.10.2.2

    echo "--- allowed iperf TCP/5201 ---"
    ip netns exec "$CLIENT_NS" iperf3 -c 10.10.2.2 -t 2 -J

    echo "--- blocked TCP/8080 ---"
    if ip netns exec "$CLIENT_NS" python3 -c \
        'import socket; s=socket.create_connection(("10.10.2.2", 8080), timeout=1); s.close()'; then
        echo "error: default-deny test failed; TCP/8080 was reachable" >&2
        exit 4
    else
        echo "blocked_tcp_8080=true"
    fi

    echo "--- conntrack evidence ---"
    ip netns exec "$FIREWALL_NS" conntrack -L -p tcp 2>/dev/null || true

    echo "--- firewall rule counters ---"
    ip netns exec "$FIREWALL_NS" nft list chain inet vfw forward
    echo "stage2_smoke_passed=true"
}

usage() {
    echo "usage: $0 {up|test|status|down}" >&2
    exit 64
}

require_root
case "${1:-}" in
    up) up ;;
    test) test_path ;;
    status) status ;;
    down) down ;;
    *) usage ;;
esac

