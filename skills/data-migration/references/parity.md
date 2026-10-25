# Proving parity

Parity means the new path holds the same data as the old one, or differs only where someone wrote down why.

## What "verified" means

A migrated table or dataset is verified only when all of these hold:

1. **Both sides cover the same scope**: the same keys, time window, and tenants, read at a point where both have caught up.
2. **The rows reconcile**: every key is on both sides, or its absence has a recorded reason.
3. **The columns reconcile**: matched rows agree column by column, within a stated tolerance for noisy numbers.
4. **The data is non-trivial.** Two empty tables agree, and prove nothing.

"The new path loaded without an error" is a smoke test, not parity.

## How to compare

- **Rows.** Run a full outer join on the natural key, and sort the keys into three groups: on both sides, old only, and new only. Split the one-sided keys into accepted loss, with its reason (rows the new path is meant to drop), and missing.
- **Columns.** Compare the matched rows column by column with null-safe equality (`IS DISTINCT FROM`), with a tolerance for noisy numeric columns. Record only the columns that differ, with the key, so a difference can be traced.
- **Late data.** Give rows a grace period before you count them as missing. A row that arrives late on one side is not a gap.
- **Counts.** Compare row counts per partition or per day as a first check. They find a whole missing day at once, but they cannot show a wrong value, so do the key-level comparison too.
- **Users' data.** Around a migration of an application database, snapshot before and compare after: row counts per table, a sample of ids per user-facing table, and a few accounts read through the application's own access filters. This also catches parts of the application that silently stopped using the database.

## Every difference gets one cause

Classify each difference as exactly one of these, and write it down:

- **A bug in the new path**: fix it.
- **A defect in the old path**: prove it against the old system's own source, never against the new copy, which may have gaps of its own.
- **An intended difference**: the migration fixes a bug, or drops data on purpose. Record why.

"Close enough" is not a cause.

## Intended differences

A migration that fixes a bug is supposed to differ from the old path. List the differences you expect before you compare, and review them instead of failing on them.

## Keep the old data to compare against

Keep the old table under a new name, for example `orders_before_migration`, until the comparison is done and nobody needs the old values. Without it you can neither explain a changed number nor roll back.

## Tests that can fail

- Derive the expected values from the tool or the source, never from a copy of your own constants. A test that compares generated values with a copy of the same values passes even when both are wrong.
- Label each claim with how it was proven: run on a real system, run in a test harness, read from code, or inferred. Say what was not run.
