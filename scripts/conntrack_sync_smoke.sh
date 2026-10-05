#!/usr/bin/env bash
set -euo pipefail

TARGET_NS="vfwlab-target"
CLIENT_PID=""
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
    if [[ "$CLIENT_PID" =~ ^[0-9]+$ ]]; then
        kill "$CLIENT_PID" 2>/dev/null || true
    fi
    ip netns delete "$TARGET_NS" 2>/dev/null || true
    bash "$SCRIPT_DIR/testbed.sh" down >/dev/null 2>&1 || true
}
trap cleanup EXIT

if [[ "$(id -u)" -ne 0 ]]; then
    echo "error: run as root in the isolated WSL test environment" >&2
    exit 2
fi

bash "$SCRIPT_DIR/testbed.sh" up >/dev/null
ip netns delete "$TARGET_NS" 2>/dev/null || true
ip netns add "$TARGET_NS"
ip -n "$TARGET_NS" link set lo up

ip netns exec vfwlab-server iperf3 -s -D --pidfile /tmp/vfwlab-iperf3.pid
ip netns exec vfwlab-client \
    iperf3 -c 10.10.2.2 -t 8 --cport 40000 >/tmp/vfwlab-live-client.log 2>&1 &
CLIENT_PID="$!"
sleep 1

SOURCE_ENTRY="$(
    ip netns exec vfwlab-source conntrack -L -p tcp \
        --orig-src 10.10.1.2 --orig-dst 10.10.2.2 \
        --orig-port-src 40000 --orig-port-dst 5201 2>/dev/null
)"
if [[ "$SOURCE_ENTRY" != *"ESTABLISHED"* ]] || [[ "$SOURCE_ENTRY" != *"[ASSURED]"* ]]; then
    echo "error: source flow was not observed as ESTABLISHED and ASSURED" >&2
    exit 3
fi

ip netns exec "$TARGET_NS" conntrack -I -p tcp \
    --orig-src 10.10.1.2 --orig-dst 10.10.2.2 \
    --orig-port-src 40000 --orig-port-dst 5201 \
    --reply-src 10.10.2.2 --reply-dst 10.10.1.2 \
    --reply-port-src 5201 --reply-port-dst 40000 \
    --state ESTABLISHED --timeout 120 --status ASSURED >/dev/null

TARGET_ENTRY="$(
    ip netns exec "$TARGET_NS" conntrack -L -p tcp \
        --orig-src 10.10.1.2 --orig-dst 10.10.2.2 \
        --orig-port-src 40000 --orig-port-dst 5201 2>/dev/null
)"
if [[ "$TARGET_ENTRY" != *"ESTABLISHED"* ]]; then
    echo "error: target conntrack entry was not created" >&2
    exit 4
fi

echo "source_entry=$SOURCE_ENTRY"
echo "target_entry=$TARGET_ENTRY"
echo "kernel_conntrack_tuple_inserted=true"
echo "seamless_flow_continuity_verified=false"
