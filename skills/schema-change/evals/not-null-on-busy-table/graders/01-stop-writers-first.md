---
type: llm
focus: trace
weight: 1
---

plan.md first changes every code path that writes NULL, including the importer, before any constraint.
