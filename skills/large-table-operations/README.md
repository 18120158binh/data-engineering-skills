# large-table-operations

Orders the work of backfilling, updating, deleting, deduplicating, partitioning, or swapping a large live table, and sends the agent to the right page of GitLab's database guidelines at each step.

## When to use it

Use it when a change touches millions of rows or a hot table. Typical requests: "backfill this column", "fix the bad rows", "delete old data", "dedupe this table", "partition it".

## What it adds

- A fixed order of work: where the work runs and how long it takes, how it iterates, how batches are shaped and throttled, how it stays correct, how it is finalized, who runs it.
- For each step, the decisions to write down, so a reviewer can check them.
- A table from each operation to the GitLab page that covers it.
- Treat a runtime of weeks as a cost of the design.
- An agent never changes production. It hands the commands to a person, as in the owner's other skills.

## Reference docs

The rules this skill applies come from these documents. The skill tells the agent which one to read at each step, and the agent cites what it followed.

- GitLab, [Batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/) and [Background operations](https://docs.gitlab.com/development/database/background_operations/)
- GitLab, [Batching best practices](https://docs.gitlab.com/development/database/batching_best_practices/) and [Iterating tables in batches](https://docs.gitlab.com/development/database/iterating_tables_in_batches/)
- GitLab, [Insert into tables in batches](https://docs.gitlab.com/development/database/insert_into_tables_in_batches/) and [Updating multiple values](https://docs.gitlab.com/development/database/setting_multiple_values/)
- GitLab, [Deduplicate database records](https://docs.gitlab.com/development/database/deduplicate_database_records/), [Swapping tables](https://docs.gitlab.com/development/database/swapping_tables/), and [Partitioning](https://docs.gitlab.com/development/database/partitioning/)
- GitLab, [Data retention policy](https://docs.gitlab.com/development/database/database_growth_control/data_retention_policy/) and [Time-decay data](https://docs.gitlab.com/development/database/scalability/patterns/time_decay/)
- PostgreSQL, [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)

## How it connects

| Skill | Relationship |
|---|---|
| [schema-change](../schema-change/README.md) | Makes the schema change around the backfill. |
| [query-review](../query-review/README.md) | Checks the batch query's plan. |
| [pipeline-review](../pipeline-review/README.md) | Checks the job as a pipeline: reruns, limits, and alerting. |
| [data-migration](../data-migration/README.md) | Moves data to another store. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The steps, the page to read at each one, and the hand-back. Start here. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1. They need web access to read the reference docs.

| Case | What it checks |
|---|---|
| `backfill-by-offset` | Catches OFFSET paging over a moving filter, row-by-row updates, swallowed errors, and a missing throttle and finalize step. |
