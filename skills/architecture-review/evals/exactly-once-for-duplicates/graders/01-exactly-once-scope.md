---
type: llm
focus: trace
weight: 1
---

decision.md explains that Kafka exactly-once does not cover the Postgres sink (or outside consumers), so it would not remove the duplicates.
