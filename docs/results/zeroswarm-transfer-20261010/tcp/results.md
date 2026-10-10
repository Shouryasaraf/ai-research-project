# Validated TCP wire-visible diagnostic

RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss

| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |
|---|---:|---:|---:|
| full_proposed_controller / 107 | 0/0 | 6/7 | 0/0 |
| reactive_threshold / 107 | 0/0 | 6/9 | 0/0 |
| full_proposed_controller / 109 | 0/0 | 11/10 | 0/0 |
| reactive_threshold / 109 | 0/0 | 6/10 | 0/0 |
| full_proposed_controller / 113 | 0/0 | 7/12 | 0/0 |
| reactive_threshold / 113 | 0/0 | 7/11 | 0/0 |
| full_proposed_controller / 127 | 0/0 | 15/14 | 0/0 |
| reactive_threshold / 127 | 0/0 | 6/9 | 0/0 |
| full_proposed_controller / 131 | 0/0 | 9/13 | 0/0 |
| reactive_threshold / 131 | 0/0 | 4/9 | 0/0 |

Only packets generated in the isolated lab are examined. Source archives, record hashes, endpoint PCAP hashes and packet-instance matching are checked before this summary. A repeated payload sequence is an indicator, not a transport diagnosis. No kernel TCP sequence/window equivalence is claimed.
