# Backfill plan for connecting new source databases

When a new source database is connected we copy its history into `warehouse.orders_raw` (see target_table.sql).

- For each new database, copy every monthly partition from the oldest one, up to 12 months back.
- Start one copy job per database per month, all at once, so onboarding finishes quickly. We onboard up to 8 databases per run.
- If a copy fails, retry it up to 5 times right away.
- Once all copies are started, mark the databases as replicated in the inventory.
