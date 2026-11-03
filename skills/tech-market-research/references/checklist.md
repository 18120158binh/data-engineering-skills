# Candidate checklist

Read this at step 2 of `tech-market-research`. Check each candidate against every section, and record the answer, its source, and its label per `principle-label-the-evidence`.

## Contents

- [1. Fit with the running stack](#1-fit-with-the-running-stack)
- [2. License and maintenance](#2-license-and-maintenance)
- [3. Cost](#3-cost)
- [4. Real limits](#4-real-limits)
- [5. Gotchas to look for on purpose](#5-gotchas-to-look-for-on-purpose)
- [6. Data residency and retention](#6-data-residency-and-retention)
- [7. Operational burden](#7-operational-burden)

## 1. Fit with the running stack

- Does it support the versions we run, such as the database, the stream processor, and the orchestrator? Is the build for our exact version, or for a nearby one?
- Does it add a second store, a new protocol, or a new runtime? What does that cost to run?
- Does it bring dependencies that conflict with ours, such as a shared library at another version or a package that overrides ours on the classpath?
- How does it authenticate, and does that fit our identity setup without provider-specific code?

## 2. License and maintenance

- The license, and whether it changed recently. Note dual licenses and source-available terms that limit hosting or commercial use.
- The date of the last release and how often releases come.
- Who maintains it: one company, a foundation, or one person. What happens to users if they stop.
- Open issues for our use case, and how quickly they get answers.

For a project on GitHub, read these from the API rather than from a summary site. Set `R=<owner>/<repo>`:

```bash
curl -s https://api.github.com/repos/$R | jq '{license: .license.spdx_id, archived, pushed_at}'
curl -s "https://api.github.com/repos/$R/releases?per_page=5" | jq '.[] | {tag_name, published_at}'
curl -s "https://api.github.com/repos/$R/tags?per_page=5" | jq -r '.[].name'
curl -s "https://api.github.com/search/issues?q=repo:$R+is:issue+is:open+<your-use-case>" | jq '.total_count, [.items[:5][] | {title, created_at}]'
```

Some projects publish tags but no GitHub releases, or track issues elsewhere, such as Jira. Then read the project's own release notes and tracker, and say which you used.

Read the license file itself at the release tag you would run, because a license can change between releases.

## 3. Cost

- The price from the vendor's own page, with the date you read it.
- The cost at our volume, worked out from the pricing units.
- The idle cost: what it costs when nothing runs. Managed services often charge for capacity that sits idle.
- What a self-hosted run costs in machines and in people's time.
- Rate limits, daily caps, and credit limits that can stop a job or a benchmark partway.

## 4. Real limits

Read the docs for the version you would run, and the source when the docs fall short.

- The limits on size, throughput, and concurrency, as numbers.
- The features that are off by default, or that exist only in one mode or edition.
- The features removed or changed in recent versions.
- Anything marked alpha, beta, preview, or experimental, which means its contract can change.

## 5. Gotchas to look for on purpose

These rarely appear on a vendor's page. Look for each one in the docs, the issue tracker, and the source.

- **What it does not do for you.** For example, a replication tool that does not create the destination table, or a connector that does not expose transaction metadata.
- **Operations you cannot stop, pause, or resume.** For example, a one-time copy that cannot be cancelled while it runs, or a finished flow that cannot be resumed.
- **Resource spikes under parallel load.** What happens to memory and connections when many jobs start at once.
- **API quirks**: time in seconds in one place and milliseconds in another, a cursor value that means "no cursor", a required wrapper in a request body, a required path prefix.
- **Retention behavior**: logs, replication slots, or offsets it holds while a consumer is down, and what fills up.
- **Restart behavior**: where it starts after a restart with no saved state, and whether a restart replays history as new data.
- **Packaging**: class-loading order, bundled drivers, and version conflicts with what the runtime already ships.
- **Upgrades**: whether state survives an upgrade, and whether versions can be skipped.
- **Security defaults**: open CORS, no authentication setting, credentials in logs.

## 6. Data residency and retention

- Where the vendor stores and processes data, and whether we can choose the region.
- Whether the vendor keeps our data, for how long, and whether there is a zero-retention option.
- Which personal data would leave our systems, and whether the law that applies to us allows it.

## 7. Operational burden

- What someone must create, secure, watch, and upgrade.
- What breaks at 3 a.m., and what fixing it takes.
- Whether the team can test it locally with the harness it already has.
