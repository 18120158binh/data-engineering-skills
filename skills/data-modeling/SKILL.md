---
name: data-modeling
description: Design or review data models, from the conceptual model (choosing an entity-relationship, dimensional, or graph model, drawn in Mermaid with a glossary, approved by a human) down to operational Postgres schemas and analytical ClickHouse tables. Covers grain, natural and surrogate keys, one writer per row, idempotent and version-guarded writes, time and timezones, absent values, soft delete, facts and dimensions with type 2 history, ClickHouse engines, sort keys, partitions, TTL, deduplication, and late data. Use it whenever you create or change a table, a column, DDL, a migration, a materialized view, a projection, a CDC or ETL target, or a fact or dimension, and whenever you review someone's schema, even if the user only says "add a table", "store X", "where should this live", or "why is this count wrong".
metadata:
  version: "1.0"
---

# Data modeling

These are rules for modeling data that is written by apps and stream jobs in Postgres and analyzed in ClickHouse. Each rule names the failure it prevents. When a rule does not fit a case, say so and explain why rather than bending the model to fit the rule.

## 0. Start with the conceptual model

Every modeling task starts with a conceptual model, even a small one, and the human approves it before any DDL. Follow [references/conceptual.md](references/conceptual.md):

1. Collect the questions the data must answer from every stakeholder, contract, use case, and lifecycle, and break each into the entities it names and the relationships it implies. The questions find the model; a short list gives a thin model. Trace every question to the entities and relationships it needs.
2. Pick the model kind for each layer from those questions: an entity-relationship model (ERD) for operational records, a dimensional model for analytics, a graph model for relationships. Ask the human what they know or prefer, recommend one, and let the human choose.
3. Draw the model as a Mermaid diagram with a glossary of every entity, fact, dimension, node, and edge.
4. Stop and ask the human to approve it. Only then design tables with the steps below.

For a change inside a model that is already approved, update that model's diagram and glossary first, then the tables.

## 1. Answer these before you design tables

A table is mostly decided by these answers. Write them down first, in this order. If the request does not answer the grain, the key, the time window, the retention, or the tenancy, ask the owner. Do not infer them from existing code, because the code may be the part that is wrong.

1. **Grain.** One sentence: "one row is one ___ per ___". Every later choice must agree with it. If two sentences are needed, there are two tables.
2. **Identity.** Which values make a row unique in the real world, and do they stay the same over the row's life? An email changes; an issuer and subject do not.
3. **Writer.** Which one process writes each row? Rows with two writers deadlock or lose updates.
4. **Replay.** Can the same input arrive twice or out of order? Assume yes: retries, reruns, backfills, checkpoint replay, and CDC snapshots all do it. Say how a second write converges on the same row.
5. **Reads.** The three queries that matter most: what they filter on, group by, and how far back they look.
6. **Time.** Which column is event time, which is write time, how late can data arrive, and in which timezone do "day" and "month" end?
7. **Lifecycle.** How rows are corrected, deleted, kept as history, and expired.
8. **Tenancy.** Who may see the row, and where that is stored.

## 2. Rules for every store

**Keys and identity**
- Key a fact by its natural identity: the values the source uses to say "this one". A replayed fact then lands on the same key. Never generate a random id on a path that can replay, because a replay writes a second row.
- An entity that people or apps create gets a server-generated UUID primary key and a UNIQUE natural key. When a system supplies the natural key (a sign-in issuer and subject, a source id), creation upserts on it, so a retried or concurrent create converges on one row. When a person chooses it (a name), creation inserts and fails on a conflict, so one person cannot silently overwrite another's row.
- Derive an id from its cause when the cause is the identity: a hash of the canonical content, or a UUIDv3 of a typed natural id. A rerun then derives the same id.
- When ids from different sources or kinds can collide (two source servers, a device id and a user id), the source or kind is part of the key.
- Carry the real source key through every view and copy. A synthetic rank or row number cannot be joined back and is not unique.

**Writers and replays**
- Give every row exactly one writer, and route all writes for a row's owner to that writer. Fix contention by keying, not by locks.
- Do not create a row that many owners update, such as a shared counter or total. Derive it with a view over the owners' rows, and materialize it only when the view's cost is measured.
- Every write converges when it is repeated: an upsert on the natural key, or an insert that skips existing rows.
- A row replaced in place is always guarded by a version that the producer carries and that only increases. Store the version in the row and replace only when the new one is higher. Without it, a delayed or replayed write overwrites a newer one.
- Facts are written once and never retracted. Downstream consumers act on the insert, and an email already sent cannot be taken back.

