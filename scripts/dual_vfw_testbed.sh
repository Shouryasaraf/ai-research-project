#!/usr/bin/env bash
set -euo pipefail

NAMESPACES=(vfwlab2-client vfwlab2-director vfwlab2-fw-source vfwlab2-fw-target vfwlab2-server-source vfwlab2-server-target)
PID_FILES=(/tmp/vfwlab2-proxy.pid /tmp/vfwlab2-source.pid /tmp/vfwlab2-target.pid /tmp/vfwlab2-old-client.pid)
CONTROL_FILE="/tmp/vfwlab2-active-backend"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

namespace_exists() {
    ip netns list | awk '{print $1}' | grep -Fxq "$1"
}

commit_target_if_valid() {
    python3 "$SCRIPT_DIR/guarded_selection.py" \
        --control-file "$CONTROL_FILE" --target-pid-file /tmp/vfwlab2-target.pid
}

start_old_flow() {
    ip netns exec vfwlab2-client \
        python3 "$SCRIPT_DIR/flow_client.py" 10.20.0.1 --delay 2 before after \
        >/tmp/vfwlab2-old.out 2>&1 &
    echo "$!" >/tmp/vfwlab2-old-client.pid
    sleep 1
}

stop_processes() {
    local pid_file pid
    for pid_file in "${PID_FILES[@]}"; do
        if [[ -f "$pid_file" ]]; then
            pid="$(cat "$pid_file")"
            if [[ "$pid" =~ ^[0-9]+$ ]]; then
                kill "$pid" 2>/dev/null || true
            fi
            rm -f -- "$pid_file"
        fi
    done
}

down() {
    stop_processes
    local namespace
    for namespace in "${NAMESPACES[@]}"; do
        if namespace_exists "$namespace"; then
            ip netns delete "$namespace"
        fi
    done
    local interface
    for interface in v2c v2d0 v2dc v2ds v2sfi v2sfo v2ss v2dt v2tfi v2tfo v2ts; do
        ip link delete "$interface" 2>/dev/null || true
    done
    rm -f -- "$CONTROL_FILE" /tmp/vfwlab2-proxy-metrics.json /tmp/vfwlab2-old.out /tmp/vfwlab2-new.out
    echo "dual_testbed_down=true"
}

move_pair() {
    local left="$1" left_ns="$2" left_name="$3" right="$4" right_ns="$5" right_name="$6"
    ip link add "$left" type veth peer name "$right"
    ip link set "$left" netns "$left_ns"
    ip link set "$right" netns "$right_ns"
    ip -n "$left_ns" link set "$left" name "$left_name"
    ip -n "$right_ns" link set "$right" name "$right_name"
}

up() {
    down >/dev/null
    local namespace
    for namespace in "${NAMESPACES[@]}"; do
        ip netns add "$namespace"
        ip -n "$namespace" link set lo up
    done

    move_pair v2c vfwlab2-client client0 v2dc vfwlab2-director client0
    move_pair v2ds vfwlab2-director source0 v2sfi vfwlab2-fw-source input0
    move_pair v2sfo vfwlab2-fw-source output0 v2ss vfwlab2-server-source server0
    move_pair v2dt vfwlab2-director target0 v2tfi vfwlab2-fw-target input0
    move_pair v2tfo vfwlab2-fw-target output0 v2ts vfwlab2-server-target server0

    ip -n vfwlab2-client addr add 10.20.0.2/24 dev client0
    ip -n vfwlab2-director addr add 10.20.0.1/24 dev client0
    ip -n vfwlab2-director addr add 10.21.0.1/24 dev source0
    ip -n vfwlab2-fw-source addr add 10.21.0.2/24 dev input0
    ip -n vfwlab2-fw-source addr add 10.31.0.1/24 dev output0
    ip -n vfwlab2-server-source addr add 10.31.0.2/24 dev server0
    ip -n vfwlab2-director addr add 10.22.0.1/24 dev target0
    ip -n vfwlab2-fw-target addr add 10.22.0.2/24 dev input0
    ip -n vfwlab2-fw-target addr add 10.32.0.1/24 dev output0
    ip -n vfwlab2-server-target addr add 10.32.0.2/24 dev server0

    ip -n vfwlab2-client link set client0 up
    ip -n vfwlab2-director link set client0 up
    ip -n vfwlab2-director link set source0 up
    ip -n vfwlab2-director link set target0 up
    ip -n vfwlab2-fw-source link set input0 up
    ip -n vfwlab2-fw-source link set output0 up
    ip -n vfwlab2-server-source link set server0 up
    ip -n vfwlab2-fw-target link set input0 up
    ip -n vfwlab2-fw-target link set output0 up
    ip -n vfwlab2-server-target link set server0 up

    ip -n vfwlab2-client route add default via 10.20.0.1
    ip -n vfwlab2-director route add 10.31.0.0/24 via 10.21.0.2
    ip -n vfwlab2-director route add 10.32.0.0/24 via 10.22.0.2
    ip -n vfwlab2-server-source route add default via 10.31.0.1
    ip -n vfwlab2-server-target route add default via 10.32.0.1

    for namespace in vfwlab2-fw-source vfwlab2-fw-target; do
        ip netns exec "$namespace" sysctl -q -w net.ipv4.ip_forward=1
        ip netns exec "$namespace" nft -f "$SCRIPT_DIR/dual_firewall.nft"
    done

    printf 'source\n' >"$CONTROL_FILE"
    ip netns exec vfwlab2-server-source \
        python3 "$SCRIPT_DIR/flow_service.py" backend --listen 10.31.0.2 --id source \
        >/tmp/vfwlab2-source.log 2>&1 &
    echo "$!" >/tmp/vfwlab2-source.pid
    ip netns exec vfwlab2-server-target \
        python3 "$SCRIPT_DIR/flow_service.py" backend --listen 10.32.0.2 --id target \
        >/tmp/vfwlab2-target.log 2>&1 &
    echo "$!" >/tmp/vfwlab2-target.pid
    ip netns exec vfwlab2-director \
        python3 "$SCRIPT_DIR/flow_service.py" proxy --listen 10.20.0.1 \
        --control-file "$CONTROL_FILE" --source-backend 10.31.0.2 --target-backend 10.32.0.2 \
        --metrics-file /tmp/vfwlab2-proxy-metrics.json \
        >/tmp/vfwlab2-proxy.log 2>&1 &
    echo "$!" >/tmp/vfwlab2-proxy.pid
    sleep 0.5
    local pid_file pid
    for pid_file in /tmp/vfwlab2-source.pid /tmp/vfwlab2-target.pid /tmp/vfwlab2-proxy.pid; do
        pid="$(cat "$pid_file")"
        if ! kill -0 "$pid" 2>/dev/null; then
            echo "error: service failed to start; inspect ${pid_file%.pid}.log" >&2
            exit 5
        fi
    done
    echo "dual_testbed_up=true"
}

