---
type: llm
focus: trace
weight: 1
---

review.md flags the plain CREATE INDEX on a live 80-million-row table and proposes CREATE INDEX CONCURRENTLY outside a transaction, checking the index is valid.
