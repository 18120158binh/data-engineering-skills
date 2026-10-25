---
name: architecture-review
description: Verify or choose a data architecture by framing the decision with numbers, grounding it in the current system and its history, laying out at least two structurally different options, having independent advocates and a challenger debate them, judging them against explicit criteria (correctness under replay, one owner per key, load on the hot path, operational burden, measured scale, testability, lock-in, cost, residency, upgrade safety, privacy), and writing a decision record that only the owner accepts. Use it when you design or change how data moves or is stored, review someone's design or RFC, choose between approaches, or revisit a decision after an incident, even if the user only says "should we use X", "is this design OK", "Kafka or CDC", or "how should this scale".
metadata:
  version: "0.1"
---

# Architecture review

A design is verified when its strongest rival lost on evidence a reader can check, its costs are written down, and its owner accepted it. This skill gets there by debate, not by first impressions.

## Where this fits

| You need | Skill |
|---|---|
| Facts about the tools that could fill a role | `tech-market-research`, before step 3 |
| The tables inside the design | `data-modeling` |
| A check that the built pipeline holds the design's guarantees | `pipeline-review`, after step 6 |

## Steps

Open a todo list with one entry per step.

### 1. Frame

Write down, before looking at options:

- **The decision**, in one sentence: what is being chosen, for which part of the system.
- **The questions the data must answer** and the users who ask them.
- **The numbers**: volume, peak rate, freshness or latency, retention, number of tenants, regions, and a cost ceiling. A number nobody can give is an open question, not a guess.
- **The constraints**: the stack already running, deployed versions, the team's skills, residency rules, and what must not change.
- **The owner**: the person who accepts the decision.

When the owner has not given an answer, stop and ask. Never take the answer from existing code, because the code may be the part that is wrong.

### 2. Ground

Read the current design and its history: earlier decision records, incidents, fix commits, and measured numbers. Note what was already tried and why it failed.

Label every fact as **measured** (with the run), **read from code or docs** (with the version), or **inferred, not run**. A design argued from inferred facts names the measurement that would settle it.

### 3. Lay out options

- At least two structurally different options: whole shapes, not variations of one shape.
- Always include the **baseline**: keep the current design and fix it in place.
- Include **defer with an alarm** when the problem has not been seen yet: build the alert that would show it happening, and revisit when it fires.
- When an option needs a tool for a role, get the candidates and their facts from `tech-market-research`.
- Note how established products solve the same problem, with links, and the shape most of them share. Following the common shape needs less argument. Departing from it needs more.

Screen each option against [references/red-flags.md](references/red-flags.md). An option with a red flag is revised or dropped, and the reason is recorded.

### 4. Debate

Run the debate with subagents, using the prompts in [references/debate.md](references/debate.md).

1. **Advocates.** One per option. Each argues for its option against the criteria, with evidence, and names the strongest case against it. Advocates work independently and do not see each other's work.
2. **Challenger.** One reviewer attacks every option: the failure each one hides, the number it needs that nobody measured, and the cost it moves elsewhere. Use a different model from the advocates when one is available, since different models catch different failures.
3. **Rebuttal.** Each advocate answers the challenges to its option, once.

For a small or reversible decision, one advocate per option and one challenger round are enough. Spend more rounds on decisions that are hard to reverse, such as a store, a delivery guarantee, a key, or state that must survive upgrades.

### 5. Judge

You are the judge, not a neutral summarizer. Score each option against [references/criteria.md](references/criteria.md), criterion by criterion, citing the evidence from the debate. Then:

- Pick the option that wins on the criteria this decision depends on most, and say which those are.
- Put every challenge in one bucket: **changes the decision**, **becomes a rule** (the chosen design must handle it), **accepted cost**, or **dismissed** (with the reason).
- When the evidence cannot separate two options, say so, and name the measurement or prototype that would. Building that is the next step, not a decision.

### 6. Record

Write the decision record with [references/decision-record.md](references/decision-record.md).

- It starts as `proposed`. Only the owner accepts it.
- Credit the owner only with the choices the owner made. Mark every choice you made as pending the owner's review.
- The consequences hold the rules that code must now follow, the guarantees the pipeline must hold, and the condition that would reopen the decision.
- A decision that reverses an accepted one is a new record that supersedes it. Never edit an accepted record to reverse it.

## Hand back

1. The decision record, with status `proposed`.
2. A short debate log: each option's best argument, each challenge with its bucket, and where the advocates and the challenger agreed.
3. The questions only the owner can answer, each with the options and your recommendation.
4. The guarantees `pipeline-review` must check once the design is built.
