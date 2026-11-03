# Integration playbook

Read this in integration mode: when the user asks to apply, adapt, or evaluate the project manager in one or more target repositories. [integration-contract.md](integration-contract.md) says when the integration counts as done.

## Contents

- [Objective](#objective)
- [Before you start](#before-you-start)
- [Phase 1: Audit](#phase-1-audit)
- [Phase 2: Design](#phase-2-design)
- [Phase 3: Implement](#phase-3-implement)
- [Phase 4: Verify](#phase-4-verify)
- [Phase 5: Evaluate end to end](#phase-5-evaluate-end-to-end)
- [Phase 6: Hand back](#phase-6-hand-back)
- [Sub-agents](#sub-agents)

## Objective

After integration, the project manager can coordinate engineering work in each target repository using that repository's own workflows and capabilities first, with Superpowers and pstack only where the repository leaves a gap. The repository's conventions keep working, and no orchestration is duplicated.

Two design rules shape every integration:

- **The project manager stays generic.** Its own files are the same in every repository. What is specific to a repository (which of its skills covers which phase, its gates, its delivery rules) lives in that repository's own instructions or workflow docs, where [discovery](project-context-discovery.md) already looks. Do not fork the project manager's guides per repository.
- **Add only what is missing.** If a repository already states a rule or a workflow, the integration points to it; it does not restate it.

## Before you start

- Get the list of target repositories, and confirm each path exists and is readable. Report any you cannot reach, and continue with the rest.
- Note any guidance the user gave per repository, such as "prefer the project's own workflows" or "fill gaps with the defaults". It is input to the design, not a substitute for the audit.
- With several repositories, integrate one first as a pilot when the user agrees, and apply what it teaches to the others.

## Phase 1: Audit

For each repository, run [discovery](project-context-discovery.md) with integration as the purpose, so look across work types rather than for one request:

1. Project instructions and development conventions, at the root and in nested folders.
2. Existing skills, agents, scripts, MCP tools, and workflow tools, with the [roles](capability-mapping.md#roles) each can fill, its contract, and whether the agent can invoke it.
3. Issue, branch, commit, pull/merge request, CI, review, and delivery conventions.
4. Each finding sorted into the [instruction types](conflict-resolution.md#types-of-instruction).
5. Which workflows cover a whole lifecycle for some work type, and which capabilities cover single phases.
6. Missing, incompatible, or unavailable capabilities, including whether Superpowers and pstack are installed where the agent will run.

Change nothing during the audit.

**Output per repository:** a capability inventory, a map of existing workflows by work type, the constraints and approval gates, and the gaps and compatibility concerns.

## Phase 2: Design

For each repository, using [workflow-resolution.md](workflow-resolution.md) and [capability-mapping.md](capability-mapping.md):

1. For each common work type (bug fix, feature, refactor, migration, investigation), the expected mode: project-native, hybrid, or default, and why.
2. Where an existing workflow keeps ownership, and where a default provider becomes workflow owner.
3. The capability for each uncovered phase, from the repository first, then the default providers per [default-workflow.md](default-workflow.md#choose-the-workflow-owner), or an acknowledged gap.
4. How the project manager will be available there: installed for the user, or added to the repository's skills folder following its conventions. Ask the user which they want when the repository has no convention.
5. The changes needed: usually a short section in the repository's agent instructions that names the project manager and maps the repository's skills and gates to phases, plus any missing workflow guidance.
6. Acceptance criteria for this repository, drawn from [integration-contract.md](integration-contract.md#completion-criteria), and the scenarios that will test them.

Present the plan and wait for the user's approval when it would change workflow ownership, an approval gate, a protected rule, or delivery permissions. A plan that only adds a pointer and a phase map can proceed after you have shown it, unless the user asked to approve everything.

**Output per repository:** the integration plan, the decisions made and the ones left to the user.

## Phase 3: Implement

1. **Install or expose** the project manager at the location chosen in the design.
2. **Configure** the repository's entry-point instructions (such as `AGENTS.md` or `CLAUDE.md`) so an agent working on a relevant task is led to the project manager.
3. **Connect** the repository's workflows, capabilities, and approval gates: the short mapping and any missing lifecycle or routing guidance, in the repository's own instruction files and style.
4. **Check discovery**: a fresh agent session in the repository finds the project manager and can invoke it, or read and follow it where invocation is user-only. A skill sitting in a skills folder is not yet a skill an agent uses.

Throughout:

- Keep existing instructions and skill contracts intact. Never silently remove, override, or weaken a rule.
- Do not duplicate what an authoritative project file already says; link to it.
- Add or update evaluation scenarios for the repository if it keeps agent tests.

Keep repository changes scoped to the integration and make them on a branch, following the repository's commit conventions. For a user-level installation, follow the host environment's installation and backup conventions, confirm you are allowed to change configuration outside the repository before you do, and leave unrelated user-level configuration alone. Opening a pull request, merging, and deploying follow the [delivery boundary](integration-contract.md#delivery-boundary).

## Phase 4: Verify

Check, and record the evidence:

- The repository's instructions are still discoverable, and the new section is reachable from where an agent starts.
- Existing skills are still present and invocable as before.
- For each common work type, [workflow resolution](workflow-resolution.md) on the repository picks the mode the design expects.
- [Capability mapping](capability-mapping.md) picks the intended provider for each phase.
- Approval gates and protected rules are unchanged.
- Each work type has one workflow owner and one execution orchestrator.
- A fresh session in the repository discovers the project manager from the entry-point instructions.
- Links in the changed files resolve, and any frontmatter or config still parses.

## Phase 5: Evaluate end to end

Run the standard scenarios in the target repository, each as a fresh normal-mode session (a new agent or sub-agent started in that repository). Use the repository's own issues or realistic stand-ins, on a throwaway branch or copy, and never against production.

| Scenario | Passes when the agent |
|---|---|
| E1. A clear, small bug fix | Executes it directly without starting an orchestration workflow or brainstorming; reproduces, fixes, and verifies |
| E2. An ambiguous issue | Recognizes the ambiguity and asks or runs a design conversation; does not invent acceptance criteria |
| E3. A multi-component feature | Plans before building; delegates where it helps and the runtime supports it; keeps one workflow owner and one orchestrator |
| E4. An implementation that fails | Switches to debugging, finds the cause, fixes, and verifies again. A small failure can stay in direct execution; when the debugging grows past a trivial task, the agent moves it to a workflow and says so |
| E5. A review that requests changes | Reads the feedback, makes the changes, verifies, and asks for review again |
| E6. A blocked run (missing access, dependency, or approval) | Names the blocker and stops at it; does not bypass permissions or an approval gate, and does not attempt a blocked action such as a push to find out whether it is allowed |
| E7. Workflow fallback: a task that needs a plan and several steps, with pstack unavailable and Superpowers installed | Recognizes pstack is unavailable, gives the whole work package to Superpowers, runs the phases the task needs, keeps one orchestrator, and keeps the project's rules and gates. Evidence: the Superpowers skills were actually loaded or invoked, the plan was written where the project or skill expects it, execution and verification output exist, and the hand-back names the workflow used |

In every scenario, also check that the agent used the repository's skills where they fit and default providers only for gaps, did not duplicate orchestration, verified the acceptance criteria, and handed back accurately.

E1 and E4 are the usual checks of direct execution for trivial work, and E7 checks the switch from pstack to Superpowers.

Run every standard scenario that applies. When one does not apply, say why and use an equivalent where one exists: a repository with no pull/merge request process adapts E5 to its own review step; a runtime without sub-agents still tests E3's planning and how the agent states the delegation limit, but cannot test delegated execution.

### Evaluation isolation

Give each scenario its own working directory and branch, such as a separate worktree or copy. Keep everything the scenario produces (plans, logs, notes, temporary files) inside that workspace, unless the scenario deliberately tests an outside integration. Do not let a scenario write into the main checkout; skills that write to a fixed project folder, such as a notes or plans directory, will follow the path they are given, so start the session in the scenario's workspace.

After the evaluation:

- inspect the main checkout for unintended changes;
- identify the files and branches the scenarios created;
- clean up only what the evaluation created;
- leave the user's own changes untouched.

Check what an evaluation harness actually loads before trusting its results. Some harnesses isolate each run and load only the skill under test, without the repository's own skills or the default providers; a scenario run that way does not test the integration.

Record each scenario's status as defined in [integration-contract.md](integration-contract.md#evaluation-status):

- **Blocked** when it cannot run because of a missing access permission, dependency, or required approval.
- **Not run** when it was not attempted, or when the evaluation environment could not test the intended integration, such as a harness that does not load the repository's instructions and capabilities.

A scenario that could not test its intended behavior is never passed. If a required scenario remains blocked or unverified, do not report the integration as done.

## Phase 6: Hand back

Report each repository separately, per [integration-contract.md](integration-contract.md#hand-back): the mode per work type and why, files added or changed, what was preserved, what was supplemented, each scenario's status with evidence, known limitations and gaps, decisions the user must make, and the integration status.

## Sub-agents

Audits of different repositories, independent edits, and evaluation scenarios are natural units to delegate, when the runtime supports sub-agents. Use the runtime's own mechanism and the brief in [capability-mapping.md](capability-mapping.md#subagents). If there is no sub-agent support, do the work in sequence and say so. Never report work as delegated that was not.

The current agent stays the workflow owner and execution orchestrator of the integration. It consolidates sub-agent findings, checks them against the repository rather than trusting a summary, resolves conflicts between delegated changes, and runs the final verification itself.
