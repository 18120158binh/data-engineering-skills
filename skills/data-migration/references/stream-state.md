# Migrating stream job state

Rules for stateful stream jobs, written from Flink. Most of them hold for any engine that restores state from a snapshot.

## Before the change

- **Ask whether deployed state exists.** If the job has never run in production, start fresh, and write no migration.
- **Give every stateful operator a fixed id.** Generated ids change with the job graph, including parallelism and chaining, so a savepoint taken under one setting may not restore under another, in either the new build or the old one.
- **When you add fixed ids to a running job, carry the old generated ids for one release** so the existing savepoints still restore. Derive those ids from the engine, never from a copy of your own constants. Delete them once a savepoint from the new version exists and no older one is kept.

## Changing state

- **Add new state instead of renaming old state.** Renamed state starts empty, which can lose deduplication ids and open a double-count window.
- **Migrate lazily, key by key.** Keep the old state with its old serializer and retention. Move each key the first time it is touched, and delete the old state only after its retention has passed and no savepoint from before the change is kept.
- **Know your serializer.** State stored through a generic serializer such as Kryo can fail to restore once its record type gains a field. A schema-aware serializer, such as Flink's POJO serializer, handles added and removed fields. Move state to a schema-aware serializer before you change its shape.
- **Fill new columns with the value restored state already assumes.** If restored state reads version 0 for each item it holds, existing rows get 0 too. Otherwise the state and the table disagree.

## Proving it

- **Prove compatibility in both directions**: old state restored into new code, and new state restored into old code. The second direction is your rollback. A throwaway operator test on the real state backend is enough.
- **After a restore that allows dropped state, read which state was dropped.** The engine logs each operator whose state it skipped. Every id in that list must be one you meant to drop, because the flag drops all unmapped state silently.

## Cutover

- **Stop with a savepoint, and start the new version from it.** Ask a person before any start without one.
- **Take the savepoint when traffic is low** if the restore drops in-flight work, such as records waiting on an async lookup.
- **Start consumers before producers.**
- **Moving between state backends**, such as from heap to RocksDB, needs a savepoint in the engine's canonical format.

## Change data capture during a handover

- If the old version drops its replication slot when it stops, the changes made between that drop and the new slot's creation are lost silently. Freeze writes to the captured tables, stop and upgrade in a fixed order, check that every slot exists and is active, then lift the freeze.
- Keep slots across stops, and delay the position each slot confirms by enough checkpoints that a rollback can re-read the changes. That delay is the rollback window. Past it, the point of no return for captured changes has passed.
