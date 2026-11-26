---
type: llm
focus: trace
weight: 1
---

lesson.md gives the chain from cause to symptom as steps: the connector was paused, so the slot stopped advancing; the backfill wrote about 64 GB of WAL, more than the 20 GB cap; Postgres invalidated the slot; the resumed connector failed.
