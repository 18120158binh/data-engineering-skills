---
name: principle-stay-compatible-during-rollout
description: Apply when changing a schema, an API, a message format, a table a stream reads, or a pipeline output while the old version is still running or still read. Each step must run correctly against both versions; add the new shape before moving users to it, and remove the old shape only after evidence shows nothing uses it.
metadata:
  version: "0.1"
---

# Stay compatible during rollout

While old and new versions run at the same time, every step must work for both. Add the new shape, move everyone to it, and remove the old shape last.

**Why:** deploys, migrations, and consumer switches never happen at once. A step that only works for the new version breaks everything still on the old one until the switch ends, and some of those breaks, such as a dropped column, cannot be reversed.

**How:**

- Split the change into three releases: add the new shape, move readers and writers to it, then remove the old shape.
- Check each release before starting the next.
- Show that nothing uses the old shape before you remove it, from query logs, consumer offsets, or access logs. Do not assume it.

**The test:**

1. If the old version runs against this step for an hour, what fails?
2. What evidence shows nothing still uses the old shape?

**Example:** renaming a column. Add the new column and write to both. Backfill it. Switch reads to the new column. Stop writing the old one. Drop it in a later release, once the logs show no reads.

Related: `principle-keep-a-way-back`.
