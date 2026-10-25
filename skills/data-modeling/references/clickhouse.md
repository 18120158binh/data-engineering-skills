# ClickHouse

Analytical tables loaded from operational sources, by batch or by CDC, and read by dashboards, a semantic layer, and ad hoc SQL.

## Engine

- Facts that can arrive more than once: `ReplacingMergeTree` on the deduplication grain, with a version column when a newer copy must win (`ReplacingMergeTree(updated_at)`).
- On a cluster, every table is `Replicated*`, materialized view targets included. A materialized view runs only on the replica that receives the insert, so a non-replicated target drifts apart across replicas.
- Plain `MergeTree` for append-only logs whose rows never repeat.

## ORDER BY

The sort key decides read speed, and for `ReplacingMergeTree` it is also the deduplication grain. Choose it from the reads in step 5 of section 1 in [SKILL.md](../SKILL.md).

- Tenant first (`tenant_id, account_id`), then the most-filtered columns, low cardinality before high.
- For entity time series: the entity, then the event time or the source id (`device_id, source_id, event_time`).
- Never lead with a UUID. It destroys locality.
- Every sort-key column is non-Nullable, with `''` or `0` standing in for absent.
- Check the deduplication grain against the source's real identity. A grain that is too coarse merges two real rows. A grain that includes a value the source can correct leaves two copies.

## PARTITION BY

Partitions are for lifecycle (TTL, DROP, REPLACE, reload), never an index. Pick the unit you drop or reload by.

1. Default, large facts: `PARTITION BY toYYYYMM(event_ts)`.
   - TTL on the same column, with `ttl_only_drop_parts = 1`.
   - A monthly reload is a REPLACE or OPTIMIZE of one partition.
2. Short retention and high volume (logs, `query_log`): `PARTITION BY toDate(ts)`, TTL in days, total partitions under about 1000.
3. Small tables (dimensions, app state, under about 10 GB): no `PARTITION BY`.
4. Small but long-lived: `toYear(ts)` or none.
5. Never a raw high-cardinality column (`user_id`, `device_id`, a timestamp).
6. Entity hash bucket (`sipHash64(id) % N`): avoid. Every insert splits into up to N parts. Use it only when loads are batched per bucket and you reload per bucket. Never with CDC or streaming inserts.
7. One insert should touch few partitions. Late data spread over many months makes many parts. The sort key, not the partition key, makes reads fast.

## TTL

- TTL on the partition column with `ttl_only_drop_parts = 1`. Without it, TTL is a merge that rewrites parts instead of dropping them.
- Adding a TTL to a large table: `materialize_ttl_after_modify = 0`, so it does not rewrite history at once.
- A raw landing table's TTL must be longer than the deepest backfill that loads into it. Otherwise the backfill is dropped at the next merge.

## Deduplication in operation

- After a load, run `OPTIMIZE TABLE ... PARTITION ID '<id>' FINAL` only on the partitions the load touched that still have more than one active part. Newest data first, one partition at a time per table. Use the real `partition_id` from `system.parts`.
- Never schedule a blanket `OPTIMIZE ... FINAL` over a whole table or a static table. It rewrites even when nothing changed.
- Reads that need exact results before a merge use `FINAL` or `argMax`, always bounded by tenant and a date range.

## Time

- Column type in UTC: `DateTime64(3, 'UTC')`. Convert source local time to UTC at extraction, with an explicit per-source timezone map and UTC as the fallback.
- Convert to the reader's zone at query time with `toTimeZone(ts, '<zone>')`. Never convert a column that was already converted.
- Anchor daily and monthly load windows to the business-local date, not the scheduler's UTC date.

## Values and types

- `Nullable` only when NULL means something ("not measured"). Counters are `DEFAULT 0`.
- Size types to the source's precision: `Float32` for a `Float32` source, never `Decimal(76, 38)` for coordinates.
- Choose codecs by measuring a real sample (a few million rows, two or three months) in a temporary table. `DoubleDelta` suits timestamps and monotonic counters only; on floats and ids it makes data larger.
- `LowCardinality(String)` only when it measurably shrinks the column.

## Loading

- Land each source in its own raw table with the source identity on every row (`source_id`, `source_host`). Ids from different sources collide.
- Keep each region's data in its own regional warehouse. Never scan or mix across regions.
- Every run re-extracts a trailing window (for example three days, no upper bound). A closed month is reloaded in full. ReplacingMergeTree absorbs the overlap, and the monthly reload also removes rows deleted at the source.
- Batch inserts: 10,000 to 100,000 rows, at most one or two inserts per second per table. Use `async_insert` when the client cannot batch.
- Record row counts per source and period before and after every load.
- Rebuild a small derived table in full: build a uniquely named temporary table, assert it is not empty, `EXCHANGE TABLES`, then drop the temporary table. Readers never see it empty.

## Aggregates

- Projection when the GROUP BY keys are a prefix of the table's ORDER BY. Write it with the exact expression the query uses (`toDate(ts)`, not `toStartOfDay(ts)`), then confirm it in `system.query_log.projections`.
- Otherwise a materialized view `TO` an explicit target table whose ORDER BY equals the GROUP BY keys: `SummingMergeTree` for sums and counts, `AggregatingMergeTree` with `-State` and `-Merge` otherwise. Read the target with `sum()` or `-Merge`, never as raw rows.

## Lookups

- Facts hold ids. Labels (product name, customer name, group) come from a dictionary at query time with `dictGet`.
- A relation that changes over time (which device is installed at which site) is a range dictionary over `[start_ts, end_ts)` rows, looked up at the event time.
