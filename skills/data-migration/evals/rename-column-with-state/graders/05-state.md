---
type: llm
focus: trace
weight: 1
---

plan.md handles the cached state explicitly: adding new state or migrating lazily rather than renaming state, or proving restore in both directions, with a savepoint at cutover.
