# Default workflow

Read this at stage 3 when the mode is default or hybrid, to compose the run from Superpowers and pstack. In hybrid mode, use it only for the phases the project leaves open.

This is a composition policy: how to pick one workflow owner, add capabilities under it, and keep each provider's contract. It does not restate the providers. Superpowers ([obra/superpowers](https://github.com/obra/superpowers)) and pstack ([cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack)) each describe their own steps; open the installed skill and follow it. Names and steps change between versions, so the installed copy wins over anything quoted here.

## Contents

- [Classify the work](#classify-the-work)
- [Phases by work type](#phases-by-work-type)
- [Who supplies each activity](#who-supplies-each-activity)
- [Choose the workflow owner](#choose-the-workflow-owner)

## Classify the work

Confirm or revise the rough call from discovery, on both dimensions: work type, and work scope.

| Work type | Signs | Notes |
|---|---|---|
| Read-only investigation | "How does X work", "why is Y like this", "should we do X or Y" | Produces an answer, not a change |
| Bug fix | A reported defect, a failing check, wrong output | The report states the intent; it rarely needs brainstorming |
| Feature | New or changed behavior | Intent needs confirming unless the request already settles it |
| Refactor | Structure changes, behavior must not | Pin current behavior before moving anything |
| Migration | A schema or data change that running code depends on | Follow the project's compatibility and rollback rules; often cross-cutting |
| Spike or prototype | Trying an approach, testing a hypothesis, settling an open design choice | A bounded, throwaway experiment; the production process does not apply to it |
| Performance improvement | One measured slowness or symptom to fix | A one-off: baseline, investigate, a measured fix |
| Sustained metric optimization | Repeated improvement toward a defined metric target | Baselines, iterative hypotheses, before-and-after measurements, and a trail entry for each accepted improvement |

| Work scope | Signs | Notes |
|---|---|---|
| Bounded | One contained piece of work | One work package |
| Cross-cutting | Several components or systems, many call sites | Usually more than one work package |
| Multi-work-package | Several independently executable units, days of work, a stack of PRs | The plan is its own deliverable, then orchestration |

This covers common engineering work. Specialized requests, such as runtime forensics, trace analysis, visual parity, skill authoring, evaluation, PR maintenance, shipping, or session recovery, can route straight to the matching provider playbook when one applies.

Record the type, scope, and reason in the trail. If the work turns out to be bigger, step up and say so ([workflow-resolution.md](workflow-resolution.md#when-the-request-changes)).

## Phases by work type

These are the usual phases. How each one is done (test-first policy, review style, who delegates) comes from the workflow owner, not from this table. Skip a phase that does not apply, with a one-line reason.

| Work type | Usual phases |
|---|---|
| Read-only investigation | Understand, gather evidence, answer. No branch, worktree, or implementation test loop. |
| Bug fix | Reproduce, investigate the root cause, establish failing evidence, fix, verify on the same surface, review, finish |
| Feature | Understand, explore approaches, design approval when required, plan when the work is multi-step, isolate when useful, implement, verify, review, finish |
| Refactor | Pin current behavior, define the target shape, change in small steps, prove behavior unchanged, review, finish |
| Migration | Understand the current schema and its readers and writers, plan steps that keep running code working, rehearse where the project allows, apply, verify the data, review, finish |
| Spike or prototype | Define the question, build the smallest useful experiment, observe, record what was learned |
| Performance improvement | Establish a baseline, investigate, form hypotheses, make a measured change, benchmark, verify, review |
| Sustained metric optimization | Set the target and baseline, define hypotheses, iterate measured changes, keep the accepted improvements, track progress toward the target |

Scope changes how the phases are organized, not which ones run:

| Work scope | How it changes the run |
|---|---|
| Bounded | The phases above, as one work package with one workflow owner |
| Cross-cutting | Understand and design across the areas touched, then split into verifiable work packages, give each a workflow owner, execute, and integrate |
| Multi-work-package | Understand, produce an approved multi-phase plan, orchestrate execution, verify each milestone and the final acceptance |

**Planning.** Plan when the work has several steps, non-obvious ordering, dependencies, or tasks that can be verified on their own, not by counting files. One file holding a tricky state machine may need a plan; ten generated files from one mechanical change may not.

**Design approval.** Superpowers `brainstorming` lets a request that already says everything that matters go straight to the work, and treats an agreed spike as outside its gate. A fully specified feature does not need a long design conversation.

**Failing evidence.** The workflow owner sets the test-first policy. Superpowers `systematic-debugging` wants a failing test case before the fix, automated where possible and a one-off reproduction script where there is no framework, written with `test-driven-development`. The pstack Bug fix playbook reproduces on the real surface and uses the `tdd` cadence when there is a cheap local test path, skipping the local test when it would be expensive or unsuitable. The same applies to "implement" in a feature: test-first is the workflow owner's method, not a step this table adds. Where the method calls for it, the check must actually demonstrate the failure, and some work has none to build: a read-only question needs no check, a docs change may have no test target, and a performance change starts from a baseline instead.

**Learning.** A short retrospective, or pstack `reflect`, is worth adding after a run that surprised you, not after every run.

## Who supplies each activity

This table shows what each provider has. It is not a menu to mix row by row: pick the workflow owner first, per [Choose the workflow owner](#choose-the-workflow-owner), and take a capability from the other provider only where the workflow owner leaves room for it.

| Activity | Superpowers | pstack |
|---|---|---|
| Understand the request | `brainstorming` | `how` for structure, `why` for history |
| Explore the design | `brainstorming` (approaches, and sizing the work) | `architect`, with `with checkpoint` when the design must be approved before code; `arena` for independent alternatives |
| Plan | `writing-plans` | The Multi-phase plan playbook in `poteto-mode`, for work spanning phases or PRs. pstack has no separate planning skill. |
| Isolate the work | `using-git-worktrees` | No separate skill. Its playbooks work from a git worktree (Opening a PR), Orchestrate runs workers in cloud environments, and the Worktree cleanup playbook prunes old worktrees. |
| Implement | `test-driven-development`, with `subagent-driven-development` or `executing-plans` | `poteto-mode` playbooks: Feature, Bug fix, Refactoring, Perf issue, Prototype; `tdd` |
| Debug and diagnose | `systematic-debugging` | Bug fix playbook with `how` and `why`; Runtime forensics and Trace forensics for a diagnosis without a fix; `principle-attack-the-premise` |
| Measure | | Perf issue playbook for a one-off fix; Hillclimb playbook for sustained optimization of one metric; `benchmark-checklist` for vetting numbers |
| Verify | `verification-before-completion` | `principle-prove-it-works`; `blast-radius` |
| Review | `requesting-code-review`, `receiving-code-review` | `interrogate` for an adversarial, multi-model review of a change or design; it reports findings and does not apply fixes |
| Open a PR | `finishing-a-development-branch` (merge, PR, keep, or discard) | Opening a PR playbook |
| Drive a PR to merge-ready | | Babysit playbook: clears checks and review threads, stops at merge-ready, does not merge |
| Verify and land | | Shipping playbook: an independent verdict per PR, then lands the verified run |
| No bundled playbook fits, or the work is large, cross-cutting, or needs a bespoke auditable plan | | `figure-it-out` designs a bespoke, auditable playbook for that run, even when a narrower playbook such as Feature would fit |
| Standing program | | Orchestrate playbook, for multi-day work across many PRs |
| Decision trail | | `show-me-your-work`, for long-running, unattended, or multi-phase work. For a small task, the decisions in the hand-back are enough. |
| Learn | | `reflect` |

**`architect` implements by default.** It grounds, sketches, and then goes straight into implementation; its agreement phase runs only when the invoker asks for a checkpoint. When the run needs a gate between design and implementation, invoke it with a checkpoint. Do not assume that calling a design capability stops before code is written.

## Choose the workflow owner

Superpowers and pstack each contain an end-to-end workflow with its own orchestrator. Splicing their steps looks reasonable and breaks both. For example, `brainstorming` → `writing-plans` → pstack Feature playbook → `subagent-driven-development` skips the execution choice `writing-plans` requires and puts two orchestrators on one work package. So choose one workflow owner per work package, then add capabilities inside it. The roles are defined in [capability-mapping.md](capability-mapping.md#roles).

### Two execution paths

**pstack owns the path.**

| Role | Who |
|---|---|
| Workflow owner | pstack `poteto-mode`, through the playbook it selects (for example Feature) |
| Execution orchestrator | That playbook |
| Capability provider (method) | Superpowers skills the selected playbook explicitly permits and that are compatible with its execution contract |
| Implementation and review | The subagents the playbook spawns |

Do not layer Superpowers `systematic-debugging` onto a pstack Bug fix path automatically. Each has its own debugging and test-first policy, and they differ on when a local failing test may be skipped. If `systematic-debugging` is required, choose the Superpowers path instead.

**Superpowers owns the path.**

| Role | Who |
|---|---|
| Workflow owner | Superpowers, starting from `brainstorming` for a feature, or `systematic-debugging` for a bug |
| Bounded bug fix | The current agent, following `systematic-debugging`, `test-driven-development`, and `verification-before-completion`, then code review and `finishing-a-development-branch`. No delegation loop. |
| Planned multi-task implementation | `writing-plans`, then `subagent-driven-development` or `executing-plans` as chosen at its handoff |
| Capability provider (specialized capability) | pstack skills that run as a bounded step, such as `how` to map a subsystem or `blast-radius` before finishing |
| Implementation and review | The current agent, or the subagents the chosen orchestrator spawns |

Not every Superpowers path needs `subagent-driven-development` or `executing-plans`; they come in only when there is a plan of several tasks. Never run both paths on the same work package.

**Read-only investigation** has no Superpowers equivalent of the pstack Investigation playbook. If pstack is installed, hand the question to `poteto-mode`, which picks Investigation. Otherwise the current agent answers it directly, under the project's rules, with its evidence. Do not run `brainstorming` to answer a question about the codebase.

### Choose the path

Resolve the workflow owner in this order:

1. **Honor an explicit preference.** If the user names a workflow, a provider, or an execution method, use it, provided it is compatible with the project rules and the harness. A subagent-driven choice in a harness with no subagents, or a project that forbids agents from creating branches or commits, changes what can run; say so and pick the nearest option that fits.
2. **Keep a gate that is already in play.** If the chosen workflow owner has a planning or approval gate, such as `writing-plans` asking for an execution method, keep that provider's handoff and let the user make the choice it asks for.
3. **Execute trivial work directly.** For a trivial, well-scoped task, the current agent executes it under the project's rules, with no workflow orchestration: a typo, a one-file mechanical change, or a small fix with a clear reproduction and no need for further orchestration. A clear reproduction alone does not make a fix trivial; it is trivial when it also needs no design decision, no plan of several steps, no delegation, and no more than one review round. Direct execution keeps every rule that applies to the task (test-first where the project requires it, its tests, review, and verification before calling it done), never skips an approval gate, and still plans a task that turns out to need a plan. If the task grows while you work on it, move it to the workflow it now needs, per [workflow-resolution.md](workflow-resolution.md#when-the-request-changes), and say so.
4. **Otherwise compare the end-to-end workflows.** Weigh how independent the tasks are, how fine-grained review needs to be, whether delegation is supported, harness compatibility, cost, and what a defect would cost. Neither provider is the "strict" one; pstack Bug fix has its own delegation and runtime verification, and the difference is how each organizes execution. Choose **pstack** when a bundled playbook closely fits the work and its execution contract is supported here.
5. **Choose Superpowers** when its design, planning, and per-task execution fit the work better, for example an approved design and plan whose tasks are independent and where fresh per-task implementation and review justify the overhead, or when pstack cannot own the work package for one of the reasons in [capability-mapping.md](capability-mapping.md#switching-from-pstack-to-superpowers).
6. **Fall back or report.** If a required provider is unavailable, use a compatible alternative per [capability-mapping.md](capability-mapping.md#when-a-capability-is-unavailable), or report a blocker.

Do not invoke a workflow only to satisfy a rule about using tools. Whatever owns the work must add real coverage for this task: a plan where ordering matters, delegation where tasks are independent, review where a defect is costly. A project that wants every task to go through one provider says so in its own instructions, and that rule then applies as a project rule.

### The router and poteto-mode work at different levels

This skill and pstack `poteto-mode` both route, but not the same question. This skill decides at the project level: whether the project's own workflow applies, whether the mode is hybrid, which work packages exist, and who owns each. `poteto-mode` decides at the work-package level: which playbook fits, whether it needs `figure-it-out` or Orchestrate, how to use subagents.

So when pstack owns a work package, hand it to `poteto-mode` with a clear scope and the constraints from discovery (the project rules, the phases already done, the gates that still apply), and let it choose the playbook. Then open that playbook and follow it as written. `poteto-mode` has the playbook's steps copied verbatim into the todo list; do not summarize them or drop steps. If its choice disagrees with your classification, take that as new information and revisit [workflow-resolution.md](workflow-resolution.md#when-the-request-changes) rather than overriding it.

### Child work packages

A workflow owner may hand a bounded piece of work to another orchestrator, for example a Superpowers-owned feature that sends one independent data backfill to a pstack playbook. The child needs a clear scope, its own single workflow owner, and a defined result to hand back. The parent waits for that result and does not run its own loop over the same files.
