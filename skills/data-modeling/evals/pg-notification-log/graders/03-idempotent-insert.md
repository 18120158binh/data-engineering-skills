---
type: llm
focus: trace
weight: 1
---

The write path is idempotent on that key (INSERT ... ON CONFLICT DO NOTHING or equivalent), so a Flink replay does not add a second row.
