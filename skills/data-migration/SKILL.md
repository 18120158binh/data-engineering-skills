---
name: data-migration
description: Plan, run, and verify a data migration (moving data, schema, stream state, ids, or consumers from an old store or shape to a new one) so that the new path is proven to match the old, every difference is explained, a way back exists until a named point of no return, and the legacy path is actually removed. Covers whether anything needs migrating at all, inventory of every reader and writer, phase order (readers before writers, consumers before producers), rollback and verified backups, backfills, write freezes, row and column reconciliation, stateful stream jobs (savepoints, operator ids, state schema changes), cutover, and decommissioning. Use it when you move to a new store, engine, or schema, rename or re-key data, upgrade a database, change stream job state, backfill history into a new target, or retire a legacy table or job, even if the user only says "move this to X", "rename this column", "switch over", or "can we drop the old one".
metadata:
  version: "0.1"
---

# Data migration

A migration is done when three things are true. The new path is proven to match the old one, or to differ only where someone wrote down why. A way back existed until a point of no return that was named in advance. And the old path is gone. This skill gets there in phases, each of which can be checked.

## Where this fits

| You need | Skill |
|---|---|
| Decide whether to migrate, and to what | `architecture-review` |
| Choose the target tool | `tech-market-research` |
| Design the target tables | `data-modeling` |
| Check the new pipelines and the backfill job | `pipeline-review` |
| Move a running pipeline to a new engine version or sink | `pipeline-migration` |
| Look back once the old path is gone | `retrospective` |

## Steps

Open a todo list with one entry per step.

### 0. Is there anything to migrate?

Ask the owner whether the old system holds production data, users, or stream state that must survive. Record the answer and who gave it. Do not infer it from the code.

- When nothing is deployed yet, drop and recreate. Write no compatibility code, upgrade notes, or restore fixtures.
- **Why**: compatibility code, upgrade notes, and restore tests written for state that does not exist must all be written, reviewed, and later deleted, and real fixes wait behind them.

### 1. Frame

Write down:

- **What moves**: data, schema, stream state, ids, or consumers. Say from what to what.
- **Why**: the decision record behind the migration, or the problem it fixes.
- **Done, as numbers**: the parity tolerance, the allowed downtime, the date by which the old path is removed.
- **What users may lose**, such as writes made after a backup, accepted by the owner in writing.
- **The owner**, who approves the plan and every irreversible step, separately for each environment.

### 2. Inventory

- **Every writer of the old form**, including defaults and any code that creates new rows in the old shape. A repair run before every writer changes is undone by the next write.
- **Every reader**: jobs, views, materialized views, saved queries, exports, and other teams.
- **State and ids** that must carry over, such as stream job state, generated ids, and cursors.
- **Irreversible steps**: deletes, type changes that lose precision, enum additions, and drops. List them before anything runs.

### 3. Plan the phases

Write the plan with [references/plan-template.md](references/plan-template.md).

- **Order by who reads what.** Readers that tolerate the new shape deploy before writers, and consumers start before their producers. A new consumer group starts at the latest offset and skips whatever was produced before it. The table rules for expand and contract are in `data-modeling`.
- **Run a data migration only after the upstream change it depends on is live and verified.** Run early, a conversion applies twice or to the wrong unit, and running it again does not undo that.

### 4. Build the way back

Write the rollback for each phase before you run it. [references/rollback.md](references/rollback.md) has the rules:

- a backup verified by a restore, taken before the first change;
- reverse SQL next to every forward step, with the order and the precondition for running it;
- the old object kept under a new name rather than dropped;
- no automatic rollback onto data that has already been migrated;
- a point of no return, named and time-boxed.

### 5. Move the data

- **Backfill with limits.** Cap concurrency across the whole run, not per item. Choose the range from what the source holds, with a cap. Make a rerun safe through the target's deduplication key.
- **Check that the target keeps what you backfill.** A target whose retention or TTL is shorter than the backfill depth copies data only to drop it at the next merge, and pays the load of copying it.
- **Freeze writes across a handover gap.** When the old path stops capturing changes before the new one starts, tell the people who write to stop, and lift the freeze only after the new path is confirmed live.
- **Probe the exact path you will use**, such as a cluster context, a connection, or credentials, immediately before an irreversible step. A wrong default context can send the change to the wrong cluster, or hang while the application is down.
- Stateful stream jobs follow [references/stream-state.md](references/stream-state.md).

### 6. Prove parity

Reconcile the new path against the old, row by row and column by column, with [references/parity.md](references/parity.md). Do not call a migration verified because the new path loaded without an error, or because both sides are empty.

### 7. Cut over

Switch readers to the new path in the order the plan states. Watch the numbers the plan named. Keep the way back open until the point of no return, then say plainly that it has passed.

### 8. Remove the legacy path

- Set the removal date in the plan. A legacy path with no date stays, and keeps being shipped and maintained with nothing using it.
- Before dropping an object, record its definition, why it is dropped, its data at that moment, the checks for dependents (queries, views, materialized views, dictionaries, application code), what replaces it, and whether it can be recreated.
- Delete compatibility code, carried-over ids, and old state after one release, once no backup or savepoint from before the migration is still kept.
- Update every document that describes the old path in the same change.

### 9. Look back

Run `retrospective` once the old path is gone.

## Hand back

1. The migration plan, from the template, with the inventory, the phases, the rollback for each phase, the point of no return, and the parity definition.
2. For each phase that ran: what was proven, how (measured, read from code, or inferred), and what is still unverified.
3. The irreversible steps, each waiting for the owner's approval in each environment.
4. For an agent: the exact commands or SQL for a person to run in production. An agent does not change production itself.
