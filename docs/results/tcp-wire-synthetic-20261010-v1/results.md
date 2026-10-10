# Validated TCP wire-visible diagnostic

RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss

| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |
|---|---:|---:|---:|
| full_proposed_controller / 47 | 0/0 | 11/19 | 0/0 |
| reactive_threshold / 47 | 0/0 | 10/19 | 0/0 |
| full_proposed_controller / 53 | 0/0 | 11/15 | 0/0 |
| reactive_threshold / 53 | 0/0 | 9/16 | 0/0 |
| full_proposed_controller / 59 | 0/0 | 8/16 | 0/0 |
| reactive_threshold / 59 | 0/0 | 8/16 | 0/0 |

Only packets generated in the isolated lab are examined. Source archives, record hashes, endpoint PCAP hashes and packet-instance matching are checked before this summary. A repeated payload sequence is an indicator, not a transport diagnosis. No kernel TCP sequence/window equivalence is claimed.
