# Migration plan template

````markdown
# Migration: <from> to <to>

Owner: <name>. Status: draft, approved, running, cut over, or done.

## Is there anything to migrate?

<Production data, users, or state that must survive: yes or no, who said so, and when.>

## Frame

- What moves: <data, schema, state, ids, consumers>
- Why: <decision record or problem>
- Done when: <parity tolerance>, <allowed downtime>, <old path removed by YYYY-MM-DD>
- Users may lose: <what, accepted by the owner on YYYY-MM-DD>

## Inventory

| Kind | Item | Where | Notes |
|---|---|---|---|
| Writer | | | |
| Reader | | | |
| State or id | | | |

Irreversible steps:
- <step>: <why it cannot be undone>

## Phases

| # | Phase | Gate to start | Proof it worked | Way back | Owner approval |
|---|---|---|---|---|---|
| 1 | <phase> | | | | |

## Point of no return

<The step after which going back means fixing forward, and the time box before it.>

## Parity

- Verified means: <the definition from parity.md, for this migration>
- Compared on: <natural key>, <time window>, <tenants>
- Column tolerance: <per noisy column>
- Intended differences: <each, with why>

## Backfill

- Range: <from what the source holds, capped at ...>
- Concurrency cap across the run: <n>
- Target retention: <TTL or retention, at least the backfill depth>
- Rerun safety: <the deduplication key>

## Removal of the legacy path

- Date: <YYYY-MM-DD>
- Objects to drop, each with its record: <list>
- Compatibility code, carried ids, and old state to delete after: <condition>

## Open questions for the owner
````
