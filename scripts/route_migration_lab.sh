#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NS=(vfwlab3-client vfwlab3-ingress vfwlab3-source vfwlab3-target vfwlab3-egress vfwlab3-server)
PID_FILES=(/tmp/vfwlab3-server.pid /tmp/vfwlab3-client.pid)

exists() { ip netns list | awk '{print $1}' | grep -Fxq "$1"; }

down() {
    local file pid name
    for file in "${PID_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            pid="$(cat "$file")"
            if [[ "$pid" =~ ^[0-9]+$ ]]; then kill "$pid" 2>/dev/null || true; fi
            rm -f -- "$file"
        fi
    done
    for name in "${NS[@]}"; do
        if exists "$name"; then ip netns delete "$name"; fi
    done
    for name in v3c v3ic v3is v3si v3se v3es v3it v3ti v3te v3et v3eb v3b; do
        ip link delete "$name" 2>/dev/null || true
    done
    echo "route_lab_down=true"
}

pair() {
    local left="$1" left_ns="$2" left_name="$3" right="$4" right_ns="$5" right_name="$6"
    ip link add "$left" type veth peer name "$right"
    ip link set "$left" netns "$left_ns"
    ip link set "$right" netns "$right_ns"
    ip -n "$left_ns" link set "$left" name "$left_name"
    ip -n "$right_ns" link set "$right" name "$right_name"
}

up() {
    down >/dev/null
    local name
    for name in "${NS[@]}"; do
        ip netns add "$name"
        ip -n "$name" link set lo up
    done
    pair v3c vfwlab3-client eth0 v3ic vfwlab3-ingress client0
    pair v3is vfwlab3-ingress source0 v3si vfwlab3-source input0
    pair v3se vfwlab3-source output0 v3es vfwlab3-egress source0
    pair v3it vfwlab3-ingress target0 v3ti vfwlab3-target input0
    pair v3te vfwlab3-target output0 v3et vfwlab3-egress target0
    pair v3eb vfwlab3-egress server0 v3b vfwlab3-server eth0

    ip -n vfwlab3-client addr add 10.50.0.2/24 dev eth0
    ip -n vfwlab3-ingress addr add 10.50.0.1/24 dev client0
    ip -n vfwlab3-ingress addr add 10.50.1.1/30 dev source0
    ip -n vfwlab3-source addr add 10.50.1.2/30 dev input0
    ip -n vfwlab3-source addr add 10.50.3.1/30 dev output0
    ip -n vfwlab3-egress addr add 10.50.3.2/30 dev source0
    ip -n vfwlab3-ingress addr add 10.50.2.1/30 dev target0
    ip -n vfwlab3-target addr add 10.50.2.2/30 dev input0
    ip -n vfwlab3-target addr add 10.50.4.1/30 dev output0
    ip -n vfwlab3-egress addr add 10.50.4.2/30 dev target0
    ip -n vfwlab3-egress addr add 10.50.5.1/24 dev server0
    ip -n vfwlab3-server addr add 10.50.5.2/24 dev eth0
    for name in vfwlab3-client vfwlab3-server; do ip -n "$name" link set eth0 up; done
    for name in vfwlab3-ingress vfwlab3-source vfwlab3-target vfwlab3-egress; do
        ip netns exec "$name" sysctl -q -w net.ipv4.ip_forward=1
    done
    for name in client0 source0 target0; do ip -n vfwlab3-ingress link set "$name" up; done
    for name in source0 target0 server0; do ip -n vfwlab3-egress link set "$name" up; done
    for name in vfwlab3-source vfwlab3-target; do
        ip -n "$name" link set input0 up
        ip -n "$name" link set output0 up
        ip netns exec "$name" nft -f "$SCRIPT_DIR/route_migration_firewall.nft"
    done
    ip -n vfwlab3-client route add default via 10.50.0.1
    ip -n vfwlab3-server route add default via 10.50.5.1
    ip -n vfwlab3-ingress route add 10.50.5.0/24 via 10.50.1.2
    ip -n vfwlab3-egress route add 10.50.0.0/24 via 10.50.3.1
    ip -n vfwlab3-source route add 10.50.0.0/24 via 10.50.1.1
    ip -n vfwlab3-source route add 10.50.5.0/24 via 10.50.3.2
    ip -n vfwlab3-target route add 10.50.0.0/24 via 10.50.2.1
    ip -n vfwlab3-target route add 10.50.5.0/24 via 10.50.4.2
    ip netns exec vfwlab3-server \
        python3 "$SCRIPT_DIR/flow_service.py" backend --listen 10.50.5.2 --id server \
        >/tmp/vfwlab3-server.log 2>&1 &
    echo "$!" >/tmp/vfwlab3-server.pid
    local attempt
    for attempt in {1..30}; do
        if ip netns exec vfwlab3-server ss -H -ltn | grep -q '10.50.5.2:9000'; then
            break
        fi
        sleep 0.1
    done
    kill -0 "$(cat /tmp/vfwlab3-server.pid)"
    ip netns exec vfwlab3-server ss -H -ltn | grep -q '10.50.5.2:9000'
    echo "route_lab_up=true"
}

