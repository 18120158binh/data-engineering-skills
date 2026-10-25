# Decision record

One record for each decision, in the repository's decision folder, numbered in order (`NNNN-short-statement.md`).

## Rules

- **Status** is `proposed`, `accepted`, `superseded`, or `rejected`. A new record starts as `proposed`. Only the owner accepts one.
- **Never edit an accepted record to reverse it.** Write a new record that supersedes it, and set `superseded_by` on the old one. Say whether it supersedes in full or in part, and list what still holds from the old record.
- **Credit only what the owner decided.** Write "The owner decided this on <date>" next to the exact rule the owner stated. A choice made while writing the record says "pending owner review".
- **Name the commit** that carried the decision out, once it exists.
- **Say how each fact is known**: measured, with the run; read from code or docs, with the version; or inferred, not run. When the reasoning has a gap, such as a reason nobody recorded, say so.
- **Research does not get its own page.** Its findings, with links, go into the Why of the decision they justify.
- **An undecided record is allowed.** When a choice must be made on purpose before a deadline, list the options and the open questions, with status `proposed`.

## Template

```markdown
---
title: <Short statement of the decision>
id: NNNN
status: proposed
date: YYYY-MM-DD
tags: []
supersedes: []
superseded_by: []
---

# NNNN. <Short statement of the decision>

## Context

The situation that forced a choice: the constraint, the incident, or the number. Name the design that existed before.

## Decision

What was chosen, in one or two paragraphs.

## Why

The incidents, measurements, and failure analyses, in enough detail that a reader can check the reasoning. How established products solve the same problem, with links, and the shape most of them share.

## Alternatives considered

| Alternative | Why it lost |
|---|---|
| <option> | <one concrete reason. "Tried, and it did not remove X" when it was tried.> |

## Consequences

- What the decision makes easier, and what it makes harder.
- The rules that code must now follow.
- The guarantees the pipeline must hold, for pipeline-review to check.
- The condition that reopens this decision, such as "if the late-drop alert fires in production".

## Open questions

Questions only the owner can answer, each with the options and a recommendation. Remove this section once the owner answers.

## Related

Other records, contracts, and issues.
```
