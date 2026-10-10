"""Bounded classic-pcap Ethernet/IPv4/TCP endpoint comparison, no payload export."""
from collections import Counter
import hashlib
from pathlib import Path
import socket
import struct
from .mawi_trace import MAGIC


def packets(path: Path) -> list[dict]:
    result = []
    with path.open("rb") as stream:
        header = stream.read(24)
        if len(header) != 24 or header[:4] not in MAGIC:
            raise ValueError("complete classic pcap required")
        endian, precision = MAGIC[header[:4]]
        major, minor, _, _, snaplen, link = struct.unpack(endian + "HHIIII", header[4:])
        if (major, minor) != (2, 4) or link != 1 or snaplen < 64:
            raise ValueError("Ethernet pcap version 2.4 required")
        while chunk := stream.read(16):
            if len(chunk) != 16:
                raise ValueError("truncated packet header")
            sec, fraction, size, original = struct.unpack(endian + "IIII", chunk)
            if size > snaplen or size != original or size > 1_000_000 or fraction >= precision:
                raise ValueError("truncated or invalid captured packet")
            frame = stream.read(size)
            if len(frame) != size or size < 14:
                raise ValueError("incomplete Ethernet frame")
            if frame[12:14] != b"\x08\x00":
                continue
            ip = frame[14:]
            if len(ip) < 20 or ip[0] >> 4 != 4:
                raise ValueError("invalid IPv4 header")
            ihl = (ip[0] & 15) * 4
            total, identifier, fragment = struct.unpack("!HHH", ip[2:8])
            if ihl < 20 or total > len(ip) or total < ihl:
                raise ValueError("incomplete IPv4 packet")
            if fragment & 0x3fff:
                raise ValueError("fragmented traffic is unsupported")
            if ip[9] != 6:
                continue
            tcp = ip[ihl:total]
            if len(tcp) < 20:
                raise ValueError("incomplete TCP header")
            sport, dport, seq, ack = struct.unpack("!HHII", tcp[:12])
            offset = (tcp[12] >> 4) * 4
            if offset < 20 or offset > len(tcp):
                raise ValueError("invalid TCP data offset")
            src, dst = socket.inet_ntoa(ip[12:16]), socket.inet_ntoa(ip[16:20])
            if {src, dst} != {"10.50.0.2", "10.50.5.2"} or 9000 not in (sport, dport):
                continue
            payload = tcp[offset:]
            digest = hashlib.sha256(payload).hexdigest()
            key = (src, dst, identifier, sport, dport, seq, ack, tcp[13], len(payload), digest)
            result.append({"timestamp": sec + fraction / precision, "source": src,
                           "sport": sport, "dport": dport, "seq": seq, "ack": ack,
                           "flags": tcp[13], "window": struct.unpack("!H", tcp[14:16])[0],
                           "key": key,
                           "payload_key": (src, dst, sport, dport, seq, len(payload), digest),
                           "payload_bytes": len(payload)})
    return result


def compare_endpoints(client: list[dict], server: list[dict], *, capture_drops: int) -> dict:
    if capture_drops < 0:
        raise ValueError("capture drop counts must be known")
    directions = []
    valid = capture_drops == 0 and bool(client) and bool(server)
    for name, source, sent, received in (("forward", "10.50.0.2", client, server),
                                         ("reverse", "10.50.5.2", server, client)):
        outgoing = [packet for packet in sent if packet["source"] == source]
        incoming = [packet for packet in received if packet["source"] == source]
        a, b = Counter(p["key"] for p in outgoing), Counter(p["key"] for p in incoming)
        missing, unmatched = sum((a-b).values()), sum((b-a).values())
        if unmatched or not outgoing:
            valid = False
        payloads = Counter(p["payload_key"] for p in outgoing if p["payload_bytes"])
        directions.append({"direction": name, "sent_packet_instances": len(outgoing),
                           "received_packet_instances": len(incoming), "unmatched_receiver_instances": unmatched,
                           "missing_receiver_instances": missing,
                           "repeated_payload_sequence_instances": sum(n-1 for n in payloads.values())})
    for row in directions:
        row["observed_packet_deficit_fraction"] = (row["missing_receiver_instances"] / row["sent_packet_instances"]
                                                     if valid else None)
    return {"comparison_valid": valid, "capture_kernel_drops": capture_drops, "directions": directions,
            "boundary": "matched packet instances between two lab captures; not exact application downtime"}
