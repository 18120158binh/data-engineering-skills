---
type: llm
focus: trace
weight: 1
---

plan.md keeps the writer's checkpoint if the docs allow it, so the job continues from the same source position, and otherwise sets an explicit start position and deduplicates the overlap.
