# Integration contract

Read this when integration is called, before planning and again before the hand-back. It defines who owns the integration, what it may change, and when it is complete. [integration-playbook.md](integration-playbook.md) describes how to get there.

## Ownership

- The current agent owns the integration as a whole. This covers only the integration process; normal engineering work in the target repository afterwards is owned per issue by the main session that runs it.
- Sub-agents may own bounded work packages: one repository's audit, one set of edits, one evaluation scenario.
- The current agent stays responsible for consolidating their results, resolving conflicts, verifying, and handing back.
- Every approval gate in the target repository stays in force.
- The user is the human approver for decisions about the integration itself.
- The repository's own approval gates are met by their designated approvers, such as a tech lead for schema design, a code owner for a pull request, or a security team for production permissions. Do not assume the user can satisfy or override them.

## Modification boundaries

- Audit before modifying.
- Keep existing project rules and workflows unless the user approved a change to them.
- Do not silently remove, override, or weaken an existing instruction.
- Do not change protected-branch, CI, merge, deployment, or production permissions without authorization.
- Keep changes scoped to the integration.

## Completion criteria

An integration of a repository is complete only when each of these holds, with evidence:

1. An agent starting in the repository finds the engineering lead and invokes it for engineering work, shown by a fresh session's log; the repository's instructions say when to use it.
2. The main session owns an issue from intake to close: it states the criteria, starts and checks the workers, runs the review loop, and decides merge readiness.
3. The repository's own instructions, agents, skills, tools, workflows, and gates are discovered and respected, and still work as before.
4. pstack execution principles are applied by the coder (`poteto-mode` where it can start, its principles otherwise), and Superpowers methods are used as methods, without a second workflow controlling the issue.
5. The coder and the reviewer stay independent: the reviewer did not write the change and does not edit it, and its verdict names the commit it reviewed.
6. Review findings go back to the coder through repeated rounds until the review is clean or blocked.
7. Verification rests on evidence the main session checked on the final commit.
8. Merging follows the repository's policy and the user's explicit authorization; approval gates and delivery boundaries are preserved.
9. Workers the main session owns are closed after the merge, and nothing it does not own is touched.
10. Status questions are answered from the task state, and a new session can resume a task.
11. Each runtime the repository is meant to use (Herdr persistent sessions, native subagents) has been exercised by at least one real run; a runtime not tested is reported as not tested.
12. Every applicable scenario from the [playbook](integration-playbook.md#phase-5-evaluate-end-to-end) has been run, or replaced by an equivalent with the reason recorded, and each result and the remaining gaps are reported with evidence.
13. No shared rule, skill, or instruction was changed without the user's approval.

Installing or copying files does not establish a successful integration. Do not report the integration as done while a required capability or evaluation remains unverified; report it as partially done, with what is missing.

## Evaluation status

Report each scenario as one of:

| Status | Meaning |
|---|---|
| Passed | Run, and every check met, with evidence |
| Failed | Run, and at least one check not met |
| Blocked | Could not run because of a missing access permission, dependency, or required approval |
| Not run | Not attempted, or the evaluation environment could not test the intended integration |

An unexecuted scenario is never passed.

## Delivery boundary

Integration does not authorize pushing, merging, or deploying anything unless the user asks for it, per [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries). Report each delivery step with its state, as defined in [execution-lifecycle.md](execution-lifecycle.md#delivery-states).

## Hand-back

Per repository:

- how each common work type runs (directly, or coder and reviewer), and why;
- the capability map and the runtime;
- files added or changed;
- workflows and capabilities preserved;
- capabilities supplied from pstack or Superpowers, and why;
- each scenario with its status and evidence;
- known limitations and unresolved gaps;
- decisions the user must make;
- the delivery states;
- integration status: done, partially done, or blocked, where done requires every completion criterion above.