established_accept_packets() {
    local firewall="${1:-target}"
    ip netns exec "vfwlab3-$firewall" nft -j list chain inet vfw forward | python3 -c '
import json,sys
items=json.load(sys.stdin)["nftables"]
for item in items:
    rule=item.get("rule", {})
    if rule.get("comment") == "established state only":
        print(next(x["counter"]["packets"] for x in rule["expr"] if "counter" in x))
        break
else:
    raise SystemExit("missing established accept counter")'
}

test_route() {
    local mode="${1:-with-seen-reply}"
    if [[ "$mode" != "with-seen-reply" && "$mode" != "without-seen-reply" && \
          "$mode" != "policy-mismatch" && "$mode" != "rollback" ]]; then
        echo "error: invalid route test mode" >&2; exit 64
    fi
    trap 'down >/dev/null' EXIT
    up
    local messages=(before after)
    if [[ "$mode" == "rollback" ]]; then messages+=(again); fi
    ip netns exec vfwlab3-client \
        python3 "$SCRIPT_DIR/flow_client.py" 10.50.5.2 --delay 3 "${messages[@]}" \
        >/tmp/vfwlab3-client.out 2>/tmp/vfwlab3-client.err &
    echo "$!" >/tmp/vfwlab3-client.pid
    sleep 1
    local source_entry sport target_entry before after client_output status
    source_entry="$(ip netns exec vfwlab3-source conntrack -L -p tcp \
        --orig-src 10.50.0.2 --orig-dst 10.50.5.2 --orig-port-dst 9000 2>/dev/null)"
    if [[ "$source_entry" != *"ESTABLISHED"* ]] || [[ "$source_entry" != *"[ASSURED]"* ]]; then
        echo "error: source flow not established and assured" >&2; exit 3
    fi
    sport="$(printf '%s' "$source_entry" | python3 -c 'import re,sys; print(re.findall(r"\bsport=(\d+)",sys.stdin.read())[0])')"
    status="ASSURED,SEEN_REPLY"
    if [[ "$mode" == "without-seen-reply" ]]; then status="ASSURED"; fi
    ip netns exec vfwlab3-target conntrack -I -p tcp \
        --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
        --orig-port-src "$sport" --orig-port-dst 9000 \
        --reply-src 10.50.5.2 --reply-dst 10.50.0.2 \
        --reply-port-src 9000 --reply-port-dst "$sport" \
        --state ESTABLISHED --timeout 120 --status "$status" >/dev/null
    target_entry="$(ip netns exec vfwlab3-target conntrack -L -p tcp \
        --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
        --orig-port-src "$sport" --orig-port-dst 9000 2>/dev/null)"
    if [[ "$mode" == "policy-mismatch" ]]; then
        ip netns exec vfwlab3-target nft insert rule inet vfw forward tcp dport 9999 accept \
            comment '"controlled route-lab mismatch"'
        if python3 "$SCRIPT_DIR/route_policy_check.py"; then
            echo "error: mismatched target policy was accepted" >&2; exit 8
        fi
        ip -n vfwlab3-ingress route get 10.50.5.2 | grep -q 'via 10.50.1.2'
        ip -n vfwlab3-egress route get 10.50.0.2 | grep -q 'via 10.50.3.1'
        wait "$(cat /tmp/vfwlab3-client.pid)"
        client_output="$(cat /tmp/vfwlab3-client.out)"
        if [[ "$client_output" != $'server:before\nserver:after' ]]; then
            echo "error: source flow failed after refused policy mismatch" >&2; exit 9
        fi
        echo "route_policy_mismatch_rejected_before_commit=true"
        echo "validated_source_flow_retained=true"
        return
    fi
    python3 "$SCRIPT_DIR/route_policy_check.py"
    if [[ "$mode" == "without-seen-reply" ]]; then
        if python3 "$SCRIPT_DIR/validate_conntrack.py" --source "$source_entry" \
            --target "$target_entry" --require-seen-reply; then
            echo "error: UNREPLIED target entry was accepted for route commit" >&2; exit 6
        fi
        ip -n vfwlab3-ingress route get 10.50.5.2 | grep -q 'via 10.50.1.2'
        ip -n vfwlab3-egress route get 10.50.0.2 | grep -q 'via 10.50.3.1'
        wait "$(cat /tmp/vfwlab3-client.pid)"
        client_output="$(cat /tmp/vfwlab3-client.out)"
        if [[ "$client_output" != $'server:before\nserver:after' ]]; then
            echo "error: source flow failed after refused migration" >&2; exit 7
        fi
        echo "unreplied_target_state_rejected_before_route_commit=true"
        echo "validated_source_flow_retained=true"
        return
    fi
    python3 "$SCRIPT_DIR/validate_conntrack.py" --source "$source_entry" \
        --target "$target_entry" --require-seen-reply
    before="$(established_accept_packets)"
    ip -n vfwlab3-ingress route replace 10.50.5.0/24 via 10.50.2.2
    ip -n vfwlab3-egress route replace 10.50.0.0/24 via 10.50.4.1
    if [[ "$mode" == "rollback" ]]; then
        local attempt source_before source_after target_current source_refreshed
        for attempt in {1..50}; do
            if grep -Fxq 'server:after' /tmp/vfwlab3-client.out; then break; fi
            sleep 0.1
        done
        if ! grep -Fxq 'server:after' /tmp/vfwlab3-client.out; then
            echo "error: target response not received before rollback" >&2; exit 10
        fi
        target_current="$(ip netns exec vfwlab3-target conntrack -L -p tcp \
            --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
            --orig-port-src "$sport" --orig-port-dst 9000 2>/dev/null)"
        if [[ "$target_current" != *"[ASSURED]"* ]] || [[ "$target_current" == *"[UNREPLIED]"* ]]; then
            echo "error: target state not safe for reverse synchronization" >&2; exit 13
        fi
        ip netns exec vfwlab3-source conntrack -D -p tcp \
            --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
            --orig-port-src "$sport" --orig-port-dst 9000 >/dev/null
        ip netns exec vfwlab3-source conntrack -I -p tcp \
            --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
            --orig-port-src "$sport" --orig-port-dst 9000 \
            --reply-src 10.50.5.2 --reply-dst 10.50.0.2 \
            --reply-port-src 9000 --reply-port-dst "$sport" \
            --state ESTABLISHED --timeout 120 --status ASSURED,SEEN_REPLY >/dev/null
        source_refreshed="$(ip netns exec vfwlab3-source conntrack -L -p tcp \
            --orig-src 10.50.0.2 --orig-dst 10.50.5.2 \
            --orig-port-src "$sport" --orig-port-dst 9000 2>/dev/null)"
        python3 "$SCRIPT_DIR/validate_conntrack.py" --source "$target_current" \
            --target "$source_refreshed" --require-seen-reply
        source_before="$(established_accept_packets source)"
        ip netns exec vfwlab3-target nft flush chain inet vfw forward
        ip netns exec vfwlab3-source nft -j list table inet vfw | \
            PYTHONPATH="$SCRIPT_DIR" python3 -c 'import json,sys; from route_policy_check import route_policy_approved; assert route_policy_approved(json.load(sys.stdin))' \
            2>/dev/null || {
                echo "error: source policy not validated for rollback" >&2; exit 11;
            }
        ip -n vfwlab3-ingress route replace 10.50.5.0/24 via 10.50.1.2
        ip -n vfwlab3-egress route replace 10.50.0.0/24 via 10.50.3.1
        if ! wait "$(cat /tmp/vfwlab3-client.pid)"; then
            echo "error: same TCP client failed after reverse state sync and rollback" >&2
            sed 's/^/client_stdout: /' /tmp/vfwlab3-client.out >&2
            sed 's/^/client_stderr: /' /tmp/vfwlab3-client.err >&2
            ip netns exec vfwlab3-source nft list chain inet vfw forward >&2
            exit 14
        fi
        client_output="$(cat /tmp/vfwlab3-client.out)"
        source_after="$(established_accept_packets source)"
        echo "client_output=$client_output"
        echo "source_established_accept_packets_before_rollback=$source_before"
        echo "source_established_accept_packets_after_rollback=$source_after"
        if [[ "$client_output" != $'server:before\nserver:after\nserver:again' ]] || \
           (( source_after <= source_before )); then
            echo "error: same TCP flow did not survive route rollback" >&2; exit 12
        fi
        echo "target_policy_fault_injected=true"
        echo "same_tcp_connection_survived_route_rollback=true"
        return
    fi
    if ! wait "$(cat /tmp/vfwlab3-client.pid)"; then
        echo "error: client flow failed after route change" >&2
        sed 's/^/client_stdout: /' /tmp/vfwlab3-client.out >&2
        sed 's/^/client_stderr: /' /tmp/vfwlab3-client.err >&2
        echo "target_established_accept_packets_after=$(established_accept_packets)" >&2
        ip netns exec vfwlab3-target nft list chain inet vfw forward >&2
        ip netns exec vfwlab3-target conntrack -L -p tcp 2>&1 >&2 || true
        ip -n vfwlab3-ingress route get 10.50.5.2 >&2
        ip -n vfwlab3-egress route get 10.50.0.2 >&2
        exit 4
    fi
    client_output="$(cat /tmp/vfwlab3-client.out)"
    after="$(established_accept_packets)"
    echo "client_output=$client_output"
    echo "target_established_accept_packets_before=$before"
    echo "target_established_accept_packets_after=$after"
    if [[ "$client_output" != $'server:before\nserver:after' ]]; then
        echo "error: same TCP flow did not finish across route change" >&2; exit 4
    fi
    if (( after <= before )); then
        echo "error: target firewall did not accept established packets" >&2; exit 5
    fi
    echo "same_tcp_connection_survived_route_change=true"
    echo "target_firewall_traversal_verified=true"
    echo "full_tcp_sequence_window_equivalence_verified=false"
}

if [[ "$(id -u)" -ne 0 ]]; then echo "error: run as root" >&2; exit 2; fi
case "${1:-}" in
    run) test_route ;;
    test-no-seen-reply) test_route without-seen-reply ;;
    test-policy-mismatch) test_route policy-mismatch ;;
    test-rollback) test_route rollback ;;
    up) up ;;
    down) down ;;
    *) echo "usage: $0 {run|test-no-seen-reply|test-policy-mismatch|test-rollback|up|down}" >&2; exit 64 ;;
esac