test_pinning() {
    local commit_start_ns new_flow_end_ns drain_end_ns new_flow_admission_ms source_drain_ms
    start_old_flow
    commit_start_ns="$(date +%s%N)"
    commit_target_if_valid
    ip netns exec vfwlab2-client \
        python3 "$SCRIPT_DIR/flow_client.py" 10.20.0.1 new >/tmp/vfwlab2-new.out 2>&1
    new_flow_end_ns="$(date +%s%N)"
    wait "$(cat /tmp/vfwlab2-old-client.pid)"
    drain_end_ns="$(date +%s%N)"
    new_flow_admission_ms="$(( (new_flow_end_ns - commit_start_ns) / 1000000 ))"
    source_drain_ms="$(( (drain_end_ns - commit_start_ns) / 1000000 ))"

    OLD_OUTPUT="$(cat /tmp/vfwlab2-old.out)"
    NEW_OUTPUT="$(cat /tmp/vfwlab2-new.out)"
    if [[ "$OLD_OUTPUT" != $'source:before\nsource:after' ]]; then
        echo "error: established flow did not remain pinned to source" >&2
        echo "$OLD_OUTPUT" >&2
        exit 3
    fi
    if [[ "$NEW_OUTPUT" != "target:new" ]]; then
        echo "error: new flow did not use prewarmed target" >&2
        echo "$NEW_OUTPUT" >&2
        exit 4
    fi

    echo "established_flow=$OLD_OUTPUT"
    echo "new_flow=$NEW_OUTPUT"
    echo "new_flow_admission_ms=$new_flow_admission_ms"
    echo "source_application_flow_drain_ms=$source_drain_ms"
    echo "source_application_flow_drained=true"
    echo "proxy_flow_pinning_verified=true"
    echo "transparent_sdn_steering_verified=false"
    echo "--- live source network telemetry ---"
    python3 "$SCRIPT_DIR/collect_network_telemetry.py" vfwlab2-fw-source
    echo "--- live target network telemetry ---"
    python3 "$SCRIPT_DIR/collect_network_telemetry.py" vfwlab2-fw-target
    echo "--- source firewall counters ---"
    ip netns exec vfwlab2-fw-source nft list chain inet vfw forward
    echo "--- target firewall counters ---"
    ip netns exec vfwlab2-fw-target nft list chain inet vfw forward
}

