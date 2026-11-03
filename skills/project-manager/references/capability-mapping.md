# Capability mapping

Read this at stage 3 to decide who or what carries out each phase, and at stage 4 when invoking a capability or when one is unavailable. The workflow is already chosen ([workflow-resolution.md](workflow-resolution.md)) and, in default or hybrid mode, so is the workflow owner ([default-workflow.md](default-workflow.md#choose-the-workflow-owner)). This guide fills in each phase.

## Contents

- [Roles](#roles)
- [Where to look first](#where-to-look-first)
- [Matching a phase to a capability](#matching-a-phase-to-a-capability)
- [The phase map](#the-phase-map)
- [Invoking a capability](#invoking-a-capability)
- [When a capability is unavailable](#when-a-capability-is-unavailable)

## Roles

This is the single definition of the roles; the other guides refer here.

| Role | Responsible for | Examples |
|---|---|---|
| Workflow owner | The workflow: its phases, their order, and their gates. It designates the execution orchestrator. | Superpowers, a pstack playbook, the project's workflow |
| Execution orchestrator | Splitting the work into tasks, delegating, coordinating, and completing it | `subagent-driven-development`, the pstack Feature playbook, the current agent on small work |
| Capability provider | Supplying a **method** (how an activity is done, such as test-first development) or a **specialized capability** (a skill, agent, script, or tool that performs an activity, such as a `schema-change` skill, `blast-radius`, or `make check`) | `test-driven-development`, `schema-change`, `blast-radius` |
| Human approver | The decision or authorization an approval gate requires | A tech lead, a code owner, the user when the decision is theirs to make |

A method and a specialized capability are different things supplied by the same role: a method says how, a capability does it.

The **user** is the person who made the request. The user is a human approver only for decisions within their authority; an approval gate that names someone else, such as a code owner's review, is not satisfied by the user's go-ahead.

One skill can fill more than one role, and often the workflow owner and the orchestrator are the same skill. A work package still has exactly one of each, plus any number of capability providers and approvers. In a migration, the pstack Feature playbook may own the workflow and orchestrate, Superpowers `test-driven-development` supply the test method, `schema-change` check the migration conventions, `make migrate-check` run the automated check, and the tech lead approve the plan. That is many participants and one orchestrator.

An approval gate is a requirement; the human approver is the person who meets it. Record the approver separately from any capability that supports the phase.

## Where to look first

For each phase, resolve three things: the action it requires, the role responsible for it, and the capability that performs it. Take them from these sources, in order:

1. **The project workflow and mandatory project instructions.** Follow the steps, tools, and approval gates they prescribe. Keep the kinds apart: "run `make migrate-check` before merging" is a working rule that names a command, "use the `schema-change` skill for migrations" is a rule that names a capability, and "the tech lead approves the plan" is an approval gate with a human approver. None of them is a workflow on its own.
2. **Project or user capabilities.** Prefer domain skills, project scripts, MCP tools, and capabilities the user asked for, found during discovery. A data project's `schema-change` or `query-review` skill knows things a general method does not.
3. **The default providers.** Superpowers and pstack per [default-workflow.md](default-workflow.md), where the project leaves the phase open. If the user named one of them, that preference holds as decided there, within the project rules and the harness's limits.
4. **The current agent's judgment.** Direct execution with no outside capability, when nothing suitable is available and the phase can proceed safely without one. Label it as the agent's own approach in the trail.

Using a capability does not show that a rule was met. Finding a `schema-change` skill does not satisfy the rule that every migration is backward compatible; check the rule on its own.

## Matching a phase to a capability

Before assigning a capability, name the [role](#roles) it would play. Then match on its documented behavior, not its name. A skill called `review` might review prose, not code. Before selecting one, check:

| Check | Question |
|---|---|
| Scope | Does it cover this activity and this work type? |
| Contract | What inputs, outputs, gates, and ordering does it require? |
| Availability | Is it installed, and can it be invoked or followed in this harness? |
| Compatibility | Does it fit the selected workflow, the project rules, the permissions, and the execution environment? |

A skill that spawns subagents in a harness with none, one that needs an MCP tool that is not connected, one that creates branches in a project that forbids it, or one that needs production access the agent does not have, fails this check however relevant its description sounds.

When more than one capability fits a phase:

- Prefer the one that most directly covers it.
- Combine capabilities only when their jobs complement each other. `make check` runs the suite; `verification-before-completion` requires evidence before claiming done. Two skills that run the same tests are redundant.
- Make sure the workflow owner allows the combination.
- Do not repeat an action that has already run and been verified.

Domain skills usually slot inside a phase rather than replacing it. The phase's orchestrator calls them, so the run still has one orchestrator.

## The phase map

Write the map into the trail before executing. Each phase names who is responsible for it, the capabilities with their role and how they are invoked, any approval gate and its human approver, the expected output, and the constraints. The format is free; this is one way (illustrative names):

```text
understand
  responsible: current agent
  capability: pstack how (specialized capability), manual read-and-follow, dispatching its explorer subagents as it specifies
  output: subsystem map with file references

plan
  responsible: current agent, with Superpowers as workflow owner
  capability: superpowers writing-plans (method), native
  approval gate: the plan is reviewed and an execution method chosen
  human approver: the user
  output: implementation plan

build
  orchestrator: superpowers subagent-driven-development, native
  capabilities: superpowers test-driven-development (method), native;
                project skill schema-change (specialized capability), native
  output: implementation, passing regression tests
  constraints: backward-compatible migration

verify
  responsible: current agent
  required check: make check (project rule)
  method: superpowers verification-before-completion
  output: command output from this session

review
  approval gate: code-owner review (project rule)
  human approver: the designated code owner
  mechanism: pull request review
  output: approval or requested changes
```

## Invoking a capability

"Installed", "invocable", and "executable here" are three different states. A skill can be installed but closed to model invocation, or invocable but dependent on subagents or tools this harness lacks. Check which state applies before planning around a capability.

### Native skill invocation

When the skill allows model invocation, use the runtime's mechanism, such as the Skill tool. Follow the skill's full instructions and keep its required handoff; do not work from a one-line summary of it.

### User-only skills

When a skill sets `disable-model-invocation: true`, do not call it through the Skill tool. Every pstack skill, including `poteto-mode`, `how`, and `interrogate`, is set this way.

- If the runtime offers a slash command and the skill's behavior depends on being run that way, ask the user to run it. pstack `poteto-mode`, for example, expects to run in the chat that received the command, which then owns the playbook, the todo list, and spawning the subagents.
- Otherwise, check whether the skill's complete instructions can be read and followed manually.

Manual read-and-follow is not native invocation, and the trail should say which one happened. Following means doing everything the skill asks, including the parts that depend on the runtime: pstack `how`, for example, dispatches read-only explorer subagents with a specific type and model. If the skill needs runtime behavior manual execution cannot reproduce, choose another capability or report a blocker. Do not run a reduced version and call it the skill.

### Subagents

A subagent does not inherit your conversation. Give it a focused brief:

- the goal and the expected result;
- its scope, and the files it may touch;
- the project rules and constraints that apply;
- relevant findings, evidence, and dependencies;
- the tests and acceptance criteria it must meet;
- what to return, and when to stop.

Respect the provider's delegation contract: the subagent type, model choice, isolation, and review cadence it specifies. pstack playbook delegates use its `poteto-agent` type, while `how` and `interrogate` set their own; Superpowers `subagent-driven-development` gives each task a fresh implementer with a review after every task and a final review.

### Scripts and MCP tools

Read the tool's documented inputs, permissions, and side effects before running it. Treat read-only and mutating operations differently, and do not take destructive or externally visible actions (deleting data, deploying, posting to shared channels, pushing to shared branches) without the authorization the project or the user requires. Keep the relevant output as verification evidence, with secrets and sensitive data redacted.

## When a capability is unavailable

Unavailable covers both missing (not installed) and installed but not usable here (user-only with no way to run it, or missing a subagent, tool, model, or permission it needs). Work through it before involving the user:

1. **Is it required?** Determine whether the selected workflow or a project rule requires this capability, or whether it was only the default choice.
2. **Is there an alternative?** Look for an installed capability that serves the same purpose without breaking the original contract.
3. **What does going without it cost?**
   - For an optional, low-risk activity, use a plain approach if the workflow permits it, and label it as the agent's own judgment.
   - For a required project action or an important gate, do not skip it silently or imitate the missing capability.
4. **Tell the user when it blocks the work**: what is missing, which phase depends on it, why the alternatives fall short, and how to make it available (for example `/plugin install superpowers@claude-plugins-official` in Claude Code, or `npx skills add backnotprop/pstack`).
5. **Never rebuild a missing skill from memory** and present the result as that skill. A remembered summary drops the gates and checks that make the skill worth using.
6. **Record** the alternative, fallback, or blocker in the trail.

| Situation | What to do |
|---|---|
| No review skill, but the project has a review script | Use the script, and record it |
| No `brainstorming`, and the request is a typo fix | Skip the phase; nothing to install |
| A migration skill the project requires is missing | Report a blocker, or ask for a suitable capability |
| No verification capability for an important change | Do not claim it is verified; find a trustworthy alternative or stop |
| pstack is missing, and Superpowers covers the work | Use Superpowers; do not ask for pstack |
