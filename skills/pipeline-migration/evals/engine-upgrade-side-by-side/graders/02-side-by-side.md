---
type: llm
focus: trace
weight: 1
---

plan.md runs the old and new ClickHouse versions at the same time on the same input, each writing its own output, rather than upgrading in place and checking afterwards.
