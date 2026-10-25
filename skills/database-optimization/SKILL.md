---
name: database-optimization
description: Make a slow query, table, or database workload faster, and prove the gain. Sets a numeric target, captures a baseline on production-sized data, names what limits it from evidence before changing anything, tries the cheapest fix first, changes one thing at a time, and verifies the result against the baseline with the same inputs and cache states, the spread across runs, unchanged results, and side effects on writes and storage. Points the agent to GitLab's database guidelines and case studies for the techniques. Covers PostgreSQL and ClickHouse. Use it when something is slow, a table grows too fast, writes contend, or someone proposes an index, a cache, a materialized view, a denormalization, or a new store for speed, even if the user only says "this is slow", "speed this up", or "optimize this table".
metadata:
  version: "0.1"
---

# Database optimization

An optimization is done when a number someone cares about moved, the cause of the move is known, and nothing else got worse. The method in this skill is about proving that. The techniques for making things faster come from GitLab's database development guidelines, listed in step 4.

## Where this fits

| You need | Skill |
|---|---|
| Review a new query before it ships | `query-review` |
| Change the schema the fix needs | `schema-change` |
| Rewrite or backfill a large table as part of the fix | `large-table-operations` |
| Choose between bigger designs, such as a new store | `architecture-review` |
| Table design rules | `data-modeling` |

## Steps

Open a todo list with one entry per step.

### 1. Set the target

Write down what is slow as a number (a latency at a percentile, a job's runtime, rows per second, growth per day), the number at which this is done, and where it is measured: which query, parameters, data, and load.

### 2. Capture the baseline

Measure on production-sized data, with a cold and a warm cache, enough times to see the spread. Record the plan with buffers, and the side metrics the change might hurt: write latency, table and index size, the plans of other queries on the same table. [Understanding EXPLAIN plans](https://docs.gitlab.com/development/database/understanding_explain_plans/) shows how to get comparable plans.

### 3. Name what limits it

Before changing anything, name the limiter from evidence: the plan, buffer counts, wait events, `pg_locks`, `pg_stat_statements`, or `system.query_log`. Ask why it is not twice as fast, and answer from what you measured. A guess from reading the code is not a limiter.

### 4. Try the cheapest fix first

Prefer a fix that adds nothing to keep consistent: a query rewrite or one index before a table reshape, a table reshape before a precomputed copy, a precomputed copy before a new store. Count each fix's write cost, backfill, and upkeep as part of its cost. A move to a new store goes through `architecture-review`.

Read what fits the limiter:

| Limiter or idea | Read |
|---|---|
| Plan reads far more than it returns, or the timings vary | [Query performance guidelines](https://docs.gitlab.com/development/database/query_performance/) |
| A missing or wrong index | [Adding database indexes](https://docs.gitlab.com/development/database/adding_database_indexes/) |
| Latest rows across many parents | [Efficient IN operator queries](https://docs.gitlab.com/development/database/efficient_in_operator_queries/) |
| A value list that flips the plan | [Forcing index seeks with LATERAL joins](https://docs.gitlab.com/development/database/lateral_planner_fence/) |
| Deep pages | [Pagination performance guidelines](https://docs.gitlab.com/development/database/pagination_performance_guidelines/) |
| Wide rows, a hot row, many indexes | [Data layout and access patterns](https://docs.gitlab.com/development/database/layout_and_access_patterns/) |
| Wasted space per row | [Ordering table columns](https://docs.gitlab.com/development/database/ordering_table_columns/) |
| Data that grows without bound | [Time-decay data](https://docs.gitlab.com/development/database/scalability/patterns/time_decay/) |
| Small data read very often | [Read-mostly data](https://docs.gitlab.com/development/database/scalability/patterns/read_mostly/) |
| The wrong store for the access pattern | [Datastore guidance](https://docs.gitlab.com/development/database/datastore_guidance/) |
| Denormalizing to speed up a filter | The case study [Filtering by label](https://docs.gitlab.com/development/database/filtering_by_label/) |
| Keeping derived counters out of hot transactions | The case study [Namespaces storage statistics](https://docs.gitlab.com/development/database/namespaces_storage_statistics/) |
| Deep hierarchies | [Group hierarchy query optimization](https://docs.gitlab.com/development/database/group_hierarchy_optimization/) |
| ClickHouse | [Optimizing query execution](https://docs.gitlab.com/development/database/clickhouse/optimization/), and the case studies on [activity data](https://docs.gitlab.com/development/database/clickhouse/gitlab_activity_data/) and [merge request analytics](https://docs.gitlab.com/development/database/clickhouse/merge_request_analytics/) |

The owner's own rules for ClickHouse are in `data-modeling`: measure codecs and `LowCardinality` on a real sample, confirm a projection in the query log, and materialize a derived total only when the view's cost is measured.

### 5. Change one thing at a time

Make one change, measure it, keep it if it moved the number, and revert it if it did not. Two changes at once leave you unable to tell which one helped, or whether one hurt.

### 6. Verify against the baseline

Verify with [references/verify.md](references/verify.md): the same inputs and cache states as the baseline, the spread across runs, the same results as before, and the side effects on writes, storage, and other queries. When the gain is smaller than the spread between runs, there is no gain.

### 7. Ship it safely

The change ships through `schema-change` or `large-table-operations`. An agent does not change production. It hands over the change, the measurements, and the commands.

## Hand back

1. The target, and the baseline with its run count and spread.
2. The limiter, with the evidence that named it.
3. Each change tried, the page it came from, its measured effect, and whether it was kept.
4. The final numbers against the baseline, the side effects measured, and a check that results are unchanged.
5. What was not measured.
