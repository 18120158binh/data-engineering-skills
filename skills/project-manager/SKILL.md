---
name: project-manager
description: Coordinate software and data engineering work from request to verified delivery. Discover the project's instructions, working rules, existing workflows, and available capabilities before resolving an execution path. Prefer applicable project-native workflows; compose a hybrid workflow when project guidance covers only part of the work. When no suitable workflow exists, use Superpowers and pstack as default providers for engineering methodology, investigation, execution, and orchestration. Adapt the workflow to the request, preserve provider requirements, and maintain clear execution ownership. Use it for features, bug fixes, refactoring, migrations, investigations, and multi-step engineering changes, or in integration mode to apply, adapt, or evaluate the project manager itself in one or more repositories ("apply project-manager to this repo", "integrate the project manager into these projects").
metadata:
  version: "0.3"
---

# Project manager

Works as an engineering workflow router. For each request it works out which workflow to follow, why, who runs each phase, and how to tell the work is done. It does not have to do every phase itself. It picks the phases the request needs, the skill or person that owns each one, and keeps the run honest until the hand-back.

## Operating modes

Decide the mode first, from what the user asks for.

**Normal mode** is for engineering work: issues, bugs, features, refactoring, migrations, investigations, and multi-step changes. Follow the principles, routing, and steps below.

**Integration mode** is for adopting the project manager itself: when the user asks to install, apply, integrate, adapt, or evaluate it in one or more target repositories. It has its own lifecycle in [integration-playbook.md](references/integration-playbook.md), with completion criteria in [integration-contract.md](references/integration-contract.md); read both. In short:

1. Confirm which target repositories exist and are accessible.
2. Audit each one without changing it: instructions, working rules, workflows, approval gates, skills, agents, tools, and delivery conventions.
3. Design the integration for each repository, resolving its workflow mode and capability coverage independently. Do not assume repositories are alike.
4. Present the plan and wait for the user wherever it would change workflow ownership, protected rules, approval gates, or delivery permissions.
5. Integrate, preserving existing behavior and instructions.
6. Verify, run representative end-to-end scenarios, and hand back per repository.

Integration mode manages the adoption, so it does not run the normal lifecycle to orchestrate itself. Running normal-mode scenarios against a target repository during evaluation is testing, not orchestration. The current agent owns the integration as a whole: it may delegate bounded audits, edits, or evaluations to sub-agents when the runtime supports them, and keeps coordination, conflict resolution, verification, and the hand-back. Integration is not complete because files were copied; it is complete when the contract's criteria are met with evidence.

The principles below apply in both modes.

## Principles

### The project's established workflow comes first

Prefer an existing project workflow when it applies to this request and is consistent with higher-priority instructions. A workflow that is out of date, superseded, or written for another work type does not qualify just because it is in the repository. Keep its required steps, gates, and conventions, and bring in outside methods or capabilities only where it leaves a gap or explicitly allows them. **Why**: project workflows encode local engineering decisions, tooling, review practice, and operational constraints, and replacing them with a generic process produces work that does not fit the project. **The test**: which project workflow was selected, why does it fit this request, and which parts came from outside it?

### Working rules are context, not a workflow

A project with only rules (test with pytest, every schema change needs a migration, run the linter before committing) has context and constraints but no process for understanding, planning, building, and verifying. Take the process from the default workflow, and obey every rule inside it. **Why**: treating rules as a full workflow skips planning and verification, and treating the project as empty ignores its constraints. **The test**: which rules did discovery find, and where in the run was each applied?

### Use only what the request needs

Pick the phases and capabilities this request needs, not everything the guides list. A bug fix rarely needs brainstorming; a read-only question needs no worktree, no test-first loop, and no branch. A phase can be done by the current agent under the project's rules, with no outside skill, when that is enough. **Why**: every extra phase costs time and context, and invites ceremony that hides the actual work. **The test**: for each capability used, what would have gone wrong without it?

### One workflow owner per work package

