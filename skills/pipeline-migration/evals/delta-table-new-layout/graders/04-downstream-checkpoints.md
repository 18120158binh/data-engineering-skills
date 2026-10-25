---
type: llm
focus: trace
weight: 1
---

plan.md gives each downstream Iceberg streaming job a new checkpoint on the new table, with a start position that neither skips nor repeats records around the switch.
