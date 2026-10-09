# Paired endpoint packet observation protocol

Development validation only. Capture generated lab traffic at client and server Ethernet interfaces before opening connections and until after sockets close. Compare only IPv4 TCP packets in the isolated client/server port-9000 flow set. Match packet instances by original IPv4 identifier, endpoints, TCP sequence/acknowledgment, flags and payload identity; ignore Ethernet addresses, TTL and IP checksum because routing changes those fields.

Capture readiness and a complete shutdown must be verified. Disable segmentation/receive offloads on the observed veth interfaces for this small-payload test, and retain the actual feature state. A truncated capture, capture-buffer drops, unsupported fragmentation or unmatched receiver-only packets makes the comparison invalid rather than proving loss. The observation is a bounded packet-instance deficit between two capture points, not a universal network loss rate.

Validation cases must include an ordinary warm transfer and intentional isolated dropping. Application errors and kernel queue counters remain separate metrics. Repeated TCP payload sequence ranges are an observed retransmission indicator, not a transport diagnosis by themselves.

Capture buffers can lose observations independently of network delivery. tcpdump reports capture-kernel drops on exit; see the [upstream manual](https://raw.githubusercontent.com/the-tcpdump-group/tcpdump/master/tcpdump.1.in). Preserve capture logs and checksums. Only locally generated synthetic lab payloads are captured; public trace packets, personal browsing and third-party traffic are out of scope.

Exact outage duration remains undefined without a specified service probe and sampling-resolution bound. Do not label a maximum inter-response gap as exact downtime.

Versioned capture correction: the first `active-recovery-capture-20261008-v1` trial had two receiver-only FIN/ACK instances despite zero kernel-drop counters and was rejected. Its raw capture/logs remain intact. Version 2 enables immediate capture delivery and allows two seconds after the workload closes for tail traffic before stopping capture. Packet-identity and zero-unmatched-receiver validity rules are unchanged.

2026-10-09 follow-up: the v2 batch produced five valid completed records and one setup failure (`OSError: [Errno 61] No data available`) before traffic. The v3 batch adds traceback diagnostics and reruns the same six-case protocol in a new directory. No earlier record is overwritten or excluded from the attempt history.
