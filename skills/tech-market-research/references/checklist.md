# Candidate checklist

Check each candidate against every section. Record the answer, the source, and how it is known.

## Evidence labels

| Label | Meaning |
|---|---|
| Reproduced | You ran it and saw the behavior. Say how. |
| Read from source | From the code at a release tag or a pinned commit. Give the link. |
| Read from docs | From the vendor's docs for the exact version. Give the link and version. |
| Vendor claim | From marketing or a sales page. |
| Third party | From a blog, benchmark site, or forum. A lead to check. |
| UNVERIFIED | No primary source found. Say what would verify it. |

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
