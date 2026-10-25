---
type: llm
focus: trace
weight: 1
---

review.md flags dropping legacy_plan in the same release that removes its code, because old code still running during the rollout reads it, and moves the drop to a later release after the deploy.
