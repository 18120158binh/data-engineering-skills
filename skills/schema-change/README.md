# schema-change

Orders the work of changing the schema of a live PostgreSQL or ClickHouse database, and sends the agent to the right page of GitLab's database guidelines at each step.

## When to use it

Use it when you write or review a migration or DDL on a database that serves traffic. Typical requests: "add a column", "rename this field", "add an index", "make this NOT NULL".

## What it adds

- A fixed order of work: is the table live, which procedure applies, which deploy phase, which lock, how it is retried and undone, how it is proven, who runs it.
- A table from each kind of change to the GitLab page that covers it.
- Lock levels are taken from the PostgreSQL documentation for the version you run, never from memory or a guide.
- Ask whether the table holds production data before writing a multi-step migration.
- An agent never changes production. It hands the commands to a person, as in the owner's other skills.

## Reference docs

The rules this skill applies come from these documents. The skill tells the agent which one to read at each step, and the agent cites what it followed.

- GitLab, [Avoiding downtime in migrations](https://docs.gitlab.com/development/database/avoiding_downtime_in_migrations/)
- GitLab, [Migration style guide](https://docs.gitlab.com/development/migration_style_guide/)
- GitLab, the pages on [indexes](https://docs.gitlab.com/development/database/adding_database_indexes/), [foreign keys](https://docs.gitlab.com/development/database/foreign_keys/), [CHECK](https://docs.gitlab.com/development/database/check_constraints/) and [NOT NULL](https://docs.gitlab.com/development/database/not_null_constraints/) constraints, [text](https://docs.gitlab.com/development/database/strings_and_the_text_data_type/), and [enums](https://docs.gitlab.com/development/database/creating_enums/)
- GitLab, [Database review guidelines](https://docs.gitlab.com/development/database_review/) and the [migration testing guide](https://docs.gitlab.com/development/testing_guide/testing_migrations_guide/)
- GitLab, the ClickHouse pages: [within GitLab](https://docs.gitlab.com/development/database/clickhouse/clickhouse_within_gitlab/), [reviewer guidelines](https://docs.gitlab.com/development/database/clickhouse/reviewer_guidelines/), [table design with Siphon](https://docs.gitlab.com/development/database/clickhouse/clickhouse_table_design_with_siphon/)
- PostgreSQL, [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) and [explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)

## How it connects

| Skill | Relationship |
|---|---|
| [data-modeling](../data-modeling/README.md) | Owns what the tables should look like, and its section 4 on changing a schema. |
| [large-table-operations](../large-table-operations/README.md) | Runs the backfills a schema change needs. |
| [query-review](../query-review/README.md) | Checks the queries the change adds. |
| [data-migration](../data-migration/README.md) | Moves data to another store or shape. |
| [database-upgrade](../database-upgrade/README.md) | Upgrades the database version. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The steps, the page to read at each one, and the hand-back. Start here. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1. They need web access to read the reference docs.

| Case | What it checks |
|---|---|
| `not-null-on-busy-table` | Makes a column NOT NULL on a busy 400-million-row table, following the referenced procedure. |
| `drop-column-in-one-release` | Catches a column dropped too early, a foreign key added inline, and a blocking index build. |
