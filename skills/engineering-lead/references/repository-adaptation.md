# Repository adaptation

Read this before the first workers are briefed in a repository, and again when its configuration changes. It turns what [discovery](project-context-discovery.md) finds into a capability map. For each need of the task, the map says which capability serves it, how that capability is used, and who uses it. Repository files stay the source of truth; the map is a working summary of them.

## Contents

- [What to inventory](#what-to-inventory)
- [Repository policy and the decision for this task](#repository-policy-and-the-decision-for-this-task)
- [Invocation modes](#invocation-modes)
- [Selecting capabilities](#selecting-capabilities)
- [Methods from Superpowers and pstack](#methods-from-superpowers-and-pstack)
- [Capabilities for external actions](#capabilities-for-external-actions)
- [When a capability is unavailable](#when-a-capability-is-unavailable)
- [The capability map and its refresh](#the-capability-map-and-its-refresh)

## What to inventory

Discovery covers how to find and evaluate these. Here, record what each one gives the main session, the coder, and the reviewer:

- mandatory instructions (`AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, nested equivalents) and the rules and gates in them;
- agent definitions the repository ships (for example `.claude/agents/`), with what each is for;
- skills, with whether each can be invoked as a tool;
- tools and MCP integrations;
- workflows the repository documents, by work type;
- test, lint, build, and CI commands;
- branch, commit, PR, and merge conventions;
- security, approval, and deployment gates, and who approves.

Do not assume any of these exist. "None found" is a finding.

## Repository policy and the decision for this task

A repository's instructions may already say which workflow each work type follows, which gates apply, and how work is delivered. That is policy. The main session applies it to the task in front of it and decides what the policy leaves open:

- whether the task really is that work type once the code is read (a "bug fix" that changes a schema is a migration);
- which contracts and gates this task touches;
- whether it needs a coder and a reviewer, or is small enough for the main session alone;
- which capabilities the coder and reviewer use, and whether they can run right now;
- the Git state, and what is already in flight;
- what stays local, and what needs authorization.

A repository workflow fits a task when it answers five questions for that work type: where the work starts, which phases it goes through, what moves it from one phase to the next, who does each, and how it is confirmed done. When it answers them, keep its phases and gates inside the main session's workflow. When it answers some, keep those parts and take the rest from the [methods](#methods-from-superpowers-and-pstack). When the repository has only working rules (use pytest, never commit to main), it has constraints but no process: the main session supplies the process and obeys every rule. Working rules, workflows, approval gates, methods, and capabilities are different things; a capability for a phase does not show that the phase's rules were met.

## Invocation modes

Classify each capability before relying on it, and report the mode that was actually used. Do not say a skill was invoked when it was read and followed.

| Mode | When | How |
|---|---|---|
| Direct invocation | The runtime lets the skill or tool be called | The skill mechanism (such as the Skill tool), the MCP tool, or the script |
| Read and follow | The skill sets `disable-model-invocation: true` and works without its slash command | Open the skill's file and follow all of it, including the parts that depend on the runtime. If they cannot be reproduced, choose another capability; do not run a reduced version under its name |
| Agent assignment | A worker should use the skill | The brief gives the skill's path and says to read it first and follow it |
| Workflow reference | A repository document defines the process | Follow the document; its gates are policy |
| Started by a slash command | The skill must own the chat that received its command, such as pstack `poteto-mode` | Only in a session where the command was typed. Under Herdr, the main session can start it in the coder's own session ([runtime-adapters.md](runtime-adapters.md)). Never ask the user to type it just to route work |
| Unavailable | Not installed, not exposed in this runtime, or missing something it needs | See [When a capability is unavailable](#when-a-capability-is-unavailable) |

Installed, discoverable, invocable, and executable are separate states. A skill in a folder may still be closed to invocation, or depend on a subagent type, tool, or model this runtime lacks.

## Selecting capabilities

Take capabilities from these sources, in order:

1. **The repository's workflow and mandatory instructions.** Use the steps, tools, and gates they prescribe.
2. **The repository's and the user's capabilities.** Domain skills, repository agents, scripts, MCP tools, and anything the user asked for. A repository's `schema-change` or `debug` skill knows things a general method does not. Do not replace a repository capability just because pstack or Superpowers has a similar one.
3. **pstack and Superpowers**, where the repository leaves a need open ([below](#methods-from-superpowers-and-pstack)).
4. **The main session's or the worker's own approach**, when nothing suitable exists and the need can be met safely without one. Say so.

| Need | Preferred |
|---|---|
| Implementation | The repository's coder agent; otherwise pstack `poteto-mode` in the coder session (Herdr), or a `poteto-agent` or general-purpose worker following poteto-mode's principles (native) |
| Debugging | The repository's debug skill or agent; otherwise `principle-fix-root-causes` or Superpowers `systematic-debugging`, one per assignment |
| Testing | The repository's test commands and testing skills |
| Independent review | The repository's reviewer agent or review skill; otherwise a fresh reviewer in `poteto-mode` following pstack `interrogate`; Superpowers `requesting-code-review` only where pstack is not installed |
| Engineering method (design, plan, test-first) | The matching Superpowers or pstack method |

Match on documented behavior, not names: a skill called `review` may review prose. Check scope (does it cover this need?), contract (inputs, outputs, gates, order), availability (can it run here?), and compatibility (does it fit the repository's rules, the permissions, the runtime?). Combine capabilities only when their jobs complement each other; two skills that run the same tests are redundant. Do not run every available skill.

## Methods from Superpowers and pstack

They are methods the main session and the workers follow, not workflow owners. The main session owns the issue; these supply how each piece is done.

| Need | Superpowers | pstack |
|---|---|---|
| Understand and clarify the request | `brainstorming` | `sharpen`; `how` for structure, `why` for history |
| Design | `brainstorming` (design approval gate) | `architect` (implements unless asked for a checkpoint); `arena` for independent alternatives |
| Plan | `writing-plans` | Multi-phase plan playbook inside `poteto-mode` |
| Implement | `test-driven-development`, `executing-plans` | `poteto-mode` playbooks (Feature, Bug fix, Refactoring, Perf issue, Prototype); `tdd` |
| Debug | `systematic-debugging` | Bug fix playbook; `principle-fix-root-causes`; `principle-attack-the-premise` |
| Measure | | Perf issue, Hillclimb; `benchmark-checklist` |
| Verify | `verification-before-completion` | `principle-prove-it-works`; `blast-radius` |
| Review | `requesting-code-review`, `receiving-code-review` | `interrogate` (findings only, no fixes) |
| Status and learning | | `ketchup`; `reflect` |

Keep each method's contract, with three rules for how they meet this skill:

- **`writing-plans` ends by asking how the plan should be executed.** The main session answers it: the coder executes it. That keeps the skill's handoff and does not ask the user a question the design already settles.
- **`poteto-mode` in the coder session routes to a playbook and may start its own subagents.** That is the coder's way of working inside its assignment, not a second issue owner. Its delivery playbooks (Opening a PR, Babysit, Shipping) and Superpowers `finishing-a-development-branch` are outside the coder's scope: the brief forbids push, PR, and merge, and delivery stays with the main session.
- **`architect` implements by default.** Where a design must be approved before code, ask for its checkpoint, or use `brainstorming`.

## Capabilities for external actions

When the task needs a Git or provider action, match a capability to that action. The repository's own capability comes first: a repository `pull-request` skill or release script beats a generic CLI. Look separately at Git transport read and write access, provider API authentication, and the permission for the operation. For the capability chosen, establish the provider and operations it supports, the channel it authenticates on, whether it can run here, and what evidence it gives of the result. A CLI on the path, a skill in a folder, or a credential helper is not proof the operation is permitted. Authorization and the preflight are in [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries) and [authentication-and-permissions.md](authentication-and-permissions.md).

## When a capability is unavailable

Work through it before involving the user:

1. **Is it required?** By a repository rule or the chosen method, or only a default choice?
2. **Is there an alternative** that serves the same purpose without breaking its contract? Where the repository documents a fallback, take it. Use the alternative yourself; do not ask the user to do the routing, such as starting an entry point by hand. A fallback changes how the work is done, not what it requires: rules, tests, review, and gates still apply.
3. **What does going without it cost?** For an optional, low-risk need, use a plain approach and say so. For a required action or an important gate, do not skip it or imitate the missing capability.
4. **Tell the user when it blocks the work:** what is missing, what depends on it, why the alternatives fall short, and how to make it available (for example `/plugin install superpowers@claude-plugins-official`, or `npx skills add backnotprop/pstack`).
5. **Never rebuild a missing skill from memory** and present it as that skill.
6. **Record** the alternative or the blocker.

| Situation | What to do |
|---|---|
| No `poteto-agent` definition (Codex, or Claude Code without pstack) | A general-purpose worker with the same coder contract, told which principles to follow |
| `poteto-mode` cannot be started in the coder session | The coder follows `tdd`, `principle-fix-root-causes`, and `principle-prove-it-works`, or Superpowers `test-driven-development` and `verification-before-completion` |
| No review skill, but the repository has a review script | Use the script |
| A migration skill the repository requires is missing | Report a blocker |
| No way to verify an important change | Do not claim it is verified |

## The capability map and its refresh

Keep the map short, in the context note or the task state:

```text
capability map: cdp-journey-engine @ 4f2c1ab
  instructions: AGENTS.md (workflow per work type, contracts first, stop and ask), CLAUDE.md -> AGENTS.md
  coder: poteto-mode in a Herdr session (read and follow its playbook); native: poteto-agent
  reviewer: fresh session following interrogate; verdict as a PR comment (pull-request skill)
  tests: ./event-processor/mvnw ... test, checkstyle; pnpm --filter studio test, lint
  delivery: pull-request skill (invoke, only when authorized); deploy skill (only on request)
  gates: contract changes need the user's decision; merge needs authorization
```

The values are illustrative. Reuse the map across tasks while it still matches the repository. On each new task, re-read the mandatory instructions and check the Git state ([discovery](project-context-discovery.md#later-runs)). Rediscover only what changed: a new or changed skill, agent definition, workflow, or rule changes the map even if nothing else does.
