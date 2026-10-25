# tech-market-research

Researches the tools, managed services, and open-source projects that could fill one role in a data architecture, and hands back an options brief where every price, limit, and claim has a primary source, a version, and a date.

## When to use it

Use it before choosing or replacing a tool, or when an architecture review needs candidates. Typical questions: "what should we use for X", "is Y still maintained", "how much would Z cost", "what are the alternatives to W".

## What it believes

- The survey supplies facts. `architecture-review` makes the decision.
- Always consider what the stack already runs, and how small an in-house version would be. A second store needs a reason.
- Look at how established products solve the problem, and note the shape most of them share.
- Primary sources only: vendor docs for the exact version, pricing pages with a date, release notes, issue trackers, and source code. A benchmark site is a lead, not a source.
- Look for the gotchas a vendor's page leaves out, on purpose: what the tool does not do for you, what cannot be stopped, what fills up while a consumer is down, and what breaks on upgrade.
- A claim that could decide the choice is verified or marked UNVERIFIED. A benchmark runs the baseline at the same time, in a realistic setup.

## How it connects

| Skill | Relationship |
|---|---|
| [architecture-review](../architecture-review/README.md) | Takes this brief's shortlist into its debate. |
| [pipeline-review](../pipeline-review/README.md) | Checks the pipeline built on the chosen tool. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The six steps and the rules for sources. Start here. |
| [references/checklist.md](references/checklist.md) | Evidence labels, and what to check for each candidate. |
| [references/options-brief.md](references/options-brief.md) | The hand-back format. |
| [evals/](evals/) | The test cases. |

## Tests

This case has not been run yet, so the skill is at version 0.1. It needs web access.

| Case | What it checks |
|---|---|
| `cdc-postgres-to-clickhouse` | A dated, sourced brief with licenses, releases, gotchas, flagged unverified claims, and no final decision. |