**Time**
- Keep event time (when it happened) and write time (when we stored it) in separate, clearly named columns. Event time drives logic. Write time is for operations.
- Store time in UTC and convert to the reader's timezone at query time. Never store a per-user timezone in data.
- Daily and monthly windows end at the business-local date, not at UTC midnight. A job that runs just after local midnight has a UTC date of the day before.
- Expect late and corrected rows. Re-extract a trailing window on every run and reload a closed period in full, and let deduplication absorb the overlap.

**Values and types**
- NULL means unknown or not measured. It is not the same as zero: "no sensor installed" is NULL, "no alarms raised" is 0. The one exception is a ClickHouse sort-key column, which cannot be Nullable and uses `''` or `0`.
- Anything that is filtered, joined, or constrained is a typed column. JSON (`jsonb` in Postgres) holds only the opaque remainder that no query looks inside.
- Use the newest type the target database version supports for the job, then check that it is the best fit for this case, for size and for the queries that read it, before you settle on it. Size numbers to the source's real precision.
- Put a closed set of values (status, type, branch) under a CHECK constraint, changed together with the code that writes it.

**History, deletion, and size**
- When an entity's attributes change and history matters, add a new row (type 2), and point facts at the version that was true when they happened. See [references/dimensional.md](references/dimensional.md).
- User-facing entities and projections are soft-deleted with a `deleted_at` column. A soft-deleted row keeps its natural key, so creating a duplicate fails and the user restores the old row instead. Definitions that stream jobs read through CDC are hard-deleted, so the jobs see a delete. Facts leave only through retention.
- Keep rows minimal. Store what a reader needs and nothing personal or optional "just in case". Do not store a derived flag as the answer to a live question; it goes stale. Store one only to detect a change.
- Decide tenancy before any data exists. If tables are shared between tenants, the tenant id leads every key and every sort key.

## 3. Store-specific rules

| Designing | Read |
|---|---|
| The conceptual model: choosing ERD, dimensional, or graph, the diagram, and the glossary | [references/conceptual.md](references/conceptual.md) |
| A Postgres table, constraint, CDC source, or projection | [references/postgres.md](references/postgres.md) |
| A ClickHouse table, partition, sort key, TTL, MV, projection, or load | [references/clickhouse.md](references/clickhouse.md) |
| Facts, dimensions, history, measures, or an analytics view | [references/dimensional.md](references/dimensional.md) |
| A design question these rules do not cover | [references/further-reading.md](references/further-reading.md), GitLab's guidelines as reference docs |

## 4. Changing a schema that exists

- Keep one DDL source. Change the DDL, the code's column names, and the data-model doc in the same commit, then search the code for the old names.
- Before the first production deployment, drop and recreate. After it, ship changes in expand and contract steps with an explicit deploy order: add the column nullable, deploy the writer, backfill, add NOT NULL and CHECKs, deploy the reader.
- Treat a change to a large production table as a proposal: the SQL, a dry run, the bytes it rewrites, a rollback, and the reversible option before the irreversible one. Change a sort key, partition key, or engine by creating a new table, copying, verifying, and swapping. Do not drop the original until the copy is verified.
- When the repository already decided something in a decision record, follow it. To change it, propose a new record instead of diverging silently.

## 5. What to hand back

First the conceptual model: the questions, the chosen model kinds, the Mermaid diagram, and the glossary, in the format in [references/conceptual.md](references/conceptual.md). If the human has not approved it yet, stop there and ask.

After approval, for each table, give a short model card, then the DDL:

```markdown
### <table>
- Grain: one row is one ___ per ___
- Key: <natural key>; <surrogate key, if any, and why>
- Writer: <the one process>; how a repeated write converges
- Time: event time <col>, write time <col>, timezone, lateness handled by <how>
- Reads served: <the main queries and how the key, sort key, or index serves them>
- Lifecycle: corrections, deletes, history, retention
- Open questions: <anything the owner must decide>
```

Name every rule you broke on purpose and why. A reviewer checks the card against the rules above before reading the DDL.
