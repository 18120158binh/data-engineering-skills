---
type: llm
weight: 1
---

The agent says the mode is hybrid, or equivalent, because CONTRIBUTING.md defines gates for all changes (test before commit, stop after committing on a branch, code-owner review) but no process for planning a migration. It names which phases come from the project (those gates) and which from the default workflow (understanding and planning the migration), and treats the schema section as a constraint. Fail if it calls the mode default and ignores the project's gates, or treats the project as having a full migration workflow.
