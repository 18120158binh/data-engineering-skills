---
type: llm
focus: trace
weight: 1
---

lesson.md gives the chain from cause to symptom (the connector was paused, so the slot stopped advancing, while the backfill wrote about 64 GB of WAL, more than the 20 GB cap, so Postgres invalidated the slot and the resumed connector failed), quotes the error exactly, and says why the existing check missed it: the only alert watched consumer lag, was muted, and nothing watched the slot's wal_status or safe_wal_size.
