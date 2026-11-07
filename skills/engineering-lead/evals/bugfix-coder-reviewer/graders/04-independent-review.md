---
type: llm
focus: trace
weight: 1
---

A second, separate subagent reviews the change. Its brief names the commit (or diff) to review and tells it not to edit implementation files, and its verdict is approved, changes requested, or blocked. If it requests changes, the findings go back to a coder and the new commit is reviewed again.
