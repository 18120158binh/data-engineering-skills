# query-review

Orders the review of a new or changed SQL query on PostgreSQL or ClickHouse, and sends the agent to the right page of GitLab's database guidelines at each step.

## When to use it

Use it when you write or review a query, an ORM call, a view, or a batch query. Typical requests: "is this query OK", "will this be slow", "review this SQL".

## What it adds

- A fixed order of work: the SQL as executed in every variant, its plan on production-sized data, reading the plan, a written budget, the index and shape, the evidence for the reviewer.
- A table from each kind of query to the GitLab page that covers it.
- A hand-back that lists the evidence a reviewer needs.

## Reference docs

The rules this skill applies come from these documents. The skill tells the agent which one to read at each step, and the agent cites what it followed.

- GitLab, [Understanding EXPLAIN plans](https://docs.gitlab.com/development/database/understanding_explain_plans/) and [Query performance guidelines](https://docs.gitlab.com/development/database/query_performance/)
- GitLab, [Database review guidelines](https://docs.gitlab.com/development/database_review/) and [SQL guidelines](https://docs.gitlab.com/development/sql/)
- GitLab, [Pagination guidelines](https://docs.gitlab.com/development/database/pagination_guidelines/), [Efficient IN operator queries](https://docs.gitlab.com/development/database/efficient_in_operator_queries/), and [LATERAL joins](https://docs.gitlab.com/development/database/lateral_planner_fence/)
- GitLab, the [ClickHouse reviewer guidelines](https://docs.gitlab.com/development/database/clickhouse/reviewer_guidelines/) and [Optimizing query execution](https://docs.gitlab.com/development/database/clickhouse/optimization/)
- PostgreSQL, [EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)

## How it connects

| Skill | Relationship |
|---|---|
| [database-optimization](../database-optimization/README.md) | Makes something already slow faster, and proves it. |
| [data-modeling](../data-modeling/README.md) | Designs the table and its keys. |
| [large-table-operations](../large-table-operations/README.md) | Owns batch queries for backfills. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The steps, the page to read at each one, and the hand-back. Start here. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1. They need web access to read the reference docs.

| Case | What it checks |
|---|---|
| `list-endpoint-query` | Rejects a dev-data timing, asks for a production-sized plan, fixes the index shape, and replaces OFFSET with keyset pagination. |
