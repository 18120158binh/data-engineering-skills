# database-optimization

Makes a slow query, table, or workload faster, and proves the gain against a baseline. The proving method is this repo's own; the techniques come from GitLab's database guidelines.

## When to use it

Use it when something is slow, a table grows too fast, writes contend, or someone proposes an index, a cache, a materialized view, a denormalization, or a new store for speed. Typical requests: "this is slow", "speed this up", "optimize this table".

## What it adds

- Set a numeric target, and capture a baseline on production-sized data before changing anything.
- Name what limits it from evidence. A guess from reading code is not a limiter.
- Prefer the fix that adds the least to keep consistent, and count each fix's write cost, backfill, and upkeep.
- Change one thing at a time, and keep only what moved the number.
- Verify against the baseline: same inputs and cache states, the spread across runs, unchanged results, and side effects. This follows the explain-the-number principle from pstack and the owner's benchmark practice.
- A table from each limiter to the GitLab page or case study that covers it.

## Reference docs

The rules this skill applies come from these documents. The skill tells the agent which one to read at each step, and the agent cites what it followed.

- GitLab, [Query performance guidelines](https://docs.gitlab.com/development/database/query_performance/) and [Understanding EXPLAIN plans](https://docs.gitlab.com/development/database/understanding_explain_plans/)
- GitLab, [Data layout and access patterns](https://docs.gitlab.com/development/database/layout_and_access_patterns/), [Datastore guidance](https://docs.gitlab.com/development/database/datastore_guidance/), and [Ordering table columns](https://docs.gitlab.com/development/database/ordering_table_columns/)
- GitLab, the scalability patterns [Time-decay data](https://docs.gitlab.com/development/database/scalability/patterns/time_decay/) and [Read-mostly data](https://docs.gitlab.com/development/database/scalability/patterns/read_mostly/)
- GitLab, the case studies [Filtering by label](https://docs.gitlab.com/development/database/filtering_by_label/), [Namespaces storage statistics](https://docs.gitlab.com/development/database/namespaces_storage_statistics/), and [Group hierarchy optimization](https://docs.gitlab.com/development/database/group_hierarchy_optimization/)
- GitLab, [Optimizing ClickHouse query execution](https://docs.gitlab.com/development/database/clickhouse/optimization/) and the ClickHouse case studies
- The owner's ClickHouse rules in `data-modeling`

## How it connects

| Skill | Relationship |
|---|---|
| [query-review](../query-review/README.md) | Reviews new queries before they ship. |
| [schema-change](../schema-change/README.md) | Ships the index or schema change the fix needs. |
| [large-table-operations](../large-table-operations/README.md) | Rewrites or backfills a large table as part of the fix. |
| [architecture-review](../architecture-review/README.md) | Decides bigger moves, such as a new store. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The steps, the page to read at each one, and the hand-back. Start here. |
| [references/verify.md](references/verify.md) | How to verify a gain, explain the number, and check side effects. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1. They need web access to read the reference docs.

| Case | What it checks |
|---|---|
| `slow-dashboard-query` | Rejects a cache hit as proof, sets a target and baseline, finds the limiter, changes one thing at a time, and verifies. |