Choose one workflow owner for each work package before composing capabilities. The workflow owner decides the workflow: its phases, their order, and their gates. It designates one execution orchestrator to delegate, coordinate, and complete the work; often one skill fills both roles, but they stay distinct. Capability providers supply methods or specialized capabilities where the workflow owner allows them, and human approvers make the decisions the gates require. [capability-mapping.md](references/capability-mapping.md#roles) defines the four roles. A workflow owner may hand a bounded child work package to another orchestrator, as long as the child has a clear scope and exactly one workflow owner of its own. Superpowers and pstack each contain end-to-end workflows, so a run usually takes one of them as workflow owner rather than splicing their steps together. **Why**: two workflows controlling the same work duplicate planning, delegation, review, and completion checks, and leave nobody accountable. **The test**: who is the workflow owner for this work package, who orchestrates execution, which providers only supply capabilities, and are any two workflows trying to control the same scope?

### Preserve provider contracts

When invoking an external skill or playbook, follow its required inputs, gates, outputs, and sequencing. Do not compose a workflow that skips a provider's hard requirement. For example, Superpowers `brainstorming` requires design approval before implementation and hands off to `writing-plans`, which asks the user to choose an execution method when none was given. If a contract does not fit the request, choose a different capability rather than running part of it. **Why**: a provider's gates are what make it worth using, and steps lifted out of order look reasonable but lose the checks that protect the work. **The test**: for each external skill used, were its gates and required order kept, or was it swapped out with a stated reason?

### Stop only at unresolved conflicts

When instructions conflict, first work out their authority, scope, and applicability with the precedence rules. Many differences are not conflicts at all: a project that requires pytest and a default workflow that requires test-first are both met by writing the failing test in pytest. When precedence gives a clear answer, apply it, record the ruling, and keep going. Stop at the decision point only when the conflict cannot be resolved safely or the resolution needs the user's judgment. Never silently discard a mandatory instruction. **Why**: not every difference is a blocker; clear precedence should keep work moving, while ambiguous or consequential conflicts need an explicit decision. **The test**: was each conflict resolved by a clear rule, or escalated with the competing sources and consequences recorded?

## Route the request

| Stage | What it settles | Read |
|---|---|---|
| 1. Discover the project | A first guess at the work type and scope; instructions, working rules, existing workflows, available capabilities | [project-context-discovery.md](references/project-context-discovery.md) |
| 2. Resolve the workflow | Project-native, hybrid, or default, and why | [workflow-resolution.md](references/workflow-resolution.md) |
| 3. Compose the run | The workflow owner, the phases, and who does each, from the resolved workflow | Project-native: the project's workflow. Hybrid: the project's workflow, plus [default-workflow.md](references/default-workflow.md) for the gaps only. Default: [default-workflow.md](references/default-workflow.md). For who does each phase: [capability-mapping.md](references/capability-mapping.md) |
| 4. Execute and coordinate | Invoking skills, delegating, tracking, unblocking | [capability-mapping.md](references/capability-mapping.md#invoking-a-capability), [conflict-resolution.md](references/conflict-resolution.md) when instructions disagree |
| 5. Verify and hand off | Evidence, review, results, what is left | [handoff-contract.md](references/handoff-contract.md) |

Some situations jump straight to a guide:

| When | Start by | Read |
|---|---|---|
| A required capability is unavailable | Checking alternatives, and whether the phase can proceed without it | [capability-mapping.md](references/capability-mapping.md#when-a-capability-is-unavailable) |
| Two instructions conflict | Resolving authority, scope, and precedence | [conflict-resolution.md](references/conflict-resolution.md) |
| A provider's contract does not fit the request, such as a design gate for a typo fix | Recomposing the run with another capability | [capability-mapping.md](references/capability-mapping.md) |
| The request changes scope or work type | Revisiting workflow resolution | [workflow-resolution.md](references/workflow-resolution.md#when-the-request-changes) |

## Steps

The stages run in this order, but they are not a script. A one-line question may finish in stages 1, 3, and 5 in a few minutes. Go back a stage whenever something you learn changes an earlier answer.

1. **Discover the smallest relevant context.** Start with a rough classification of the request on two dimensions: its work type (investigation, bug fix, feature, refactor, migration, spike, performance) and its scope (bounded, cross-cutting, or several work packages); later stages can revise it. Then read the instructions that apply to the files you will touch, at the root and in their folders, follow links to the workflow docs this work type needs, look at the existing code and tests, and find capabilities for the phases this request needs. Watch for docs that disagree with current practice, and treat practice as evidence, not as a rule. Do not read secret values. Do not scan unrelated docs or inventory every installed skill; widen only when the request or what you find calls for it. Keep a short context note. See [project-context-discovery.md](references/project-context-discovery.md).
2. **Resolve.** Check whether an applicable project workflow answers the five questions for this work type, then name the mode and the reason. See [workflow-resolution.md](references/workflow-resolution.md).
3. **Compose.** Build the run from the resolved workflow. Project-native: follow the project's phases and ownership. Hybrid: keep the project's parts and fill only the uncovered phases with default capabilities. Default: use the baseline in [default-workflow.md](references/default-workflow.md). Choose the workflow owner first, then add capabilities it allows. A phase may need no outside skill; the current agent can do it under the project's rules. See [capability-mapping.md](references/capability-mapping.md).
4. **Execute.** Run each phase through the role assigned to it, following each skill's own instructions and contract rather than a summary of them. Record decisions that materially affect scope, architecture, execution order, ownership, risk, or delivery, with their reason, source, and evidence; skip routine actions. Settle disagreements per [conflict-resolution.md](references/conflict-resolution.md).
5. **Verify and hand off.** Check each acceptance criterion and show evidence from this session, run the review the workflow calls for, and hand back per [handoff-contract.md](references/handoff-contract.md).

## Hand back

Report the workflow and why it was chosen, the workflow owner, the project rules applied, the capabilities used and how each was invoked, what was done, the decisions made, and what is still open. Map verification to the request's acceptance criteria: for each one, the check performed, its result and relevant output, whether it ran in this session, and any limitation; a passing command proves only what it tested. Give the result (done, partially done, or blocked) separately from each delivery step (implemented, verified, PR opened, approved, merged, deployed), and mark every step complete, not reached, not requested, or not applicable. [handoff-contract.md](references/handoff-contract.md) has the fields and the decision trail. Size the report by work type and risk; an investigation needs a few lines, a production migration needs the full contract.
