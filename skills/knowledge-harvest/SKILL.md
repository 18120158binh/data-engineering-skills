---
name: knowledge-harvest
description: Collect the valuable knowledge buried in past work (repositories, decision records, contracts, runbooks, incident notes, known issues, commit history, pull request reviews, decision logs, and agent sessions) into a reviewed catalog of rules, decisions, failure stories, tool gotchas, measured numbers, and open problems, each with its evidence and a label saying whether the owner stated it, it was inferred, or a teammate wrote it. Establishes who wrote what before mining, fans out read-only agents by slice, verifies quotes, removes duplicates and resolves conflicts, keeps private evidence out of anything published, and routes each item to the skill or file that should own it. Use it before writing or updating a skill from experience, when onboarding to a codebase's history, before a retrospective over a long period, or when someone asks "what have we learned", "collect what we know about X", "mine my repos", or "turn my history into rules".
metadata:
  version: "0.1"
---

# Knowledge harvest

Most of what a team knows is already written down, scattered across decision records, fix commits, review comments, and runbooks. Nobody can use it while it stays scattered. This skill collects it into one catalog where every item carries its evidence, says whose knowledge it is, and names the place it should live.

## Where this fits

| You need | Skill |
|---|---|
| Look back at one finished piece of work and change the process | `retrospective` |
| Turn harvested rules into a skill | the skill that owns the topic, or a new one |

## Steps

Open a todo list with one entry per step.

### 1. Scope

Write down:

- **The purpose**: what the harvest is for, such as a new skill, an update to one, onboarding, or a retrospective. The purpose decides which items count as valuable.
- **The topics**: for example pipeline operations, design decisions, or tool choices.
- **The sources**: which repositories, logs, and sessions, and the time range.
- **Whose knowledge it is**: usually one person or one team. Items from others are still useful, but they are labeled.

### 2. Find out who wrote what

Before reading content, find the authors:

```bash
git -C <repo> shortlog -sne --all | head -20
git -C <repo> log --format='%an %ad %s' --date=short -- <path> | head
```

- Note which repositories, folders, and documents are the owner's work, which are a teammate's, and which are copied from another project. A folder of vendored skills or third-party code often looks like the owner's own rules.
- One person can appear under several names and emails. Group them.

**Why**: a harvest that credits the owner with a teammate's rule, or with a vendored file, writes the wrong person's judgment into the result.

### 3. List the sources

For each repository, list what holds knowledge, richest first. [references/sources.md](references/sources.md) says where to look and what each kind of source tends to hold.

### 4. Fan out

Split the work into slices by topic or by repository, and give each slice to one read-only subagent with the brief in [references/slice-brief.md](references/slice-brief.md).

- Every slice returns items in the same shape, from [references/item-schema.md](references/item-schema.md).
- Tell each slice what is already captured, so it reports only what is new.
- Slices must not edit, commit, or call any remote system.
- For a small scope, one agent or your own reading is enough. Do not fan out more than the sources need.

### 5. Verify

- Spot-check quotes against the files. Check every quote that decides something, and a sample of the rest. Drop an item whose evidence does not hold up.
- Drop items without evidence. "I remember that" is not evidence.
- Merge duplicates, keeping the strongest evidence.
- Resolve conflicts. When two sources disagree, the later decision usually supersedes the earlier one. Say which won and why. When it is unclear, list it for the owner.

### 6. Keep what is valuable

Keep an item when it would change a decision someone makes later. In practice:

- a rule with the failure it prevents;
- a decision with the alternatives it beat, and especially a decision that was later reversed, with what triggered the reversal;
- a failure story with numbers, and the rule it produced;
- a tool's behavior that its marketing does not mention;
- a measured number with the run behind it;
- something wrong right now: drift between a document and the code, a secret in source, an open defect.

Drop one-off observations, style preferences that nobody enforced, and items already captured where they belong. Note those briefly, so the owner sees they were considered.

### 7. Separate private from publishable

The catalog keeps its full evidence: paths, commits, quotes. Keep it out of anything public, in a git-ignored folder or a private document.

Anything that will be published, such as a public skill, is written in general terms: no company or customer names, internal hostnames, ticket ids, internal paths, or personal data. Never copy a secret, a token, or a credentialed URL into the catalog or anywhere else, even as evidence. Say that one exists and where.

### 8. Route and hand back

Suggest an owner for each item, using the routing table in the `retrospective` skill: a test or lint, a contract, a decision record, a skill, `AGENTS.md`, or a script. Then hand back for review. The owner confirms, edits, or cuts items, and only confirmed items go into skills or shared files.

## Hand back

1. **The catalog**, saved privately, grouped by topic. Each item follows [references/item-schema.md](references/item-schema.md).
2. **Authorship**: who wrote which sources, and what was excluded as a teammate's or third-party work.
3. **Routing**: for each item, where it should live.
4. **Things to fix now**: drift, secrets in source, and open defects the harvest found.
5. **Questions for the owner**: conflicts you could not resolve, and items labeled INFERRED or TEAM that need a yes or no.
