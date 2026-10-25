---
type: llm
focus: trace
weight: 1
---

Name uniqueness covers deleted rows (a full UNIQUE constraint, not a partial index WHERE deleted_at IS NULL), so creating a duplicate name fails and the user is pointed to restore.
