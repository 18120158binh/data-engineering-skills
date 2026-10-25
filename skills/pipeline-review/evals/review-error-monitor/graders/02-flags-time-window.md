---
type: llm
focus: trace
weight: 1
---

review.md flags reading errors by a time window since the last run instead of by an increasing id, because a late or skipped run misses errors.
