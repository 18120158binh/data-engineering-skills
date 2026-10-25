---
type: llm
focus: trace
weight: 1
---

review.md flags the Variable.get and the database query at the top level of the DAG file, because they run on every scheduler parse, and moves them into tasks.
