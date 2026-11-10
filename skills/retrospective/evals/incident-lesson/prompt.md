---
tags: [retrospective]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Last week the change-data-capture feed from our orders database broke. These are my notes from the incident channel, in the order things happened to us. Write it up as a lesson for the team in lesson.md.

- 02:41 Tue 2026-10-06, the Debezium connector for project Lotus failed on resume with:
  `ERROR: can no longer get changes from replication slot "debezium_orders"`
  `DETAIL: This slot has been invalidated because it exceeded the maximum reserved size.`
- The warehouse had no new orders from 01:50, when the connector was paused on purpose (see below). That part was planned. The unplanned outage started at 02:31, when the slot was lost, so the resumed connector had nothing to read from.
- Postgres log on pg-orders-01 (Postgres 16) at 02:31:
  `LOG: invalidating obsolete replication slot "debezium_orders"`
  `DETAIL: The slot's restart_lsn 3A/1F000000 exceeds the limit by 1342177280 bytes.`
- `max_slot_wal_keep_size` on pg-orders-01 is 20GB.
- The connector had been paused from 01:50 for a Kafka Connect upgrade, and was resumed at 02:40.
- At 02:10 a backfill started: one UPDATE over 180 million order_items rows to fill a new column. It wrote about 64 GB of WAL in 35 minutes.
- Our only CDC alert is on consumer lag in seconds, and it was muted for the upgrade window. Nothing watches `pg_replication_slots.wal_status` or `safe_wal_size`.
- Recovery: dropped and recreated the slot, then ran a Debezium initial snapshot of the 4 CDC tables, 03:05 to 05:20. The feed was back at 05:20: unplanned outage 02:31 to 05:20, warehouse behind from 01:50 to 05:20 in total.
- Checked after: row counts and the sum of order totals per day, Postgres vs warehouse, for 2026-09-01 to 2026-10-06: 0 differences. The 38,214 orders written during the gap are all in the warehouse.
- Done since: an alert when `wal_status` is `unreserved` or `safe_wal_size` drops below 5 GB; the backfill script now updates in batches of 50,000 rows and pauses while the slot holds more than 8 GB of WAL. In a test backfill the slot's retained WAL peaked at 7.6 GB.
- Not done: raising the cap to 60 GB needs a disk resize. The DBA team owns it, ticket OPS-1182.
