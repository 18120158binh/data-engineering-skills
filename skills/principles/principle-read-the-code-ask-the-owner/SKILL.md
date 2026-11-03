---
name: principle-read-the-code-ask-the-owner
description: Apply when gathering facts before a change, a review, a design, or a migration. Learn what the system does from the code, its history, and its runs; ask the owner what it must do and what is true outside the code, such as whether it holds production data or who depends on it. Never fill one source with the other, and report where they disagree.
metadata:
  version: "0.1"
---

# Read the code, ask the owner

Two sources, two kinds of fact. The code tells you what the system does. The owner tells you what it must do, and what is true outside the repo. Use each for its own kind.

**Why:** the code shows behavior, bugs included, so requirements taken from the code turn bugs into rules. Asking the owner what the code already answers wastes their time and returns a memory instead of a fact.

| Read it from the code, history, and runs | Ask the owner |
|---|---|
| What it does now: inputs, outputs, configuration | What it must do: business rules, limits, failure handling |
| What it calls, and what calls it inside the repo | Who depends on it outside the repo |
| What changed, when, and in which commit | Whether it holds production data, users, or state that must survive |
| How it behaves when you run it | Which trade-offs are acceptable |

**How:**

- Read before you ask, so each question is one the code cannot answer.
- Record each answer with who gave it and when.
- When the code and the owner disagree, report the gap. Do not quietly pick one.

**The test:**

1. Does any requirement in the plan come only from the code?
2. Did you ask the owner anything the code could have told you?
3. Who answered each owner question, and when?

Related: `principle-label-the-evidence`, `principle-write-the-contract-first`.
