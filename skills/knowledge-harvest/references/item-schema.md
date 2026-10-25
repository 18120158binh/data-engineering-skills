# Item schema

Every slice returns items in this shape, so the catalog can be merged, sorted, and reviewed.

## Fields every item has

| Field | Content |
|---|---|
| Kind | One of the kinds below. |
| Topic | The theme it belongs to, such as reruns, alerting, or tool choice. |
| Evidence | `file:line` or a commit hash, plus a quote of at most two lines. |
| Source | **STATED**: the owner wrote it as a rule or a decision. **INFERRED**: you read it from code, commits, or behavior. **TEAM**: a teammate wrote it. **THIRD-PARTY**: copied from another project. |
| Date | When it was written or decided, from git. |
| Route | Where it should live: a test, a contract, a decision record, a skill, `AGENTS.md`, or a script. |

## Kinds

**Rule**
- RULE: one imperative sentence.
- WHY: the failure it prevents, from the evidence.
- TEST: the question a reviewer asks, or the check to run.

**Decision**
- CHOICE: what was chosen.
- AGAINST: the alternatives, each with why it lost.
- CRITERIA: what decided it.
- STATUS: proposed, accepted, superseded, or rejected.
- REVERSED: if it was reversed, by what, and what triggered it.

**Failure story**
- WHAT: what happened, with numbers and a date.
- NOTICED: how and when someone found out.
- FIX: what changed.
- RULE: the rule it produced, or "none yet".

**Gotcha**
- TOOL: the tool and its version.
- BEHAVIOR: what it does that a user would not expect.
- HOW KNOWN: read from docs, read from source, or reproduced.

**Number**
- VALUE: the measured value, with its unit.
- RUN: how it was measured, when, and how many runs.
- MEANING: the decision it supports.

**Open problem**
- WHAT: drift between a document and the code, a secret in source, or an open defect.
- RISK: what it can break.
- OWNER: who should fix it, if known.

## Example

```markdown
- Kind: Rule
- Topic: reruns
- RULE: Save the cursor only after the effect it covers succeeds.
- WHY: A save before a failed send loses those errors for good.
- TEST: Kill the run between the send and the save. Does the retry resend exactly the unsent errors?
- Evidence: docs/error-monitor.md:113 "If the message cannot be sent: the Variable stays unchanged"
- Source: STATED
- Date: 2026-10-14
- Route: pipeline-review principles, theme 1
```