test_fallback() {
    printf 'target\n' >"$CONTROL_FILE"
    local target_pid start_ns end_ns recovery_ms
    target_pid="$(cat /tmp/vfwlab2-target.pid)"
    start_ns="$(date +%s%N)"
    kill "$target_pid"
    wait "$target_pid" 2>/dev/null || true

    if ! kill -0 "$target_pid" 2>/dev/null; then
        echo "target_failure_detected_by_test=true"
    else
        echo "error: injected target failure was not detected" >&2
        exit 6
    fi

    ip netns exec vfwlab2-client \
        python3 "$SCRIPT_DIR/flow_client.py" 10.20.0.1 fallback \
        >/tmp/vfwlab2-fallback.out 2>&1
    FALLBACK_OUTPUT="$(cat /tmp/vfwlab2-fallback.out)"
    if [[ "$FALLBACK_OUTPUT" != "source:fallback" ]]; then
        echo "error: new flow was not restored to validated source path" >&2
        echo "$FALLBACK_OUTPUT" >&2
        exit 7
    fi
    if [[ "$(cat "$CONTROL_FILE")" != "source" ]]; then
        echo "error: proxy did not restore source selection automatically" >&2
        exit 8
    fi
    end_ns="$(date +%s%N)"
    recovery_ms="$(( (end_ns - start_ns) / 1000000 ))"
    echo "injected_failure=target_backend_stopped"
    echo "fallback_flow=$FALLBACK_OUTPUT"
    echo "fallback_recovery_ms=$recovery_ms"
    echo "new_flow_route_fallback_verified=true"
    echo "automatic_proxy_fallback_verified=true"
    echo "established_target_flow_recovery_verified=false"
}

run_all() {
    trap 'down >/dev/null' EXIT
    up
    test_pinning
    test_fallback
    echo "dual_vfw_integration_passed=true"
}

run_policy_mismatch_test() {
    trap 'down >/dev/null' EXIT
    up
    start_old_flow
    ip netns exec vfwlab2-fw-target \
        nft insert rule inet vfw forward tcp dport 9999 accept comment \
        '"controlled policy mismatch"'
    if commit_target_if_valid; then
        echo "error: mismatched target policy was accepted" >&2
        exit 10
    fi
    if [[ "$(cat "$CONTROL_FILE")" != "source" ]]; then
        echo "error: active backend changed despite failed validation" >&2
        exit 11
    fi
    echo "injected_failure=target_policy_mismatch"
    echo "unsafe_commit_rejected=true"
    echo "validated_source_retained=true"
}

run_state_mismatch_test() {
    trap 'down >/dev/null' EXIT
    up
    start_old_flow
    ip netns exec vfwlab2-fw-source conntrack -F >/dev/null
    if commit_target_if_valid; then
        echo "error: missing source flow state was accepted" >&2
        exit 12
    fi
    if [[ "$(cat "$CONTROL_FILE")" != "source" ]]; then
        echo "error: active backend changed despite missing source flow state" >&2
        exit 13
    fi
    echo "injected_failure=source_conntrack_state_missing"
    echo "unsafe_commit_rejected=true"
    echo "validated_source_retained=true"
}

run_target_unhealthy_test() {
    trap 'down >/dev/null' EXIT
    up
    start_old_flow
    kill "$(cat /tmp/vfwlab2-target.pid)"
    sleep 0.1
    if commit_target_if_valid; then
        echo "error: unhealthy target was accepted" >&2
        exit 14
    fi
    if [[ "$(cat "$CONTROL_FILE")" != "source" ]]; then
        echo "error: active backend changed despite unhealthy target" >&2
        exit 15
    fi
    echo "injected_failure=target_backend_stopped_before_commit"
    echo "unsafe_commit_rejected=true"
    echo "validated_source_retained=true"
}

run_unsafe_source_fallback_test() {
    trap 'down >/dev/null' EXIT
    up
    start_old_flow
    commit_target_if_valid >/dev/null
    kill "$(cat /tmp/vfwlab2-target.pid)"
    ip netns exec vfwlab2-fw-source nft flush ruleset
    if ip netns exec vfwlab2-client \
        python3 "$SCRIPT_DIR/flow_client.py" 10.20.0.1 unsafe \
        >/tmp/vfwlab2-unsafe.out 2>&1; then
        echo "error: unsafe source policy was used for fallback" >&2
        exit 16
    fi
    if [[ "$(cat "$CONTROL_FILE")" != "target" ]]; then
        echo "error: selector changed to unvalidated source" >&2
        exit 17
    fi
    echo "injected_failure=target_stopped_and_source_policy_removed"
    echo "unsafe_source_fallback_rejected=true"
    echo "new_flow_failed_closed=true"
}

run_scaling_test() {
    trap 'down >/dev/null' EXIT
    up
    python3 "$SCRIPT_DIR/live_scaling_smoke.py"
    echo "live_scaling_smoke_passed=true"
}

if [[ "$(id -u)" -ne 0 ]]; then
    echo "error: run as root inside the isolated WSL test environment" >&2
    exit 2
fi

case "${1:-}" in
    up) up ;;
    test) test_pinning ;;
    test-policy-mismatch) run_policy_mismatch_test ;;
    test-state-mismatch) run_state_mismatch_test ;;
    test-target-unhealthy) run_target_unhealthy_test ;;
    test-unsafe-source-fallback) run_unsafe_source_fallback_test ;;
    test-scaling) run_scaling_test ;;
    down) down ;;
    run) run_all ;;
    *) echo "usage: $0 {run|up|test|test-policy-mismatch|test-state-mismatch|test-target-unhealthy|test-unsafe-source-fallback|test-scaling|down}" >&2; exit 64 ;;
esac
