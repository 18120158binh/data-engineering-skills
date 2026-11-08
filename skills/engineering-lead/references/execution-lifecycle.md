# Execution lifecycle

Read this when a task needs state (anything beyond a small task), when the user asks how the work is going, when resuming, and at the end to write the final report and the retrospective.

## Contents

- [When to keep state](#when-to-keep-state)
- [Where it lives](#where-it-lives)
- [What it holds](#what-it-holds)
- [Who writes it](#who-writes-it)
- [Decisions](#decisions)
- [Answering a status question](#answering-a-status-question)
- [Resuming](#resuming)
- [Final report](#final-report)
- [Delivery states](#delivery-states)
- [Retrospective](#retrospective)

## When to keep state

| Task | State |
|---|---|
| A question, a typo, a very small fix | None. The conversation and the final report are enough |
| Anything with a worker, or that may need resuming | A state file |

When a small task grows, create the state at that point and log the move.

## Where it lives

`.pm/<task-id>/state.md` in the task's workspace, where `<task-id>` is the issue id or a short slug. Worker result files sit next to it ([runtime-adapters.md](runtime-adapters.md#result-files)).

Before creating it, check that Git ignores it:

```bash
git check-ignore -q .pm/<task-id>/state.md
```

If it is not ignored, do not edit `.gitignore` and do not create the file there: coordination data must not reach the repository. Keep the state outside the repository instead (the session's scratch area, or a folder the user names), or tell the user the condition is not met. Use the repository's own convention when it has one.

The state never holds secrets: no tokens, keys, passwords, or credential output.

## What it holds

```markdown
# <task-id>: <title>
source: <issue reference, or "user request">   opened: <time>
step: <1-8>   status: active | waiting on user | blocked | merge-ready | closed

## Task
goal, acceptance criteria, scope, gates
## Workspace
repository, worktree, branch, base
## Workers
| role | name | runtime | pane / agent id | directory | status | last result file |
## Commits and review
| round | commit | coder status | checked by main | verdict | findings |
## Verification
| criterion | check | result | commit | reference |
## Delivery
| step | state | authorization |
## Blocker and next action
## Decisions
D-001 ...
## Retrospective
## Log
<time>  <transition>
```

Update it at meaningful transitions: a step change, a worker started, blocked, or closed, a result received and checked, a verdict, a verification result, a delivery step, a blocker opened or cleared. Not after every command.

## Who writes it

Only the main session. Workers write their own result files and reply with the path; the main session reads them, checks them, and records the outcome. A worker or anything it starts never edits `state.md`, so parallel work cannot overwrite it and the user gets one source of truth.

## Decisions

Record decisions that change scope, design, the order of work, risk, or delivery: a reclassification, a gate applied, a finding dropped with a reason, a fallback, a plan changed after a new finding. Skip routine reads and test runs. Each entry: an id (`D-001`), the decision, the reason in a sentence, its source (repository rule, user, method, own judgment, with a reference), the evidence it rests on (what kind, and a reference precise enough to check), who decided, the alternatives, and its status (accepted, open for the user, or superseded by a later id). Keep superseded entries. Say what is confirmed, what is inferred, and what is unresolved.

## Answering a status question

When the user asks how the work is going:

1. Read the state.
2. Check it against reality where that is cheap: each worker's current status (`herdr agent get`, or the latest notice), `git log` on the task branch.
3. Answer briefly: the step; each worker's state; the latest commit and its verdict; the blocker, if any; the next action; the delivery state.
4. Carry on from where the work was.

Do not restart, re-plan, or re-ask what is decided. If the state and reality disagree, say so, correct the state, and then answer. A long blocking wait must not stop this; see [runtime-adapters.md](runtime-adapters.md#waiting-without-going-deaf).

## Resuming

A new session given a task id, or finding one open state for the work at hand:

1. Reads the state.
2. Re-checks the repository context and Git state ([project-context-discovery.md](project-context-discovery.md#later-runs)).
3. Checks each worker recorded as active: does it still exist, under the recorded name and pane, in the recorded directory? Workers it cannot confirm are not its to use; start new ones and record that.
4. Checks result files that arrived since the last update.
5. Continues from the recorded step and logs the resumption.

Trust the state only as far as these checks confirm it.

## Final report

Report, sized to the task:

- the outcome against each acceptance criterion: the check, its result and output, the commit it ran on, and any limitation. A passing command proves only what it tested;
- the workers used, the runtime, and how each capability was used (invoked, read and followed, or assigned);
- the review rounds and how the findings were resolved;
- the decisions made, by id;
- the delivery state of each step, and for the next external step whether it is authorized, waiting for someone's approval (name who), or not applicable;
- external actions, when any were in scope: provider and repository, local or remote, the identity by a non-sensitive name, each channel's authentication, the permission, the authorization and its source, the gates, what was performed with the provider state that confirms it, and what is blocked and by which condition ([authentication-and-permissions.md](authentication-and-permissions.md));
- what is still open, and the retrospective.

The result is separate from the delivery:

| Result | Meaning |
|---|---|
| Done | Every acceptance criterion is met, with evidence on the final commit |
| Partially done | Part is complete; the rest is listed as open |
| Blocked | The task cannot continue for lack of access, a decision, a dependency, or a precondition, named as open |

Never put credentials or secret-bearing values in the report.

## Delivery states

Report each delivery step (implemented, verified, pushed, PR opened, reviewed, approved, merged, deployed) with one of these states, never a blank:

| State | Meaning |
|---|---|
| Complete | It happened and was checked, on the provider where it can be queried |
| Not reached | Part of this work, not yet done, such as a PR waiting for approval |
| Not requested | The user did not ask for it |
| Not applicable | This work has no such step |

List every step, even the ones that did not happen. For a bug fix taken to an open PR, with no go-ahead to merge:

```text
implemented   complete       b9ffd04 on fix/idempotent-daily-load
verified      complete       unittest 2 OK on b9ffd04, run by the main session
pushed        complete       origin/fix/idempotent-daily-load at b9ffd04
PR opened     complete       PR #42
reviewed      complete       reviewer approved b9ffd04
approved      not reached    waiting for the code owner
merged        not requested  waiting for the user's go-ahead
deployed      not applicable
```

Rules that keep it honest:

- **Reviewed** is the independent reviewer's verdict on a commit. **Approved** is the repository's required approval. Neither is the other, and neither is authorization to merge.
- A state the user reported but no one could confirm is reported as told: "PR opened: reported by the user, not confirmed".
- A step prepared locally has not happened. A drafted PR description, or a commit not pushed, leaves pushed and PR opened Not reached or Not requested, with a note on what is ready.
- A partial run reports each step as it is. "Pushed, PR not opened" is true; "delivered" and "nothing happened" are both false.
- Never call work shipped or released unless the merge or deploy is Complete.

## Retrospective

After meaningful work, a few lines in the state, and in the repository's retrospective log where it keeps one (such as `.pm/retros.md`):

- what worked;
- what caused rework, and its root cause;
- whether the briefs were clear enough;
- whether the skills and agents chosen fitted;
- whether worker coordination worked;
- what verification or review missed;
- what to change next time.

When the repository keeps a lesson log, write each lesson there as it happens, not only at the end, and end it with one line:

```text
Next action: <where> / <change> / <status>
```

`where` is the place that owns the fix: a test or script, a project skill or doc, a generic skill, memory, or `none` for a one-off. `change` is the smallest edit, in one sentence. `status` is `done <commit or PR>` only when the change has landed, otherwise `open`. When a lesson repeats an earlier one, start with `Repeats lesson <n>.`: the earlier fix was text that did not hold, so the next action is a script or a check. **Why**: a lesson logged without a destination is read once and lost; in one two-day run, 36 of 57 logged lessons were still open at the end, and the one fixed only in text came back three times.

At the end of a delivery, or when several lessons are open, run the `retrospective` skill over the log (pstack `reflect` when it is not installed). It routes each open lesson to one change.

It may propose changes to this skill, the repository's agents, skills, or instructions, the pstack integration, the briefs, or the execution policy. These are proposals only. List them for the user; a human must approve each one before anything is changed, and the agent never applies one on its own.
