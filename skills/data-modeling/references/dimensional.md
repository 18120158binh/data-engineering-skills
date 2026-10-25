# Facts and dimensions

How analytical data is shaped, whatever the store.

## Grain

- State the grain of every table and view: "one row is one order line", "one row is one session per clock hour it overlaps". Every measure must make sense at that grain.
- Count rows to count entities. Never `countDistinct` a derived id such as a per-customer rank: it returns the largest rank, not the number of rows.
- When a fact spans time buckets (a session across several hours), give the split its own grain and table. Pro-rate the measures so they sum exactly to the parent, and clamp runaway rows (for example at 168 hours).
- Rows that pad a spine (one per entity per day with id 0) are excluded from every count unless the measure means to count them.

## Facts

- A fact row holds: its natural identity (what deduplication uses), the surrogate keys of its dimensions, the event time, and the measures.
- Measures are additive ingredients: sums and counts. Compute a ratio at query time as `sum(a) / nullIf(sum(b), 0)`. A ratio of sums is not an average of ratios.
- Record each measure's base unit in metadata and convert in the model. Never relabel a column to change its unit, and never infer a unit from a name.
- Do not copy display labels into facts. They come from the dimension at query time.

## Dimensions

- A dimension row holds: its surrogate key, the natural key of the entity, and the descriptive attributes.
- When an attribute changes and history matters, add a new row with a new surrogate key (type 2), with `valid_from` and `valid_to` and an open end at the type's maximum: `'9999-12-31'` in Postgres, `'2299-12-31 23:59:59'` for ClickHouse `DateTime64` (and `'2106-02-07'` for `DateTime`), which cannot store year 9999. Rebuild these rows in full from an append-only history of changes.
- When loading a fact, look up the dimension row that was valid at the event time and store its surrogate key. The fact then always points at the owner, group, or name as it was when the event happened. A device that moved to another account keeps its old events with the old account.
- Collapse a dimension to one row per join key before joining it to a fact. A dimension with several rows per key multiplies every additive measure.
- A real many-to-many relation gets a bridge table, modeled on purpose.

## Names

- Lead a table or view name with its class: `historical_`, `today_`, `live_`, `dim_`.
- Never put a retention window or duration in a name (`orders_1year`). The name lies the day retention changes.
- Do not name a column after a time granularity token (`hour`); use `hour_of_day`.
- Put the environment in names that differ by environment (`view_orders_${env}`), and never hardcode `prod`.

## Isolation

- Put tenant isolation in the table or view itself, as a filter on the tenant columns that fails closed, not through a join. A view isolated through a join inherits the join's grain and can leak rows.
- Always bound heavy reads (`FINAL`, `uniqExact`, wide scans) by tenant and a date range.
