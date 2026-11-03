# Conflict resolution

Read this when two instructions point different ways, or before combining project instructions with a default workflow in hybrid mode. This guide settles authority, applicability, ownership, and conflicts. It does not design a workflow; engineering method stays with the project's workflow, Superpowers, or pstack.

## Contents

- [Types of instruction](#types-of-instruction)
- [Precedence](#precedence)
- [When both cannot hold](#when-both-cannot-hold)
- [One execution orchestrator per work package](#one-execution-orchestrator-per-work-package)
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

A real conflict is two applicable instructions that cannot both hold, such as a project rule "work on a branch, no worktrees" against the default workflow's `using-git-worktrees`.

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
- **Direct conflict only.** A higher-ranked instruction overrides a lower one only where they directly conflict. Compatible instructions all stay in force and are combined: the project's review rule and the default workflow's verification step both apply.

A user request does not automatically override a project restriction. When the user's authority or intent is unclear, ask before any action that bypasses a protected branch, a production safeguard, a security control, or a required human approval. "Just push it" from someone who may not know main is protected is a question, not an authorization.

## When both cannot hold

First check whether precedence and applicability settle it.

- **Resolvable.** The higher-ranked instruction is clear: follow it, and record both sources and the resolution. The project forbids worktrees and the default workflow uses them, so work on a branch and note that `using-git-worktrees` was skipped because of the project rule.
- **Unresolved.** Authority, scope, or intent is unclear: pause the affected activity and ask the user.
- **Safety-critical.** The conflict involves data safety, security, production, or an irreversible action: do not proceed without the required authorization, however the ranking looks.

Then decide what it blocks. A conflict usually blocks only the activities that depend on it. If the project requires approval before a schema change and the user asks to ship now, the migration waits, but tests, code that does not depend on the new schema, and documentation can go ahead. Keep working on what is independent.

Record:

- the conflicting instructions and their sources;
- why they cannot both be satisfied;
- the precedence or the uncertainty involved;
- the decision and who made it, or the open question;
- which activities are paused, and which continue.

## One execution orchestrator per work package

Each work package has exactly one execution orchestrator, designated by its single workflow owner; often the same skill fills both roles. The roles are defined in [capability-mapping.md](capability-mapping.md#roles).

The orchestrator may use several agents, methodologies, and specialized capabilities. Those are capability providers, and do not become orchestrators unless they take over the same delegation and completion loop. Human approvers stay separate from the orchestrator. For example, in a feature built under Superpowers `subagent-driven-development`, implementer agents follow test-driven development with a project skill, a fresh reviewer agent checks each task, and a code owner, as human approver, approves the PR. That is many participants and one orchestrator.

When ownership changes, for example a plan grows into a program and moves to pstack Orchestrate, record the handover, the reason, the remaining scope, and the new orchestrator's responsibilities.

## Where Superpowers and pstack differ

Under the one-workflow-owner rule, a run normally follows one provider's workflow, and that provider's policy governs. These differences matter when one provider supplies a capability inside the other's path, or when a hybrid fills gaps around project gates. The project's rules and the user's preference come first in every row.

| Question | Superpowers | pstack | How to handle it |
|---|---|---|---|
| When to ask the user | `brainstorming` gates building on approval of the design; `writing-plans` asks for review and an execution method | `principle-never-block-on-the-human`: proceed on reversible work; pause for irreversible actions | Keep every approval gate of the workflow owner and the project. Do not ask again about a decision already approved. Do not widen scope without asking. A decision beyond the agent's authority, or with high risk, still needs approval. |
| Test first | `test-driven-development`: a failing test first, exceptions only with the user's permission | `tdd`: test first when there is a cheap local test target | Start from a failing test, or another reproducible check that actually demonstrates the failure, when the workflow owner's method requires it and a meaningful check can be built. A read-only question needs none; a docs change may have no test target; a performance change starts from a baseline instead. |
| Fixes keep failing | `systematic-debugging`: after three failed fixes, question the architecture | `principle-attack-the-premise`: after two that share a premise, test the premise | These are heuristics, not retry quotas. After two failed fixes resting on the same assumption, test the assumption. After three, stop the current loop, reconsider the design, and tell the user when it changes the plan. |
| Who reviews | A fresh reviewer after each task and at the end | A second opinion from another model; `interrogate` for adversarial review | Follow the project's review policy first, then the workflow owner's. With neither, pick an independent reviewer that fits the risk. Cross-model review is an addition when available, not a default requirement. |
| Run log | The execution ledger in `subagent-driven-development` | `show-me-your-work` decision trail | Keep one authoritative decision trail per run. Reuse the orchestrator's ledger when it meets [handoff-contract.md](handoff-contract.md#decision-trail); otherwise use `show-me-your-work` or a record the project already keeps. |
