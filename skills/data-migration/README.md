# data-migration

Plans, runs, and verifies a data migration, whether data, schema, stream state, ids, or consumers move from an old store or shape to a new one. The goal is that the new path is proven to match the old, a way back exists until a named point of no return, and the old path is actually removed.

## When to use it

Use it when you move to a new store, engine, or schema, or when you rename or re-key data, upgrade a database, change stream job state, backfill history into a new target, or retire a legacy table or job. Typical requests: "move this to X", "rename this column", "switch over", "can we drop the old one".

## What it believes

- First ask whether anything deployed needs to survive. If nothing does, drop and recreate, and write no compatibility code.
- Inventory every writer and reader of the old form before changing anything. Readers move before writers, and consumers start before producers.
- Write the way back before each phase: a backup proven by a restore, reverse SQL in order, the old object kept under a new name, and a named point of no return.
- Verified means the rows and columns reconcile on the natural key over the same scope, every difference has one written cause, and the data is non-trivial. Two empty tables prove nothing.
- Prove stream state compatible in both directions, because the second direction is your rollback.
- Set a removal date for the legacy path. Without one, it stays.

## How it connects

| Skill | Relationship |
|---|---|
| [architecture-review](../architecture-review/README.md) | Decides whether to migrate, and to what. |
| [tech-market-research](../tech-market-research/README.md) | Chooses the target tool. |
| [data-modeling](../data-modeling/README.md) | Owns the target tables and the expand-and-contract rules. |
| [pipeline-review](../pipeline-review/README.md) | Checks the new pipelines and the backfill job. |
| [pipeline-migration](../pipeline-migration/README.md) | Moves a running pipeline instead of stored data. |
| [retrospective](../retrospective/README.md) | Looks back once the old path is gone. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The ten steps and the hand-back. Start here. |
| [references/plan-template.md](references/plan-template.md) | The migration plan template. |
| [references/rollback.md](references/rollback.md) | Backups, reverse steps, and the point of no return. |
| [references/parity.md](references/parity.md) | What verified means, and how to reconcile rows and columns. |
| [references/stream-state.md](references/stream-state.md) | Savepoints, operator ids, and state schema changes in stream jobs. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1.

| Case | What it checks |
|---|---|
| `rename-column-with-state` | Asks whether deployed state exists, inventories readers and writers, orders the phases, writes the way back, handles cached state, and sets a removal date. |
| `backfill-into-short-ttl` | Catches a target TTL shorter than the backfill depth, unbounded parallel copies, immediate retries, and an inventory marked too early. |
