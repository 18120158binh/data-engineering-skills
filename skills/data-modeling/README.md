# data-modeling

Rules for designing and reviewing data models, from the conceptual model down to operational Postgres schemas and analytical ClickHouse tables. Each rule names the failure it prevents.

## When to use it

Use it when you create or change a table, a column, a migration, a materialized view, a CDC or ETL target, a fact, or a dimension, or when you review someone else's schema.

## What it covers

Conceptual models (ERD, dimensional, graph) drawn in Mermaid with a glossary, then grain, natural and surrogate keys, one writer per row, idempotent and version-guarded writes, time and timezones, absent values, soft delete, facts and dimensions with type 2 history, ClickHouse engines, sort keys, partitions, TTL, deduplication, and late data.

## What it believes

- Every modeling task starts with a conceptual model: the questions, a Mermaid diagram, and a glossary. A person approves it before anyone writes DDL.
- The questions the data must answer decide the model. Collect them from every stakeholder, contract, and lifecycle, and trace each question to the entities and relationships it needs.
- A fact is keyed by its natural identity. A path that can replay never generates a random id, because a replay would write a second row.
- Every row has exactly one writer. Totals across many owners come from a view over their rows, not from a shared counter row.
- Every write gives the same result when it runs twice. A row replaced in place is guarded by a version that only increases.
- Time is stored in UTC, with event time and write time in separate columns. Daily and monthly windows end at the business-local date.
- A soft-deleted row keeps its natural key, so creating a duplicate fails and the user restores the old row instead.
- In ClickHouse, partitions exist for dropping and reloading data. The sort key makes reads fast.

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The rules every store follows, and what to hand back. Start here. |
| [references/conceptual.md](references/conceptual.md) | Collecting the questions, choosing ERD, dimensional, or graph, the Mermaid diagram, and the glossary. |
| [references/postgres.md](references/postgres.md) | Postgres keys, writes, types, deletes, CDC sources, and tenancy. |
| [references/clickhouse.md](references/clickhouse.md) | ClickHouse engines, sort keys, partitions, TTL, deduplication, loading, aggregates, and lookups. |
| [references/dimensional.md](references/dimensional.md) | Grain, facts, type 2 dimensions, names, and tenant isolation. |
| [references/further-reading.md](references/further-reading.md) | Links to GitLab's guidelines for design questions this skill does not cover. |
| [evals/](evals/) | The test cases. |

## Tests

| Case | What it checks |
|---|---|
| `referral-program-model` | Lists the questions, picks a model kind per layer, draws Mermaid with a glossary, and stops for approval. |
| `pg-notification-log` | A Postgres log table with a stated grain, a natural key, and an idempotent insert. |
| `template-soft-delete` | Soft delete with a natural key that stays taken, and restore. |
| `vehicle-owner-history` | A type 2 dimension, and facts that point at the version valid at event time. |
| `ch-orders-from-countries` | A ClickHouse table in UTC, deduplicated per source database, with monthly partitions and TTL. |
| `review-flawed-schema` | A review that catches eight planted flaws in a proposed schema. |
