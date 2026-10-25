---
name: large-table-operations
description: Backfill, update, delete, deduplicate, partition, or swap a large live table without stalling the database, following GitLab's database development guidelines as the reference. Orders the work (where the work runs and how long it takes, how it iterates, how each batch is shaped and throttled, how it stays correct, how it is finalized, which procedure applies, who runs it in production) and points the agent to the GitLab page to read at each step. Use it when a change touches millions of rows or a hot table, even if the user only says "backfill this column", "fix the bad rows", "delete old data", "dedupe this table", or "partition it".
metadata:
  version: "0.1"
---

# Large table operations

This skill orders the work of changing many rows in a live table. The rules come from GitLab's database development guidelines, which are the reference for this skill. Read the pages each step names, and cite the page and section you followed in the hand-back.

## Where this fits

| You need | Skill |
|---|---|
| The schema change around the backfill | `schema-change` |
| Check the batch query's plan | `query-review` |
| Check the job as a pipeline: reruns, limits, alerting | `pipeline-review` |
| Move data to another store | `data-migration` |

## Steps

Open a todo list with one entry per step.

### 1. Decide where the work runs

Estimate the total runtime from a sample of batches measured on a production-sized copy, spread across the key range. Then decide whether it runs during the deploy, after it, or as a throttled background job. Treat a runtime of weeks as a cost of the design, not only of the operation.

Read: [Batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/), sections on when to use them and on estimating the total time, and [Background operations](https://docs.gitlab.com/development/database/background_operations/), its decision tree.

### 2. Choose how to iterate

Write down the key you iterate on, the index that serves each batch boundary, and how a filter is applied.

Read: [Iterating tables in batches](https://docs.gitlab.com/development/database/iterating_tables_in_batches/), including its sections on filters, non-unique columns, and complex queries, and the iteration strategies in [Batching best practices](https://docs.gitlab.com/development/database/batching_best_practices/).

### 3. Shape and throttle the job

Write down the batch and sub-batch sizes, the statement each sub-batch runs, the caps on time and rows per job, where the cursor is stored, and the database health signals that pause the job.

Read: [Batching best practices](https://docs.gitlab.com/development/database/batching_best_practices/), the throttling and optimization sections of [Batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/), [Insert into tables in batches](https://docs.gitlab.com/development/database/insert_into_tables_in_batches/), and [Updating multiple values](https://docs.gitlab.com/development/database/setting_multiple_values/).

### 4. Keep it correct

Write down why each batch is safe to run twice, how rows written during the run reach the new shape, how failures are retried and when the run gives up, and that no error is swallowed.

Read: the sections on idempotence, isolation, retries, and best practices in [Batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/).

### 5. Finalize before anything depends on it

Write down the check that proves every batch ran, and the changes that wait for it.

Read: the finalize and clean-up sections of [Batched background migrations](https://docs.gitlab.com/development/database/batched_background_migrations/).

### 6. Use the procedure for the operation

| Operation | Read |
|---|---|
| Deduplicate, then add a unique constraint | [Deduplicate database records](https://docs.gitlab.com/development/database/deduplicate_database_records/) |
| Swap a table for a rebuilt copy | [Swapping tables](https://docs.gitlab.com/development/database/swapping_tables/) |
| Partition an existing table | [Partitioning](https://docs.gitlab.com/development/database/partitioning/), with its [date range](https://docs.gitlab.com/development/database/partitioning/date_range/), [list](https://docs.gitlab.com/development/database/partitioning/list/), and [hash](https://docs.gitlab.com/development/database/partitioning/hash/) pages |
| Delete old data, or set retention | [Data retention policy](https://docs.gitlab.com/development/database/database_growth_control/data_retention_policy/) and [Time-decay data](https://docs.gitlab.com/development/database/scalability/patterns/time_decay/) |

For lock levels during partition attach, detach, or a swap, read the PostgreSQL [ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html) documentation for your version.

### 7. Hand production to a person

An agent does not start jobs against production. It hands over the job, the runtime estimate, the throttle settings, and the commands for a person to run.

## Hand back

1. The job: key, index, batch and sub-batch sizes, caps, and throttle signals.
2. The runtime estimate, with its measurement on a production-sized copy.
3. How new writes reach the new shape during the run, and the finalize check.
4. For each choice, the GitLab page and section it follows.
5. What was not measured.
