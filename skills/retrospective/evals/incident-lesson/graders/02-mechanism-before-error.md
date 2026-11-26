---
type: llm
focus: trace
weight: 1
---

Before lesson.md quotes the error or describes the failure, it explains from the basics what a replication slot is, what it remembers (the position the consumer has confirmed, so Postgres keeps the WAL after it), and what max_slot_wal_keep_size does when a slot holds more WAL than the cap. A lesson that opens with the error or the timeline fails.
