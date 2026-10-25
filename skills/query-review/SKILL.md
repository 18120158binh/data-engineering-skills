---
name: query-review
description: Review a new or changed SQL query before it ships, on PostgreSQL or ClickHouse, following GitLab's database development guidelines as the reference. Orders the work (get the SQL actually executed in every variant, get its plan on production-sized data with realistic parameters, read the plan, hold it to a written budget, check the index and the query's shape, hand the evidence to the reviewer) and points the agent to the GitLab page to read at each step. Use it when you write or review a query, an ORM call that generates one, a view, or a batch query, even if the user only says "is this query OK", "will this be slow", or "review this SQL".
metadata:
  version: "0.1"
---

# Query review

This skill orders the review of a query before it ships. The method for getting and reading plans, and the rules for indexes, pagination, and query shape, come from GitLab's database development guidelines, which are the reference for this skill. Read the pages each step names, and cite them in the hand-back.

## Where this fits

| You need | Skill |
|---|---|
| Make something already slow faster, and prove it | `database-optimization` |
| Design the table and its keys | `data-modeling` |
| Batch queries for a backfill | `large-table-operations` |

## Steps

Open a todo list with one entry per step.

### 1. Get the SQL as executed

Capture the SQL the database receives, not the ORM code, for every variant the code can produce: the main query, any count, any existence check, and each combination of optional filters.

Read: [SQL guidelines](https://docs.gitlab.com/development/sql/) and [Query count limits](https://docs.gitlab.com/development/database/query_count_limits/).

### 2. Get the plan on production-sized data

Run the plan on a production-sized copy or a replica, never on development data, with parameters that return rows, including the largest tenant. Get it with a cold and a warm cache.

Read: [Understanding EXPLAIN plans](https://docs.gitlab.com/development/database/understanding_explain_plans/), and the PostgreSQL [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html) documentation for your version. For ClickHouse, the query performance section of the [ClickHouse reviewer guidelines](https://docs.gitlab.com/development/database/clickhouse/reviewer_guidelines/) and [Optimizing query execution](https://docs.gitlab.com/development/database/clickhouse/optimization/).

### 3. Read the plan

Write down what the plan reads compared with what it returns, and every node that grows with the table rather than with the result.

Read: the sections on node statistics and on what makes a bad plan in [Understanding EXPLAIN plans](https://docs.gitlab.com/development/database/understanding_explain_plans/).

### 4. Hold it to a budget

Write down a time budget for each place the query runs: a web request, a background job, a migration. Check the plan against it, cold and warm.

Read: [Query performance guidelines](https://docs.gitlab.com/development/database/query_performance/), for GitLab's budgets as a starting point.

### 5. Check the index and the query's shape

Read what applies:

| The query | Read |
|---|---|
| Relies on a new or changed index | [Adding database indexes](https://docs.gitlab.com/development/database/adding_database_indexes/) |
| Pages through results | [Pagination guidelines](https://docs.gitlab.com/development/database/pagination_guidelines/) and [Pagination performance guidelines](https://docs.gitlab.com/development/database/pagination_performance_guidelines/) |
| Lists the latest children across many parents | [Efficient IN operator queries](https://docs.gitlab.com/development/database/efficient_in_operator_queries/) |
| Filters on a list of values and its plan flips | [Forcing index seeks with LATERAL joins](https://docs.gitlab.com/development/database/lateral_planner_fence/) |
| Updates or deletes a set of rows | [Updating multiple values](https://docs.gitlab.com/development/database/setting_multiple_values/), and `large-table-operations` |
| Needs to be traced to its source | [Database query comments](https://docs.gitlab.com/development/database/database_query_comments/) |

### 6. Hand the evidence to the reviewer

Use the author's requirements and the reviewer checklist in the [Database review guidelines](https://docs.gitlab.com/development/database_review/).

## Hand back

For each query:

1. the SQL as executed;
2. the plan on production-sized data, cold and warm, with the parameters used;
3. the budget it must meet, and whether it does;
4. the index it relies on, and whether it exists in production;
5. the GitLab pages followed, and what was not checked.
