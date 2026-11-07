---
type: llm
focus: trace
weight: 1
---

The main session starts a coder subagent (an Agent call) whose brief includes the goal, the acceptance criteria, the files in scope, the test command from AGENTS.md, and a boundary that allows at most a local commit and forbids push, PR, and merge.
