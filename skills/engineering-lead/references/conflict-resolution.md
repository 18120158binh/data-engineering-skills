# Conflict resolution

Read this when two instructions point different ways, or before combining the repository's instructions with a Superpowers or pstack method. This guide settles authority, applicability, ownership, and conflicts. It does not design a workflow; engineering method stays with the repository's workflow, Superpowers, or pstack.

## Contents

- [Types of instruction](#types-of-instruction)
- [Precedence](#precedence)
- [When both cannot hold](#when-both-cannot-hold)
- [One issue owner](#one-issue-owner)
- [Side-effect and delivery boundaries](#side-effect-and-delivery-boundaries)
- [Where Superpowers and pstack differ](#where-superpowers-and-pstack-differ)

## Types of instruction

Most apparent conflicts come from mixing up these kinds:

| Kind | What it defines | Example |
|---|---|---|
| Working rule | A constraint the work must satisfy | Every migration must be backward compatible |
| Workflow | Phases, ordering, ownership, and transition conditions | Design, then plan, then build, then review |
| Approval gate | A decision or authorization required before continuing; a human approver meets it | The tech lead approves the schema design |
| Methodology | How an activity is performed | Test-first development |
| Capability | A skill, tool, script, or agent that performs an activity | A `schema-change` skill, pstack `architect` |

They interact in predictable ways. A methodology is a way to meet a rule, so the two rarely conflict. A methodology cannot remove a gate the workflow requires. The human approver behind an approval gate is not a capability, and the user's go-ahead does not meet a gate that names someone else. And using a capability does not show that a rule was met: running `schema-change` does not prove the migration is backward compatible, so check the rule on its own.

A real conflict is two applicable instructions that cannot both hold, such as a project rule "work on a branch, no worktrees" against Superpowers `using-git-worktrees`.

## Precedence

Resolve instructions in this order:

1. System, platform, security, and safety constraints.
2. Explicit authorization and constraints from the user for this request, within the authority they have over the project.
3. Applicable mandatory project rules and approval gates.
4. The selected project workflow, including its required order and transition conditions.
5. Default methodologies and capabilities from Superpowers and pstack.
6. This router's fallback judgment.

Two qualifiers decide most cases:

- **Applicability.** An instruction only governs what it covers. A rule that every code change gets reviewed does not apply to a read-only question. Check scope before ranking.
- **Direct conflict only.** A higher-ranked instruction overrides a lower one only where they directly conflict. Compatible instructions all stay in force and are combined: the project's review rule and a method's verification step both apply.

A user request does not automatically override a project restriction. When the user's authority or intent is unclear, ask before any action that bypasses a protected branch, a production safeguard, a security control, or a required human approval. "Just push it" from someone who may not know main is protected is a question, not an authorization.

## When both cannot hold

First check whether precedence and applicability settle it.

- **Resolvable.** The higher-ranked instruction is clear: follow it, and record both sources and the resolution. The project forbids worktrees and a Superpowers method uses them, so work on a branch and note that `using-git-worktrees` was skipped because of the project rule.
- **Unresolved.** Authority, scope, or intent is unclear: pause the affected activity and ask the user.
- **Safety-critical.** The conflict involves data safety, security, production, or an irreversible action: do not proceed without the required authorization, however the ranking looks.

Then decide what it blocks. A conflict usually blocks only the activities that depend on it. If the project requires approval before a schema change and the user asks to ship now, the migration waits, but tests, code that does not depend on the new schema, and documentation can go ahead. Keep working on what is independent.

Record:

- the conflicting instructions and their sources;
- why they cannot both be satisfied;
- the precedence or the uncertainty involved;
- the decision and who made it, or the open question;
- which activities are paused, and which continue.

## One issue owner

The main session owns the issue: its decisions, its state, the review loop, merge readiness, and delivery ([worker-contract.md](worker-contract.md#roles)). The coder and the reviewer do bounded assignments. A coder working through `poteto-mode`, a Superpowers method, or subagents of its own does so inside its assignment; it does not become a second owner, and its brief keeps delivery with the main session, unless the user has let a Herdr pair merge its own PRs ([worker-contract.md](worker-contract.md#in-herdr-the-pair-may-merge-when-the-user-says-so)). Human approvers stay separate from all of them: a code owner who must approve a PR is not met by the reviewer's verdict or by the user's go-ahead.

When the shape of the work changes, for example a bug fix turns out to need a migration, the main session records the change, the reason, and how the assignments change.

## Side-effect and delivery boundaries

This section is the single definition of when an external action is authorized. [authentication-and-permissions.md](authentication-and-permissions.md) covers how to check identity and technical permission, and refers back here for authorization.

External actions are externally visible or irreversible:

- pushing a branch;
- creating or updating a pull/merge request;
- submitting a review, or approving;
- merging;
- releasing or deploying;
- changing production resources or permissions, or the configuration of another external system.

An external action may proceed only when four separate conditions all hold:

| Condition | Question |
|---|---|
| Authentication | Which identity is acting, and is it authenticated for the channel this action uses? |
| Technical permission | Can that identity do this action on this resource? |
| User authorization | Did the user, or an applicable higher-priority instruction, explicitly authorize this action? |
| Repository policy | Do the project's and the organization's rules and gates permit it now? |

None of them implies another. Credentials and permissions do not grant authorization, and the user's authorization does not override branch protection or an approval gate that names someone else.

Check authorization before choosing a capability whose job is one of these actions, not only before running its command. Once a PR skill is loaded, its steps lead straight to the push.

Authorization covers the action asked for and its direct prerequisites, nothing more:

| The user says | What it covers |
|---|---|
| "Fix this bug", or any task given to the engineering lead | The fix, pushing the task branch, opening its PR, and the review posted on it (the skill's default flow), unless the user or the repository says otherwise; not a merge |
| "Commit the changes" | The local commit |
| "Push this branch" | Pushing that branch, within the project's rules |
| "Open a PR" or "create an MR" | Pushing the branch it needs, and opening it, within the project's rules |
| "Review this PR" | The review; not an approval or a merge |
| "Approve this PR" | The approval, where the identity may give it and the review policy allows it |
| "Merge this PR" | The merge, once the required permissions and gates are met |
| "Deploy this change" | The deploy, to the named target only, within the deployment gates |

Do not infer authorization from:

- **What is technically possible.** Available tools, working credentials, the identity's permissions, a command allowlist, or a command that would run.
- **A workflow or skill that describes the action.** A project's PR skill or a provider's "open a PR" step says how to do it, not when it is wanted.

Opening a PR does not authorize merging, deploying, or other remote changes, and the same reading applies to each later step. Outside a task given to the engineering lead, a vague request such as "share it with the team" is a question to ask, not permission to publish.

When authorization is missing or unclear:

1. Stop before the external action.
2. Finish the local preparation that is still in scope.
3. Ask the user, or the designated approver, for the specific authorization, naming the action.
4. Report what was done and what was not, per [execution-lifecycle.md](execution-lifecycle.md#delivery-states).

Never attempt the action to find out whether it is allowed. A push that fails for lack of a token was still attempted without authorization. The same goes for technical permission: use a read-only check where the provider offers one, and when none can establish the permission, report it as unknown rather than pushing to see.

When an action is denied, do not switch to another identity or escalate permissions to get past it. When a provider call times out or returns an unclear result, query the provider for what actually happened before retrying. Creating a PR or submitting an approval is not safe to repeat blindly. [authentication-and-permissions.md](authentication-and-permissions.md#when-something-fails) has the details.

Instructions and enforcement are separate safety controls. Runtime permissions, credentials, branch protection, and other external checks may stop an action; an instruction does not. Do not rely on either alone: follow the instruction even when nothing would enforce it, and do not treat a missing technical block as permission.

## Where Superpowers and pstack differ

Superpowers and pstack are methods here, not owners. Their policies differ in a few places, and the difference decides what a coder's or reviewer's brief asks for. The repository's rules and the user's preference come first in every row.

| Question | Superpowers | pstack | How to handle it |
|---|---|---|---|
| When to ask the user | `brainstorming` gates building on approval of the design; `writing-plans` asks for review and an execution method | `principle-never-block-on-the-human`: proceed on reversible work; pause for irreversible actions | Keep every approval gate of the repository and of the methods in use. Do not ask again about a decision already approved. Do not widen scope without asking. A decision beyond the agent's authority, or with high risk, still needs approval. |
| Test first | `test-driven-development`: a failing test first, exceptions only with the user's permission | `tdd`: test first when there is a cheap local test target | The repository's test policy first; otherwise the coder's method. Where the method calls for a failing test, the check must actually show the failure; a docs change or a read-only task may have none to build. |
| Fixes keep failing | `systematic-debugging`: after three failed fixes, question the architecture | `principle-attack-the-premise`: after two that share a premise, test the premise | These are heuristics, not retry quotas. After two failed fixes resting on the same assumption, test the assumption. After three, stop the current loop, reconsider the design, and tell the user when it changes the plan. |
| Who reviews | A fresh reviewer after each task and at the end | A second opinion from another model; `interrogate` for adversarial review | The repository's review policy first; then an independent reviewer per [worker-contract.md](worker-contract.md#the-reviewer-brief), matched to the risk. Cross-model review is an addition when available, not a default requirement. |
| Run log | The execution ledger in `subagent-driven-development` | `show-me-your-work` decision trail | One authoritative decision record per task, in the task state ([execution-lifecycle.md](execution-lifecycle.md#decisions)). |
