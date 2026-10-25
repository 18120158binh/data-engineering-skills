# Criteria

Score every option against each criterion that applies. Each criterion states the question and the stance this skill takes, with the failure behind it.

## Correctness

**1. Correct under replay.** What happens when an input arrives twice, late, or out of order, or a run restarts from a checkpoint?
- Prefer at-least-once delivery with idempotent writes over exactly-once. Exactly-once covers only the hop between systems that share a transaction. It does not cover a database sink, an outside consumer, or a re-snapshot. Idempotent writes are correct whatever caused the repeat.
- A replay must rebuild the same result.

**2. One owner for each key and each row.** Who writes each piece of state, and in what order?
- Route all work for one key to one writer, and get ordering from that keying, not from locks. A lock moves the contention instead of removing it.
- A design that gives up keying usually needs a workaround for every guarantee it lost.

**3. One decider, no second copy that drifts.** Is any fact decided in two places, or copied where it can go stale, such as a cache that ignores merges, a second DDL file, or a second copy of the rules?
- Prefer one decider and one source, and derive the rest.

**4. Bounded error.** Where the design approximates, is the error bounded and stated?
- An approximation with a known small error, such as a sketch with a small stated error, is acceptable.
- A cap whose error depends on how active a user is, such as keeping only the first N events per user, is not, because the answers go wrong exactly for the users who matter most.

## Runtime

**5. Nothing slow on the hot path.** Does the path that must answer fast wait on a database, a remote call, or an LLM?
- Keep the decision path off stores that can be slow. When a lookup is unavoidable, run it off the processing thread with bounded concurrency, so a slow store applies backpressure instead of blocking everything.

**6. Latency for the user against strict ordering.** When the two conflict, which does the use case need?
- A message meant to go out within seconds of an event can accept a narrow, written-down ordering gap. Say which cases the gap affects.

**7. Scale, measured.** What are the numbers the design must handle, and were they measured?
- Prefer a measured number with its run over an estimate. An option that only works at untested scale names the test.

## Operations

**8. Operational burden against evidence.** How many new moving parts does it add (topics, stores, jobs, slots, deploy steps), and is the problem it solves real?
- Every new part must be created, secured, watched, and upgraded. Do not pay that for an outage nobody has seen. Prefer deferring with an alarm that shows the outage when it happens.
- Prefer the stack already running. A second store needs a reason the first cannot meet.

**9. State survives change.** Can state and data move across an upgrade, a schema change, or a re-keying?
- A design whose state cannot be restored after a field is added, or that needs all state re-keyed to change tenancy, carries that cost into every future change. Every change to a job graph or its state needs an upgrade note.

**10. Testable by the team.** Can the team's test harness run it, and does the team know the components?
- A design that depends on internals the test harness cannot drive is a risk until the harness can. That condition can reverse the decision later, and the record says so.

## Business

**11. Lock-in and maturity.** Does it tie the system to one vendor's conventions, an alpha API, or a version-specific feature?
- Prefer small, framework-independent pieces and standard protocols. An alpha dependency needs a rollback path that keeps the existing path working.

**12. Cost and isolation per customer.** What does each new tenant cost, and how isolated is it?
- Score isolation and cost per customer side by side. Decide tenancy before the second customer arrives, because changing it later re-keys every table and all stored state.

**13. Residency and privacy.** Where may the data live and travel, and what personal data does the design copy, log, or send out?
- Keep each region's data in its region. Logs are kept long and read widely, so they hold no personal data. A dead-letter or side store with personal data needs its own access rule and retention.

## How the evidence counts

- A measured result beats an argument. An argument beats an impression.
- Something tried and failed is strong evidence against that option. Record it in the alternatives table.
- Agreement between the advocate and the challenger is strong. A point only one of them raised gets weighed, not counted.
