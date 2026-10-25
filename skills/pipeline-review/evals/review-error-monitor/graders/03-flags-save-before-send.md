---
type: llm
focus: trace
weight: 1
---

review.md flags that the checkpoint is saved before the message is sent, so a failed send loses those errors, and proposes sending first and saving after.
