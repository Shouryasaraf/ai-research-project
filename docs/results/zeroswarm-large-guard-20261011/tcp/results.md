# Validated TCP wire-visible diagnostic

RST absence at endpoints and repeated payload sequences do not prove full TCP state equivalence or zero packet loss

| Policy / seed | Sender RST fwd/rev | Repeated payload-sequence fwd/rev | Zero-window fwd/rev |
|---|---:|---:|---:|
| full_liveness_guarded_experimental / 137 | 0/0 | 16/20 | 0/0 |
| full_proposed_controller / 137 | 0/0 | 13/19 | 0/0 |
| reactive_threshold / 137 | 0/0 | 13/19 | 0/0 |
| full_liveness_guarded_experimental / 139 | 0/0 | 15/21 | 0/0 |
| full_proposed_controller / 139 | 0/0 | 16/21 | 0/0 |
| reactive_threshold / 139 | 0/0 | 18/18 | 0/0 |
| full_liveness_guarded_experimental / 149 | 0/0 | 15/19 | 0/0 |
| full_proposed_controller / 149 | 0/0 | 14/17 | 0/0 |
| reactive_threshold / 149 | 0/0 | 16/19 | 0/0 |
| full_liveness_guarded_experimental / 151 | 0/0 | 14/22 | 0/0 |
| full_proposed_controller / 151 | 0/0 | 15/21 | 0/0 |
| reactive_threshold / 151 | 0/0 | 18/19 | 0/0 |
| full_liveness_guarded_experimental / 157 | 0/0 | 16/20 | 0/0 |
| full_proposed_controller / 157 | 0/0 | 15/21 | 0/0 |
| reactive_threshold / 157 | 0/0 | 15/21 | 0/0 |

Only packets generated in the isolated lab are examined. Source archives, record hashes, endpoint PCAP hashes and packet-instance matching are checked before this summary. A repeated payload sequence is an indicator, not a transport diagnosis. No kernel TCP sequence/window equivalence is claimed.
