---
name: schema-change
description: Change the schema of a live PostgreSQL or ClickHouse database without downtime, following GitLab's database development guidelines as the reference. Orders the work (is the table live, which procedure applies, which deploy phase each step runs in, what lock it takes, how it is retried and undone, how it is proven on production-sized data, who runs it in production) and points the agent to the GitLab page to read at each step. Use it when you write or review a migration or DDL on a database that serves traffic, even if the user only says "add a column", "rename this field", "add an index", or "make this NOT NULL".
metadata:
  version: "0.1"
---

# Schema change

This skill orders the work of changing a live schema. The rules for each operation come from GitLab's database development guidelines, which are the reference for this skill. Read the pages each step names before you write the migration, and cite the page and section you followed in the hand-back.

## Where this fits

| You need | Skill |
|---|---|
| Decide what the tables should look like | `data-modeling`, including its section 4 on changing a schema |
| Backfill or rewrite many rows as part of the change | `large-table-operations` |
| Check the queries the change adds | `query-review` |
| Move data to another store or shape | `data-migration` |
| Upgrade the database version | `database-upgrade` |

## Steps

Open a todo list with one entry per step.

### 1. Ask whether the table is live

Ask the owner whether the table holds production data. If nothing is deployed yet, drop and recreate, and write no multi-step migration. Record who said so.

### 2. Find the procedure for the operation

Read the procedure for what you are changing:

| Change | Read |
|---|---|
| Drop, rename, or retype a column; change a default; drop or rename a table; integer to bigint keys; change stored data formats | [Avoiding downtime in migrations](https://docs.gitlab.com/development/database/avoiding_downtime_in_migrations/) |
| Add or drop an index | [Adding database indexes](https://docs.gitlab.com/development/database/adding_database_indexes/) |
| Add or change a foreign key | [Foreign keys](https://docs.gitlab.com/development/database/foreign_keys/) |
| Add a CHECK constraint | [CHECK constraints](https://docs.gitlab.com/development/database/check_constraints/) |
| Make a column NOT NULL | [NOT NULL constraints](https://docs.gitlab.com/development/database/not_null_constraints/) |
| Add a text column or a length limit | [Strings and the text data type](https://docs.gitlab.com/development/database/strings_and_the_text_data_type/) |
| Add an enum | [Creating enums](https://docs.gitlab.com/development/database/creating_enums/) |
| Name a constraint or index | [Constraint naming conventions](https://docs.gitlab.com/development/database/constraint_naming_convention/) |
| Change a ClickHouse schema | [ClickHouse within GitLab](https://docs.gitlab.com/development/database/clickhouse/clickhouse_within_gitlab/) and the [ClickHouse reviewer guidelines](https://docs.gitlab.com/development/database/clickhouse/reviewer_guidelines/) |
| Change a ClickHouse table fed by change data capture | [Table design with Siphon](https://docs.gitlab.com/development/database/clickhouse/clickhouse_table_design_with_siphon/) |
| Change a sort key, partition key, or engine in ClickHouse | `data-modeling`, section 4 |

GitLab's pages use Rails helpers. Translate each helper to the SQL it runs before you use the procedure elsewhere.

### 3. Place each step in a deploy phase

Read the [Migration style guide](https://docs.gitlab.com/development/migration_style_guide/), sections "Choose an appropriate migration type" and "How long a migration should take", and [Post-deployment migrations](https://docs.gitlab.com/development/database/post_deployment_migrations/). Decide for each step whether it runs before the code deploy, after it, or as a background job, and write down your own time budget for each phase. Measure each step against it in step 6.

### 4. Check the locks

- Look up the lock each statement takes in the PostgreSQL documentation for the version you run: [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) and [explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html). Lock levels change between versions, and secondary sources sometimes get them wrong, so do not take them from memory or from a guide.
- Read the style guide's sections on lock retries and on heavy operations in a single transaction, before you write DDL against a busy table.

### 5. Make each step retryable and reversible

Read the style guide's sections on transactions, reversibility, and idempotent steps, and [Deleting migrations](https://docs.gitlab.com/development/database/deleting_migrations/). For each step, write down whether it runs in a transaction, what happens if it is retried after a partial failure, and its down step or recovery plan.

### 6. Prove it on production-sized data

Run the migration against a production-sized copy, and record each step's duration and the locks it took. [Database migration pipeline](https://docs.gitlab.com/development/database/database_migration_pipeline/), [db:check-migrations job](https://docs.gitlab.com/development/database/dbcheck-migrations-job/), and [Testing Rails migrations](https://docs.gitlab.com/development/testing_guide/testing_migrations_guide/) show what to measure and test. For a review, use the checklist in the [Database review guidelines](https://docs.gitlab.com/development/database_review/).

When the software is installed by others who upgrade across versions, also read [Adding required stops](https://docs.gitlab.com/development/database/required_stops/). When the application uses several databases, read [Migrations for multiple databases](https://docs.gitlab.com/development/database/migrations_for_multiple_databases/).

### 7. Hand production to a person

An agent does not run migrations against production. It hands over the migration, the measured timings, and the exact commands, for a person to run.

## Hand back

1. The migration files, one step each, with the phase each belongs to.
2. For each step: the GitLab page and section it follows, the lock it takes with the PostgreSQL documentation link for your version, its measured runtime on a production-sized copy, and its down step or recovery plan.
3. The order of migrations and code deploys, release by release.
4. What was not measured, said plainly.
