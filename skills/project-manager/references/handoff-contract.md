# Handoff contract

Read this during execution to keep the decision trail, and at stage 5 to write the hand-back. Both work with or without Superpowers and pstack.

## Contents

- [Decision trail](#decision-trail)
- [Hand-back](#hand-back)
- [Verification](#verification)
- [Result and delivery](#result-and-delivery)
- [Sizing the hand-back](#sizing-the-hand-back)

## Decision trail

Record decisions that materially affect scope, architecture, execution order, ownership, risk, or delivery: the mode, the work type and scope, the workflow owner and execution orchestrator, a conflict settled, a phase skipped, a fallback taken, a plan changed after a new finding. Do not record routine tool use, file reads, ordinary test runs, or implementation details that do not change the direction of the work. A trail that logs everything buries the decisions that matter.

Each entry carries:

| Field | What it holds |
|---|---|
| ID | `D-001`, `D-002`, ... so the hand-back and later entries can refer to it |
| Phase | Where in the run it was made |
| Decision | What was chosen |
| Reason | Why, in a sentence |
| Source | Where the authority for it comes from: its type (project rule, project workflow, user, workflow owner's skill, agent judgment) and a reference (file and section, the user's message, the skill) |
| Evidence | What it rests on: its type (measured, read from code, read from docs, stated by the user, inferred), a reference precise enough to check (file and section, command, output), and the finding in a sentence |
| Decided by | Who made it: the agent, the user, a human approver, or the project workflow; a name only when known |
| Alternatives | What else was possible |
| Status | Accepted, open for the user, or superseded by a later ID |

Example (illustrative):

```text
D-003  plan
  decision: add the column and backfill it in two separate migrations
  reason: the project requires backward-compatible migrations
  source: project rule; CONTRIBUTING.md, "Migrations"
  evidence: read from docs; CONTRIBUTING.md, "Migrations";
    "every migration must stay compatible with the previous application version"
  decided by: agent, applying the project rule
  alternatives: one migration that adds and backfills
  status: accepted
```

When a decision changes, mark the old entry superseded with the new ID, and keep it. The history of why the plan moved is part of the record.

The format is free. Keep one authoritative trail per run: the execution orchestrator's ledger when it holds these fields, pstack `show-me-your-work`, or a record the project already keeps. A conclusion without its evidence, or with its doubts left out, is the thing to avoid: say what is confirmed, what is inferred, and what is unresolved.

## Hand-back

| Field | What it holds |
|---|---|
| Workflow | The mode (project-native, hybrid, default), the workflow owner, and why |
| Project rules | The rules that shaped the work, and where each was applied |
| Capabilities | Skills, agents, and tools used, by phase, and how each was invoked (native or read-and-follow); any that were unavailable and what replaced them |
| Execution | What was done: files, commits, PRs |
| Verification | Each acceptance criterion with its check and result; see [Verification](#verification) |
| Decisions | Decisions made without the user, by trail ID |
| Open items | What is unresolved, and what needs the user |
| Delivery | The state of each delivery step; see [Result and delivery](#result-and-delivery) |
| Result | Done, partially done, or blocked |

Report what each phase produced, not that a skill was invoked. Calling a skill is not finishing the work.

## Verification

Map verification back to the request's acceptance criteria. For each criterion, report:

- the check performed;
- its result, with the relevant output;
- whether it ran in this session;
- any limitation or remaining doubt.

A successful command proves only what it tested. "All tests pass" says nothing about a criterion no test covers. Compare:

```text
Verification
- API returns the documented schema: integration test test_upload_schema, passed (this session)
- Files up to 100 MB accepted: not tested; largest fixture is 5 MB
- Existing behavior unchanged: full suite, 124 passed (this session); no test covers the old CSV path
```

That is a more honest hand-back than "all tests passed, feature complete".

## Result and delivery

The result says whether the request was met. The delivery says how far the change has travelled. They are separate because a request can be fully met at "PR opened", and a deployed change can still miss a criterion.

| Result | Meaning |
|---|---|
| Done | The request's acceptance criteria are met, with evidence from this session |
| Partially done | Part of the work is complete; the rest is listed in open items |
| Blocked | The run cannot continue for lack of access, a decision, a dependency, or a precondition, named in open items |

Report each delivery step (implemented, verified, PR opened, approved, merged, deployed) with one of these states, never a blank. Approved means the review the project requires has been given by its approver; an open PR with green checks is not approved.

| Delivery state | Meaning |
|---|---|
| Complete | The step happened and was checked: the commit exists, the PR is open, the merge or deploy was confirmed |
| Not reached | The step is part of this work but is not finished, such as a PR waiting for review |
| Not requested | The user did not ask for this step |
| Not applicable | This work type has no such step, such as a deploy for a read-only investigation |

Example: a feature whose request was "build it and open a PR" can be **Done** with implemented, verified, and PR opened Complete, approved and merged Not reached (waiting for the reviewer), and deployed Not requested. Never call work shipped or released unless the merge or deploy is Complete.

## Sizing the hand-back

Choose the detail by work type, risk, and delivery scope. Keep every field that applies, and leave out the ones that do not; a short report must still carry the evidence that matters.

| Work type | Put first |
|---|---|
| Read-only investigation | The answer, its evidence, what is still unknown |
| Bug fix | Root cause, the fix, the regression check, verification |
| Feature | New behavior against the acceptance criteria, tests, delivery |
| Refactor | Behavior shown unchanged, tests, the extent of the change |
| Migration | Compatibility, the migration steps, rollback, verification |
| Multi-work-package | Each package's state and dependencies, then the whole |

A short investigation does not need a full delivery report, and a production migration should not get a minimal summary.
