---
type: llm
focus: trace
weight: 1
---

lesson.md separates the immediate recovery (recreate the slot and re-snapshot the tables) from the root fix (the slot alert and the batched, throttled backfill), and marks raising the cap with a disk resize as still open, with its owner.
