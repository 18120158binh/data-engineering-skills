---
type: llm
focus: trace
weight: 1
---

review.md flags OFFSET pagination (each batch slower than the last) and proposes iterating by a unique indexed key, starting each batch at the last key.
