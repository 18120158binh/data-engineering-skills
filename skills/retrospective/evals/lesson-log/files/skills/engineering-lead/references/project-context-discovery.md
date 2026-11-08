# Project context discovery

Read this in phase 1, intake and triage, before choosing a workflow. Discovery works at two levels. For the repository, know how it is organized and how work is done in it: build that understanding once, then refresh only what has changed. For the request, gather the smallest context that lets you decide how to run it. Neither level is a survey of every file, and neither replaces the investigation the worker does before changing code. The checklist at the end is the short version.

Discovery collects and assesses context. [repository-adaptation.md](repository-adaptation.md) turns it into the capability map and decides how the repository's policy applies to the task.

## Contents

- [Know the repository, then keep it current](#know-the-repository-then-keep-it-current)
- [Classify the request first](#classify-the-request-first)
- [What to discover](#what-to-discover)
- [Where to discover](#where-to-discover)
- [How to evaluate what you find](#how-to-evaluate-what-you-find)
- [When to stop](#when-to-stop)
- [The context note](#the-context-note)
- [Checklist](#checklist)

## Know the repository, then keep it current

### The first time

When you have no baseline for this repository that you can check against its current state (nothing from earlier in this session, no context note or memory), build one before taking on the request. Keep it at overview level:

- the agent and contributor instructions and their mandatory constraints, at the root and in nested folders;
- the structure, the major components, and the dependencies between them;
- the workflows and conventions, by work type;
- the project's own skills, agents, scripts, and MCP tools, with what each can do for the coder or the reviewer ([repository-adaptation.md](repository-adaptation.md));
- ownership and approval gates;
- testing, CI, review, and delivery conventions.

Take it from the docs and the source, checked as described under [How to evaluate what you find](#how-to-evaluate-what-you-find). Do not read every implementation or study modules that do not affect how work is organized. In most repositories this means the instruction files, the README and contributing guide, the top-level layout, the skills folders, and the CI config. Check the Git state too, as on later runs. Record the overview in the context note with the commit it describes. The note is a working record for this run, kept in the trail or the hand-back; create a persistent file only where the repository has a place for one.

Do not assume you remember a repository. Without a baseline you can check, treat it as the first time. No marker or separate store is needed; the baseline is whatever earlier context you can verify.

### Later runs

Do not repeat the whole discovery. At the start of each run:

1. Read the current instructions and the workflow docs this work type needs. They may have changed since the baseline.
2. Check the Git state before changing anything, with commands whose output shows it (`git status`, the current branch, and its base): the branch, the base revision, uncommitted changes, and whether the base is the one the project works from. Do this on every run, even when nothing else needs rediscovering.
3. Look at what changed since the baseline in instructions, skills, workflows, ownership, gates, and architecture, for example with `git log --stat <baseline>..HEAD` on those paths. Compare the skills folders with the capabilities the baseline lists. A skill that is new or changed, and covers a phase this task needs, changes the capability map even when the instructions do not mention it.
4. Reuse the baseline only where it still matches the repository.

Rediscover the areas that changed before choosing a workflow or a capability: a new skill goes into the capability list, a changed rule replaces the old one. When much has changed, or the baseline no longer fits what you see, redo the affected parts of the first-time discovery.

Git state also feeds a separate decision: whether to isolate the work in a branch or worktree. The main session decides it from the project's rules ([runtime-adapters.md](runtime-adapters.md#workspace-for-the-task)); it is execution setup, not discovery. A read-only question needs no isolation, work that continues an existing branch stays on it, and some projects forbid worktrees.

### Task-specific investigation belongs to the worker

Repository understanding is for coordinating the work. Before planning or changing code, whoever executes the work package investigates the code, dependencies, data flows, and constraints the task touches, using the project's own skills first and default capabilities after. Do not run a second investigation over ground assigned to the worker. Check instead that its investigation covers the task and that the resulting approach meets the project's rules and the acceptance criteria. When the current agent executes directly, it does both.

## Classify the request first

Make a rough call before searching, because it decides which workflow to look for and which docs are worth opening. Do not analyze deeply; later stages can revise it. Classify along two dimensions, because the work type and the scope are different questions: a bug fix can also need a migration and touch several services.

**Work type**: what kind of engineering activity is requested.

| Work type | Look especially for |
|---|---|
| Read-only investigation | The code itself, architecture docs, ADRs. Workflow docs matter little. |
| Bug fix | A bug, incident, or hotfix process; how to reproduce (test commands, fixtures, logs) |
| Feature | A feature or RFC process, design doc templates, review and release rules |
| Refactor | Rules about behavior-preserving changes, coverage expectations |
| Migration | Schema or data migration rules, backward-compatibility policy, deploy order, rollback |
| Spike or prototype | Whether the project has a place or rule for throwaway experiments; usually little else |
| Performance improvement | Benchmarks, profiling tools, performance budgets, how numbers are recorded |
| Sustained metric optimization | The metric's definition and target, how it is measured, where results are recorded |

**Work scope**: how broadly the change spans components, systems, or separately executable units.

| Work scope | What it means | Look especially for |
|---|---|---|
| Bounded | One contained piece of work | Only the rules and docs on the path of the files touched |
| Cross-cutting | Spans several components or systems | The rules for each area touched, ownership (CODEOWNERS), release coordination |
| Multi-work-package | Several independently executable units, possibly across several PRs | Planning, stacking, and release conventions; who can approve a plan |

A request can have more than one work type, and you will often only guess its scope until you read the code. Record both, with what you are unsure of.

## What to discover

Four kinds of context, each only as far as this request needs:

| Kind | What it is | Example |
|---|---|---|
| Project instructions | What the project tells agents and contributors to do | "Agents work on a branch and stop before opening a PR" |
| Working rules | Constraints the work must meet | Test runner, lint, branch naming, migration policy, review requirements |
| Workflows | A process from request to done for some work type: where to start, the phases, what moves work between them, who does each, how done is confirmed | A documented feature process with proposal, approval, build, review |
| Capabilities | Who or what can do the phases this request needs | Skills, agents, MCP tools, project scripts, the current agent itself |

Also note **evidence of actual practice**: what the code, tests, CI, and recent history show the project really does. Use it to understand the project and to check the docs, not as a source of rules; see [Practice is evidence, not authority](#practice-is-evidence-not-authority).

## Where to discover

Work outward from the files the request touches.

1. **Instructions on the path.** Read `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/`, and similar files at the repository root and in every folder between the root and the files you will change. A change in `services/payment/` is bound by the root file and by `services/payment/AGENTS.md`. A nested instruction applies within its folder and may add more specific requirements. If it appears to override a parent instruction, such as a root rule that every migration is backward compatible against a nested note allowing direct schema replacement, settle it with the project's precedence rules per [conflict-resolution.md](conflict-resolution.md); do not assume the nearest file wins.
2. **Linked workflow docs.** Follow links from those instructions, and from `CONTRIBUTING.md` and `README.md`, to the docs for this work type. Skip docs for other types: a fix to one endpoint does not need the deployment, analytics, or release-management docs unless the instructions send you there.
3. **The code and its tests.** Read the implementation you will change and the tests around it, enough to classify and route the work. They show conventions the docs may not mention. The deeper investigation is the worker's, per [Task-specific investigation belongs to the worker](#task-specific-investigation-belongs-to-the-worker).
4. **Practice signals.** CI config, `pyproject.toml`, `package.json`, `Makefile` or task-runner targets, PR templates, and `git log` for the files involved. Read the parts that relate to this request.
5. **Capabilities for the needed phases.** Look where the current agent loads skills (project `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`; user `~/.claude/skills/`, `~/.agents/skills/`; installed plugins), at the subagent types the harness offers, at connected MCP tools, and at project scripts. Search for the phases this request needs, by name and description. Do not inventory every installed skill.

If a search for the words a workflow would use (`workflow`, `process`, `RFC`, `design doc`, `release`, `migration`, `hotfix`, `review`) turns up a relevant doc you were not led to, read it too.

**Sensitive data boundary.** Do not open or expose secret values, credentials, private keys, tokens, or production data during discovery: `.env` files, `credentials.json`, service-account keys, `*.key` files, data dumps. When configuration matters, read the schema, the variable names, templates such as `.env.example`, and redacted examples instead. Read a sensitive value only when the user has authorized it and the task cannot be done without it, following the project's security policy.

## How to evaluate what you find

### Sort each finding

Sort each finding into one of the instruction types defined in [conflict-resolution.md](conflict-resolution.md#types-of-instruction), or into background, which explains but asks for nothing. Typical findings:

| Finding | Type |
|---|---|
| "Run ruff before committing" | Working rule |
| "1. Write a change note. 2. Build on a branch. 3. ..." | Workflow |
| "The tech lead approves schema changes" | Approval gate |
| "Write the failing test first" | Methodology |
| A `schema-change` skill, `make migrate-check` | Capability |
| An architecture overview | Background |

Finding an `AGENTS.md` or `CLAUDE.md` does not mean the project has a workflow. A file of rules is context and constraints; the process still comes from somewhere else, and phase 1 resolution decides where.

### Check that a workflow or rule is in force

A doc in the repository is a candidate, not an instruction. Check the ones you will rely on:

| Check | How | What it tells you |
|---|---|---|
| Is it current? | `git log -1 --format=%cs -- <file>`; whether the commands, paths, and tools it names still exist; whether CI runs what it describes | An old file that still matches CI is fine. One that names a removed script is out of date. |
| Is it in force? | Words like legacy, deprecated, old, or superseded in its name or text; whether the root instructions or README link to it; whether a newer doc covers the same ground | `docs/legacy-workflow.md` next to a newer process in `CONTRIBUTING.md` is superseded. |
| Does it match practice? | Compare it with the code, tests, CI, and config | A mismatch is a finding to record, not a verdict on which side is right. See below. |
| Does it cover this request? | Which work types and which parts of the repo it describes | A feature process says nothing about an urgent production fix or a migration. |
| Who does it bind? | Whether it addresses agents, all contributors, or one team; root or subfolder | A release runbook for the on-call team does not bind a refactor in a library. |

Give each workflow an assessment of **applies**, **doubtful**, or **superseded**, with the reason. These are judgments for repository adaptation to weigh, not a decision on the mode. When two rules disagree, such as an old test command in `CONTRIBUTING.md` against a newer one in `AGENTS.md`, record both for [conflict-resolution.md](conflict-resolution.md).

### Practice is evidence, not authority

Use code, tests, CI, configuration, and history to understand how the project works and to test the docs against it. Do not infer a mandatory rule from repeated behavior alone. When practice and an explicit rule disagree, either could be wrong: the doc may be out of date, or people may be skipping a rule that still holds. If the docs require a rollback for every migration and recent migrations have none, that does not show the policy changed.

So record the discrepancy as a discrepancy. For example: "CI and the existing tests use unittest; the README says pytest. Which governs the current testing process is unresolved." Resolve it through the project's precedence rules, or ask the user when the intended policy is unclear. Until then, work in a way that satisfies both where you can, such as tests that run under the command CI uses.

### Note each capability's roles

For each capability you might use, note what it does and who would use it: the main session, the coder, or the reviewer. A method says how an activity is done (`test-driven-development`); a specialized capability performs it (`how`, `blast-radius`, a repository `schema-change` skill). Some skills bring a whole loop of their own: pstack `poteto-mode` routes to a playbook and may start subagents, and Superpowers `subagent-driven-development` runs tasks with reviews. Here they run inside an assignment, never as owners of the issue.

Also note any human approver the project names for a gate, such as a tech lead or code owner. They are people, not capabilities.

Also note for each:

- **Contract.** The gates and required order it imposes. Superpowers `brainstorming` holds implementation until the design is approved and then hands off only to `writing-plans`, which asks for an execution method when none was given. pstack `architect` goes straight from design into implementation unless asked for a checkpoint. Noting these now keeps planning from running into a gate it will hit later.
- **Invocation.** Whether the agent can call it. A skill with `disable-model-invocation: true` cannot be called as a tool; [repository-adaptation.md](repository-adaptation.md#invocation-modes) covers what to do.

Whether Superpowers or pstack is installed matters only if the run will need it, which planning decides. Note it and move on.

## When to stop

Stop discovering when you can answer all of these for this request:

1. What is its work type and scope, at first guess?
2. Which instructions and rules apply to the files it touches, and are they in force?
3. Is there a project workflow for this work type, and does it apply, look doubtful, or is it superseded?
4. Where do docs and practice disagree, and which conflicts are still unresolved?
5. Who or what can do each phase this request needs?

For a one-line question that may take a minute. Widen the search only when an answer is missing or what you found points further: a nested `AGENTS.md` that links a migration policy, a CI job that runs a check no doc mentions, a request that turns out to touch a second service. If after a reasonable search a question has no answer, write "none found" in the note; that is a finding repository adaptation can use.

## The context note

Keep a short note for the rest of the run. It feeds the capability map, the decisions, and the final report.

```markdown
## Project context

- Repository: baseline at a1b2c3d (this session); refreshed at f4e5d6c, new skill `schema-change`, CONTRIBUTING.md "Migrations" changed
- Git state: branch fix/rename-col from main, clean
- Request: rename a column used by the load and the report
- Classification: migration; cross-cutting (load, report, tests)
- Read: AGENTS.md, CONTRIBUTING.md, load.py, report.py, tests/, .github/workflows/ci.yml
- Working rules:
  - migrations must be backward compatible (CONTRIBUTING.md)
  - no direct commits to main (AGENTS.md)
  - CI and existing tests use unittest
- Workflows:
  - feature process in CONTRIBUTING.md: applies to features, silent on migrations
  - docs/old-release.md: superseded, names a deploy script that no longer exists
- Capabilities:
  - project skill `schema-change`: migration checks, invocable; for the coder
  - Superpowers: installed (methods; brainstorming gate, then writing-plans)
  - pstack: installed, model invocation disabled (read and follow; poteto-mode in a Herdr coder session)
- Workflow coverage: partial (a feature process exists; nothing for migrations)
- Gaps: no documented process for planning a migration
- Unresolved conflicts: README says pytest, CI and tests use unittest
```

The values above are illustrative.

## Checklist

- [ ] Built an overview baseline of the repository if there was none you could check, or refreshed the parts that changed since it, after reading the current instructions and Git state.
- [ ] Classified the request by work type and work scope, noting anything uncertain.
- [ ] Read the agent and contributor instructions at the root and in each folder on the path to the files you will change, without assuming the nearest one wins.
- [ ] Followed links to the workflow docs for this work type, and skipped docs for unrelated types.
- [ ] Read the code and tests you will change.
- [ ] Checked practice signals (CI, config, recent history) for the rules you will rely on.
- [ ] Left secret values, credentials, keys, and production data unread; used names, schemas, and templates instead.
- [ ] Sorted findings into working rules, workflows, approval gates, methodologies, capabilities, and background.
- [ ] Assessed each relevant workflow as applies, doubtful, or superseded, with the reason.
- [ ] Recorded where docs and practice disagree as discrepancies, without turning practice into a rule.
- [ ] Found capabilities for the phases this request needs, with the roles they can fill, their contract, and whether the agent can invoke them; noted any human approvers.
- [ ] Can answer the five stop questions, or wrote "none found" where a search came up empty.
- [ ] Wrote the context note, including workflow confidence and unresolved conflicts.
