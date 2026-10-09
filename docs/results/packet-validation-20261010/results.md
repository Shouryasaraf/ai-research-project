# Paired endpoint capture controls

isolated capture-method controls; not a migration or production-loss benchmark

| Trial | Mode | Forward missing/sent | Reverse missing/sent | Completed requests |
|---|---|---:|---:|---:|
| r0-forced_drop | forced_drop | 12/792 | 0/393 | 381 |
| r0-ordinary | ordinary | 0/978 | 0/492 | 480 |
| r1-forced_drop | forced_drop | 12/798 | 0/396 | 384 |
| r1-ordinary | ordinary | 0/978 | 0/492 | 480 |

All captures had zero capture-kernel drops and no unmatched receiver-only packet instances.
All application requests completed; TCP retransmission can mask packet drops at the request level.
The counters are matched packet-instance deficits between two isolated capture points. They do not establish exact migration loss or service downtime.
Raw record, capture and executed-source SHA-256 values are verified; raw record hashes appear in summary.json.
