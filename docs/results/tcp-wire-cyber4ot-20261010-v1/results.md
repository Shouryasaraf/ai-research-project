# Validated TCP wire-visible diagnostic

RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss

| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |
|---|---:|---:|---:|
| full_proposed_controller / 61 | 0/0 | 13/19 | 0/0 |
| reactive_threshold / 61 | 0/0 | 0/0 | 0/0 |
| full_proposed_controller / 67 | 0/0 | 15/19 | 0/0 |
| reactive_threshold / 67 | 0/0 | 5/9 | 0/0 |
| full_proposed_controller / 71 | 0/0 | 16/20 | 0/0 |
| reactive_threshold / 71 | 0/0 | 6/10 | 0/0 |
| full_proposed_controller / 73 | 0/0 | 13/17 | 0/0 |
| reactive_threshold / 73 | 0/0 | 6/9 | 0/0 |
| full_proposed_controller / 79 | 0/0 | 12/17 | 0/0 |
| reactive_threshold / 79 | 0/0 | 5/9 | 0/0 |

Only packets generated in the isolated lab are examined. Source archives, record hashes, endpoint PCAP hashes and packet-instance matching are checked before this summary. A repeated payload sequence is an indicator, not a transport diagnosis. No kernel TCP sequence/window equivalence is claimed.
