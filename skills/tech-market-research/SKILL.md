---
name: tech-market-research
description: Research the tools and approaches that could do one job in a system, compare them with the current approach in a table of metrics, argue whether to keep the current approach or change it given the system's status, requirements, scope, and phase, and write a report that ends in a final approach. Every fact that could decide it has a primary source, a version, and a date. Use it before choosing or replacing a tool or an approach, or when someone asks "what should we use for X", "should we switch from Y", "is Y still maintained", "how much would Z cost", or "what are the alternatives to W".
metadata:
  version: "0.1"
---

# Tech market research

Produces a research report that ends in a final approach: keep what you have, change it, or change it later. It prevents two failures: choosing a tool on its marketing instead of on sourced facts, and choosing the best tool in general instead of the one that fits this system now.

## Principles

### Judge by the system as it is

Every comparison and argument is judged against the current system's status, the requirements, the scope, and the phase. A tool that is better in general is not better here unless it fixes something this system needs now. **Why**: a choice made for an imagined scale or a later phase costs effort today and may never pay off. **The test**: does each argument in the report name the current status, a requirement, the scope, or the phase?

### Source every deciding fact

Every price, limit, and claim that could decide the choice has a primary source, the version it applies to, and the date it was read, and is labeled per `principle-label-the-evidence`. **Why**: prices and features change, vendors leave out what a tool does not do, and an unsourced fact cannot be checked later. **The test**: which deciding facts lack a source, a version, a date, or a label?

## Steps

Open a todo list with one entry per step.

### 1. Frame the question

Write down:

- **The job**, in one sentence: what the tool or approach must do.
- **The current approach**: the tools or the way the job is done today, if any.
- **The current status**: what runs today, its numbers (volume, latency, cost, failures), what works, and what hurts.
- **The requirements, as numbers**: volume, latency, retention, regions, budget.
- **The scope and the phase**: what is in and out of scope, and the phase, such as prototype, pilot, production, or scale-up.
- **The constraints**: self-hosted or managed, data residency, how long a vendor may keep the data, license limits, and the skills of the team that will run it.

Read the current approach and status from the code, configuration, and dashboards. Ask the owner for the requirements, scope, phase, and constraints. Never fill a missing one with a guess.

### 2. Research the alternatives

1. **List every option before judging any**: established vendors, open-source projects, their managed versions, and other approaches to the job (for example batch instead of streaming). Add the current approach, and a small in-house build with roughly what it would take.
2. **Find the common shape**: how established products solve the problem, per `principle-follow-the-common-shape`.
3. **Check each option** against [references/checklist.md](references/checklist.md): fit with the stack, license and maintenance, cost, real limits, gotchas, data residency, and operational burden.
4. **Drop an option** as soon as it fails a hard requirement, and record which requirement and the evidence.

For every fact:

- Use the primary source: the vendor's docs, pricing page, license file, release notes, issue tracker, and source code. A blog post, benchmark site, or comparison article is a lead to check, not a source.
- Use the docs for the version you would run, not for the latest version.
- When a third party disagrees with the vendor, say so, and say which you trust and why.
- Never paste credentials or internal data into a vendor's tool, a playground, or a search engine.

### 3. Compare

1. **Choose the metrics before filling the table**, from the requirements and constraints, per `principle-analyze-trade-offs`. Typical metrics: fit with each requirement, cost at the target volume and when idle, operational burden, cost of moving from the current approach, maturity (license, release history, maintainers), and the deciding gotcha. Say which two or three metrics decide this case.
2. **Build the table**: one row per option still standing, with the current approach as the first row. One column per metric. Each cell holds a value with its unit and its source label.

### 4. Argue: keep or change

For each option that beats the current approach on a deciding metric, write:

- what it fixes in the current status, with numbers;
- what switching costs: migration, running both side by side, retraining, and the risk of the move;
- whether the phase justifies the switch now, later, or never;
- each objection, sorted per `principle-analyze-trade-offs`.

When there is no current approach, argue among the options that remain.

When a deciding claim can only be settled by running the tool, propose a spike: a realistic end-to-end setup, the baseline run at the same time with the same inputs, a check that each run used what it asked for (model, version, tier, setting), the result that would change the answer, and the limits of the run (number of runs, sample size, rate or cost caps). Run it only when the owner asks.

### 5. Form the final approach

State, in two or three sentences tied to the status, requirements, scope, and phase:

- the approach: keep the current one, change to an option, or keep it now and change later;
- what it costs, and who pays;
- the conditions that would reverse it, so the choice can be revisited;
- the next steps, such as a spike or an outline of the move.

The final approach is a recommendation. The owner approves it.

### 6. Write the report

Use the format in [references/report.md](references/report.md). Put the final approach first, then the evidence behind it.

## Hand back

1. **The report**, in the format of [references/report.md](references/report.md), dated, with a source and a label on every deciding fact.
2. **The final approach**, with its cost, the conditions that would reverse it, and its next steps.
3. **Unverified claims** that could change the answer, and the spike or source that would settle each.
4. **For the owner**: requirements, scope, or phase nobody gave, each with options and a recommendation, and the final approach to approve.
