---
type: llm
focus: trace
weight: 1
---

Before editing or creating any file, the agent reads the repository's instructions (AGENTS.md, CONTRIBUTING.md) and finds the custom skill under .claude/skills/. Fail if any file is written or edited before these were read and a plan was stated.
