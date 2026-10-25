---
name: tech-market-research
description: Research the tools, managed services, and open-source projects that could fill one role in a data architecture (CDC, streaming, OLAP, orchestration, BI or semantic layer, LLM serving, observability, and others), then hand back an options brief where every price, limit, and claim has a primary source, a version, and a date, unverified claims are flagged, and each candidate's gotchas are checked against the docs, the source, or a spike. Covers framing the role, the long list, how established products solve it, fit with the running stack, license and maintenance, pricing and idle cost, real limits and known gotchas, data residency and retention, and evidence labels. Use it before choosing or replacing a tool, when an architecture review needs candidates, or when someone asks "what should we use for X", "is Y still maintained", "how much would Z cost", or "what are the alternatives to W".
metadata:
  version: "0.1"
---

# Tech market research

A survey is useful when every fact that could decide the choice has a primary source, a version, and a date, and when the surprises a vendor's page leaves out were looked for on purpose. This skill produces that survey. It does not make the decision. `architecture-review` does.

## Where this fits

| You need | Skill |
|---|---|
| Decide between the options this survey finds | `architecture-review` |
| Check a pipeline built on the chosen tool | `pipeline-review` |

## Steps

Open a todo list with one entry per step.

### 1. Frame the role

Write down:

- **The role**, in one sentence: the job the tool does in the system.
- **The hard requirements, as numbers**: volume, latency, retention, regions, budget.
- **The running stack**: what the tool must work with, at which versions.
- **The rules**: self-hosted or managed, data residency, data retention by vendors, license limits.

When a requirement is missing, ask the owner instead of assuming one.

### 2. Make the long list

- The established vendors and open-source projects for the role.
- The managed versions of each.
- **What we already run**: can a tool in the stack do the job? A second store or service needs a reason the first cannot meet.
- **Build it small**: what the smallest in-house version would take.

### 3. Find the common shape

Look at how four to six established products solve the same problem, from their own docs, with links. Write down the shape most of them share, and where they differ. A candidate that departs from the common shape needs a reason.

### 4. Check each candidate

Go through [references/checklist.md](references/checklist.md) for every candidate still standing:

- fit with the running stack and its versions;
- license, release history, and who maintains it;
- pricing from the vendor's own page, with the date, plus idle cost and the cost at the target volume;
- the real limits, from the docs for the exact version or from the source at a release tag;
- the known gotchas, looked for on purpose;
- data residency, vendor data retention, and security;
- the operational burden: what someone must create, watch, upgrade, and fix.

Drop a candidate as soon as it fails a hard requirement, and record why.

### 5. Verify what decides

Label every claim with how it is known, using the labels in [references/checklist.md](references/checklist.md). A claim that could decide the choice must reach "read from docs at a version", "read from source at a tag", or "reproduced". When it cannot, mark it **UNVERIFIED** and say what would verify it.

For a claim that decides the choice and can only be settled by running the tool, propose a spike or a benchmark:

- Test in a realistic setup, not one step at a time. A tool that looks good step by step can fail in the full flow.
- Run the baseline at the same time as the candidate, with the same inputs.
- Check that each run used what it asked for, such as the right model, version, or setting.
- Record the limitations: the number of runs, the sample size, and any rate or cost cap that cut a run short.

### 6. Hand back the brief

Write the options brief in the format in [references/options-brief.md](references/options-brief.md). Lead with the shortlist and the facts that separate the candidates. Recommend which options `architecture-review` should debate, not which one to pick.

## Rules for sources

- Prefer the primary source: the vendor's docs, pricing page, license file, release notes, issue tracker, and source code. A blog post, benchmark site, or comparison article is a lead to check, not a source.
- Date every price and every "latest release". Prices and features change, and an undated fact cannot be checked later.
- Cite the docs for the version you would run, not the latest version.
- When a third party disagrees with the vendor, say so and say which you trust and why. Benchmark sites often quote the wrong model, tier, or price.
- Never paste credentials or internal data into a vendor's tool or a search engine while researching.
