---
type: llm
focus: trace
weight: 1
---

review.md flags the bigserial id on reward_events, written by a replaying job, as causing duplicate rows, and proposes a natural or derived key with an idempotent insert.
