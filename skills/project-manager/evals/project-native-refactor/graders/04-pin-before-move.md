---
type: llm
focus: trace
weight: 1
---

Before editing load.py or report.py, the agent adds or runs a test that pins the current load-and-report behavior, and it passes. Fail if code moves before any pinning test exists.
