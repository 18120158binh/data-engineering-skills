---
type: llm
focus: trace
weight: 1
---

retro.md groups the three fixes under one shared cause: the data window was computed from the wall clock or a UTC date instead of the run's scheduled time in the pipeline's timezone.
