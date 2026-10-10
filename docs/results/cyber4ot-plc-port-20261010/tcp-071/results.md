# Validated TCP wire-visible diagnostic

RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss

| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |
|---|---:|---:|---:|
| full_proposed_controller / 101 | 0/0 | 28/25 | 0/0 |
| reactive_threshold / 101 | 0/0 | 18/18 | 0/0 |
| full_proposed_controller / 103 | 0/0 | 26/26 | 0/0 |
| reactive_threshold / 103 | 0/0 | 12/18 | 0/0 |
| full_proposed_controller / 83 | 0/0 | 28/27 | 0/0 |
| reactive_threshold / 83 | 0/0 | 15/20 | 0/0 |
| full_proposed_controller / 89 | 0/0 | 29/27 | 0/0 |
| reactive_threshold / 89 | 0/0 | 15/19 | 0/0 |
| full_proposed_controller / 97 | 0/0 | 27/25 | 0/0 |
| reactive_threshold / 97 | 0/0 | 11/15 | 0/0 |

Only packets generated in the isolated lab are examined. Source archives, record hashes, endpoint PCAP hashes and packet-instance matching are checked before this summary. A repeated payload sequence is an indicator, not a transport diagnosis. No kernel TCP sequence/window equivalence is claimed.
