---
name: pipeline-review
description: Check a data pipeline, Airflow DAG, stream job, CDC flow, or ops job against the principles that keep it correct under retries, reruns, replays, backfills, late data, partial failure, and on-call. Lists every side effect, walks each through rules for cursors and checkpoints, idempotent writes, backfill and late data, partial failure, concurrency and limits, alerting, data quality, retention, secrets, and human gates, then proves the one fact the pipeline's safety rests on by running code. Use it when you build, change, or review a pipeline, before a merge or a first deploy, after an incident, or when someone asks "is this safe to rerun", "what happens if it fails halfway", "will this double count", or "why did nobody get alerted".
metadata:
  version: "0.1"
---

# Pipeline review

A pipeline is correct when it reaches the same end state however many times it runs and wherever the last run stopped, and when a person learns about it the moment it cannot. This skill checks a pipeline against that standard. Each rule in [references/principles.md](references/principles.md) names the failure it prevents.

## Where this fits

| You need | Skill |
|---|---|
| Choose the design before building | `architecture-review` |
| Compare tools or vendors for a role | `tech-market-research` |
| Check the tables a pipeline writes | `data-modeling` |
| Airflow-specific rules: contracts, top-level code, the deployed version | `airflow-dag-repo` |

When `architecture-review` produced a decision record, its "Guarantees the pipeline must hold" list is part of what you check here.

## Steps

Open a todo list with one entry per step.

### 1. Scope

- Name what you review: the files, the DAG or job, and its contract or decision record if one exists.
- State the pipeline's purpose in one sentence, and what it must never change.
- If the purpose, a limit, or a failure rule is missing, ask the owner. Do not take the answer from the code, because the code may be the part that is wrong.

### 2. List the side effects

List every effect the pipeline has outside its own process: each write, delete, message, external call, state save, and lock. For each one, note what it depends on and what runs after it.

**Why**: every rule below is about an effect. A review that starts from the code's structure checks the tasks and misses the effect that two of them share.

### 3. Walk the principles

For each effect, ask the questions in [references/principles.md](references/principles.md), theme by theme:

1. Reruns, cursors, and checkpoints
2. Writes under replay
3. Backfill and late data
4. Partial failure and failing dependencies
5. Concurrency, limits, and cost
6. Alerting
7. Data quality and schema change
8. Retention of state
9. Secrets and data boundaries
10. Human gates and production

Skip a theme only when no effect touches it, and say why. Hand table-level findings to `data-modeling` and Airflow-level findings to `airflow-dag-repo` rather than restating their rules.

### 4. Prove the one fact

Most pipelines are safe or unsafe because of one or two facts, such as "the cursor is saved only after the send succeeds" or "a second insert with the same key does nothing". Find those facts and get each as far down this list as is cheap:

1. You said so.
2. You pointed at the line.
3. You walked the failure step by step and it does not reach.
4. You ran it: a test or script that calls the real code with a fake at the boundary, runs it twice, or kills it between two effects, and fails loudly if you are wrong.
5. You reproduced it on a real run.

Say where each fact stopped. A fact below step 4 is unproven, so write it as unproven. This ladder comes from the `blast-radius` skill in pstack, by Lauren Tan (MIT). Label every claim as read from the code, run, or inferred.

### 5. Find the root, not the patch

When two findings share one cause, report the cause. When the fix needs a different shape, such as a shared row many writers update, a lock to serialize writers, or exactly-once assumed across systems that do not share a transaction, the problem is the design. Send it to `architecture-review` instead of proposing a patch.

### 6. Challenge the serious findings

For a blocker or a high finding that only one reviewer raised, have a second reviewer try to refute it, on a different model when one is available. A reviewer does not see what another reviewer found before writing its own findings. Keep the finding only if it survives.

## Severity

| Level | Meaning |
|---|---|
| Blocker | Loses or corrupts data, duplicates an external effect, or fails silently. Do not merge. |
| High | Breaks on a normal event (a retry, a late row, a slow dependency) and needs a person to repair it. |
| Medium | Costs time, money, or noise, and recovers without a person. |
| Note | Worth knowing, and no action needed now. |

## Hand back

```markdown
## Verdict
PASS, ISSUES, or BLOCKED, in one sentence.

## Side effects
| Effect | Depends on | Runs after | Safe to repeat? |

## Findings
For each: severity, the principle, what breaks and how (the input or event and the bad end state), the evidence (file:line, and the test or run with its output), and the fix.

## The facts it rests on
Each fact, the step it reached, and the proof.

## Not checked
What you could not check and why. Never report a check you did not run as passed.

## Design questions
Findings sent to architecture-review, and questions for the owner.
```
