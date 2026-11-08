# Worker contract

Read this before briefing a coder or a reviewer, when a result comes back, and before declaring a task merge-ready. It defines the two worker roles, what each is given, what each returns, how the main session checks results, and how the review loop runs. How workers are started and closed is in [runtime-adapters.md](runtime-adapters.md); which capabilities they use is in [repository-adaptation.md](repository-adaptation.md).

## Contents

- [Roles](#roles)
- [When to use workers](#when-to-use-workers)
- [The coder brief](#the-coder-brief)
- [The coder result](#the-coder-result)
- [Checking the coder's result](#checking-the-coders-result)
- [The reviewer brief](#the-reviewer-brief)
- [The reviewer result](#the-reviewer-result)
- [The review loop](#the-review-loop)
- [Merge readiness](#merge-readiness)

## Roles

| Role | Owns | Does not |
|---|---|---|
| Main session | The issue: understanding it, the decisions, the state, checking results, the review loop, merge readiness, delivery, and closing | Hand its decisions to a worker |
| Coder | One implementation assignment: the change, its tests, its checks, the commit, pushing the task branch, and opening or updating the PR, like a human engineer would | Merge, deploy, approve, or decide that the task is done |
| Reviewer | An independent review of the PR at one head commit, posted on the PR | Edit implementation files, fix what it finds, push, or merge |

The coder may work through `poteto-mode` or a Superpowers method inside its assignment, including subagents of its own. That is how it does the work, not a second owner of the issue: its brief bounds the scope and forbids delivery. The reviewer must be a fresh agent that did not write the change.

## When to use workers

| Task | How it runs |
|---|---|
| A technical question | The main session answers it |
| A typo or a very small fix | The main session may do it directly, where the repository allows; it still runs the checks |
| An ordinary bug fix | Coder, then reviewer |
| A larger feature | Coder, then reviewer; an investigator first if the code is unknown territory; several coder assignments in sequence when the work splits into verifiable parts |
| Review feedback on an existing change | Coder fixes, reviewer checks again |

Two roles are the standard for engineering work, not a quota. Do not start a worker that has nothing to do yet: the reviewer starts, or is given work, once there is a commit to review.

## The coder brief

A worker does not see the main session's conversation. Each assignment carries:

- the task goal and its acceptance criteria;
- the repository instructions that apply, and where they are written;
- the skills to use, by exact path, with "read it first and follow it"; in a Herdr session, the brief is sent as `/poteto-mode <brief>` where pstack is installed;
- the workspace and branch;
- the files and areas in scope, and the interfaces it must not change;
- the constraints: contracts, gates, test policy;
- the checks it must run, by command. Fixtures that stand in for an external system's response (an API, a metrics query, a provider) are recorded real responses or the provider's documented examples. **Why**: a fixture written from the code's own assumption passes while the real call never matches. A new step that runs against live infrastructure (a bootstrap or node script, a migration, a permission grant) also gets a safe live run before delivery: read-only, idempotent, or a stub test the coder runs. **Why**: a step that was only read in review can still fail on its first live run, for a reason no reader sees, such as a missing permission;
- the cross-cutting rules every change in this area must keep, each with the test that checks it (for example: every page checks the session itself, with a no-session test). When a review finds a new one, add it to the brief of every coder working in that area, not only the one whose PR it was found on. **Why**: a rule that lives only in reviews is learned again by each coder, one finding at a time;
- the side effects: every write outside the task branch the work needs (cloud, cluster, secret store, Git remote, merge, delete), and for each who performs it: the worker, the main session, or the user. A write the worker's harness may block (applying infrastructure, writing a secret, a remote shell write, deleting branches) is planned from the start as a user step, with a ready script. Before an approved live operation, list every write it needs and get each permission in place before the first step. **Why**: the user's approval in the main session's chat does not reach a worker's session, and a blocked write discovered halfway leaves the system half changed;
- the boundary: commit on the task branch, push it, and open the PR (or update it on a rework round) with the repository's PR tool; no merge, approval, or deploy; never credentials. If the push or PR fails for missing access, stop and report it, without workarounds. If the repository has no remote or PR process, commit locally and report the commit;
- when to stop and report instead of guessing: an unresolved design decision, a silent contract, a missing dependency, a permission boundary, anything out of scope;
- how to return the result: as its final message for a native subagent, or written to `.pm/<task-id>/coder-<round>.md` for a Herdr worker ([runtime-adapters.md](runtime-adapters.md#result-files)), with the contents listed below;
- to keep every file it creates (notes, scratch checkouts, logs) inside the task's workspace; a separate checkout, if it needs one, goes under `.pm/<task-id>/`, never in `/tmp`.

For a rework round, the brief points the coder at every review on the PR, not only the latest, and lists every required finding still open from any round, each with the round it was raised in and what must not regress. The coder answers each finding by id. **Why**: a fix brief built from the latest review alone dropped two required findings from round 1, and only the reviewer noticed. The same coder and reviewer stay on the task across all rounds ([runtime-adapters.md](runtime-adapters.md)), so the brief can name the reviews instead of retelling them.

### Parallel assignments

When several coders work at once, list the files more than one of them will touch (route tables, shared components, a shared config) before starting them. Give each shared file one owner assignment; the others leave it alone or ask the owner. Merge the assignment that touches the most shared files first, and have each later one merge the new base before its review. **Why**: parallel lanes that each edit a shared file pass review alone and then conflict, or break each other, at merge.

## The coder result

- Status: done, partial, or blocked, and why.
- What was implemented, in a few lines.
- Files changed.
- The PR (number or URL) and its head commit SHA, or the local commit when there is no PR process.
- The checks run, by command, with their results.
- Evidence for each acceptance criterion.
- Decisions it made, and why.
- Concerns, questions, and blockers.

Writing code is not finishing the task. "Done" is the coder's claim; the main session decides.

## Checking the coder's result

Before sending anything to review:

1. Read the diff at the reported commit. Changes outside the brief's scope go back, or become their own assignment.
2. Check each criterion against its evidence. A criterion with no evidence is not met. Re-run the checks that are cheap or that matter most.
3. Check the interfaces others depend on.
4. Accept it for review, or send specific feedback as a rework round.

Worker evidence is enough for an assignment once the main session has checked it. The final state is different: see [Merge readiness](#merge-readiness).

## The reviewer brief

The reviewer gets the material to judge for itself, not the coder's summary:

- the original issue and its acceptance criteria;
- the repository rules and conventions that apply;
- the PR to review (number or URL) and its head commit SHA; without a PR process, the local commit and its base;
- the coder's verification evidence, as a claim to check;
- the method to follow, by path: the repository's review skill, or pstack `interrogate`; in a Herdr session the brief is sent as `/poteto-mode <review brief>`, as for the coder. Superpowers `requesting-code-review` is the fallback where pstack is not installed;
- the boundary: read and run checks only, in its own checkout; never in the coder's folder; no edits to implementation files, no push or merge; post the review on the PR with the repository's PR tool, with the verdict and the head SHA it applies to;
- how to return the result: as its final message (native), or in `.pm/<task-id>/reviewer-<round>.md` (Herdr);
- to keep every file it creates inside the task's workspace; to check out the commit separately, use `git worktree add .pm/<task-id>/review-<round> <sha>` and remove it afterwards, never a path in `/tmp`.

## The reviewer result

- The verdict: **approved**, **changes requested**, or **blocked**.
- The commit SHA it reviewed.
- Findings, each with a severity, the file and line, what is wrong, the failure it causes, and the evidence (a reproduction, a failing check, the line).
- The corrections required, kept separate from optional suggestions.

The reviewer checks correctness, the acceptance criteria, regression risk, the repository's conventions, test coverage and evidence, and security or operational concerns where they apply. It checks that each fixture standing in for an external response is real or documented, not copied from the code's assumption.

## The review loop

1. The main session reads the findings and decides what is actionable: it may drop a finding with a reason, or take one to the user when it needs their judgment.
2. The coder gets specific feedback (the finding, the evidence, what must hold after the fix), fixes, re-runs the checks, commits, and pushes to the same PR.
3. The main session checks the new result as above.
4. The reviewer reviews the PR again at its new head commit.
5. Repeat until the verdict is approved, or a blocker needs the user.

A verdict holds only for the SHA it names. Any change to the code after a review, however small, needs a new review of the new SHA. Never carry an approval forward.

After two rework rounds on the same finding or assignment that still fail, stop sending the same request. Re-examine the cause: the brief, the design, how the work was split, or a premise the fixes share (pstack `principle-attack-the-premise`). Continue only after changing the approach, and record what changed. Ask the user if the cause needs their judgment.

## Merge readiness

The main session declares a task merge-ready only when all of these hold, with evidence it checked itself:

- every acceptance criterion is met on the final commit;
- the checks the change needs pass on that commit, run by the main session or confirmed from CI for that SHA; evidence from an earlier commit does not count;
- the required CI checks pass;
- the checks pass on the head merged with the base's current tip: the provider's merge ref when it runs checks there, otherwise a trial merge the main session or the reviewer runs with the full suite. After another PR merges into the base, check again before merging this one. Several PRs delivered together get one trial merge of all their heads. **Why**: two PRs that each pass alone can break the base together, and a repository without "require up-to-date branches" will not stop it;
- the reviewer approved exactly that commit;
- the repository's own required approvals are present (a code owner, a lead, or whatever the repository defines);
- no blocker or open question remains.

A reviewer's approval is not authorization to merge, and merge-ready is not merged. Merging needs the user's explicit authorization and the repository's policy, checked per [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries) and [authentication-and-permissions.md](authentication-and-permissions.md). Without it, stop at merge-ready and report what remains.
