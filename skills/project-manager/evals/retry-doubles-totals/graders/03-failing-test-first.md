---
type: llm
focus: trace
weight: 1
---

The agent adds a test that loads the same day twice and checks the total, runs it, and shows it failing before the fix is applied. The test is committed before the fix or in the same commit, never after it.
