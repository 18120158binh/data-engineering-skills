# database-upgrade

Orders the work of upgrading a database to a new major version, or moving it to another instance, and sends the agent to the right page of GitLab's and the vendor's documentation at each step.

## When to use it

Use it for PostgreSQL major upgrades, managed database version changes, moving a database to a new host, and ClickHouse or operator upgrades. Typical requests: "upgrade Postgres", "move the database".

## What it adds

- A fixed order of work: plan in waves, test compatibility, prepare, choose the method and its way back, run it, check after, operate migrations during the window.
- A table from each upgrade method to the page that covers it.
- A note from the owner's team: an operator can hang on one abandoned read-only table, so look for such tables first.
- An agent never changes production. It hands the commands to a person, as in the owner's other skills.

## Reference docs

The rules this skill applies come from these documents. The skill tells the agent which one to read at each step, and the agent cites what it followed.

- GitLab, [Timeline for version upgrades](https://docs.gitlab.com/development/database/pg_upgrade_timeline/) and [Database upgrade DDL lock](https://docs.gitlab.com/development/database/database_upgrade_ddl_lock/)
- GitLab, [Check for background migrations before upgrading](https://docs.gitlab.com/update/background_migrations/)
- GitLab, [Replication and failover](https://docs.gitlab.com/administration/postgresql/replication_and_failover/), [Moving to a different PostgreSQL instance](https://docs.gitlab.com/administration/postgresql/moving/), and [PgBouncer](https://docs.gitlab.com/administration/postgresql/pgbouncer/)
- GitLab, [Load balancing](https://docs.gitlab.com/development/database/load_balancing/), [Troubleshooting PostgreSQL](https://docs.gitlab.com/administration/troubleshooting/postgresql/), and [Maintenance operations](https://docs.gitlab.com/development/database/maintenance_operations/)
- PostgreSQL, [pg_upgrade](https://www.postgresql.org/docs/current/pgupgrade.html), [logical replication](https://www.postgresql.org/docs/current/logical-replication.html), and the [release notes](https://www.postgresql.org/docs/release/)

## How it connects

| Skill | Relationship |
|---|---|
| [data-migration](../data-migration/README.md) | Moves data into a different store or shape. |
| [pipeline-migration](../pipeline-migration/README.md) | Moves a pipeline onto the upgraded engine, running old and new side by side. |
| [schema-change](../schema-change/README.md) | Makes the schema changes the new version needs. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The steps, the page to read at each one, and the hand-back. Start here. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1. They need web access to read the reference docs.

| Case | What it checks |
|---|---|
| `postgres-major-upgrade` | Plans a PostgreSQL 13 to 17 upgrade behind PgBouncer with background jobs, a method, a rollback order, and checks after. |
