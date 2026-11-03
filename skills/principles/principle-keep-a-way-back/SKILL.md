---
name: principle-keep-a-way-back
description: Apply before any change that is hard to undo, such as a data migration, a schema change, a database or engine upgrade, a pipeline cutover, or a deletion. Write and test how to undo each step before running it, keep the old version until the owner agrees there is no going back, and name the point after which undoing is no longer possible.
metadata:
  version: "0.1"
---

# Keep a way back

Before a step runs, know how to undo it, check that the undo works, and say when undoing stops being possible.

**Why:** an undo written during an incident is written in a hurry, has never run, and is often the moment someone finds out the backup does not restore.

**How:**

- Take a backup before the first change, and prove it by restoring it.
- Write the reverse of each step next to it, with the order and the condition for running it.
- Keep the old table, pipeline, or service, renamed or stopped rather than deleted, until the owner agrees there is no switching back.
- Do not roll back automatically onto data the new version has already changed. Decide case by case.
- Name the point of no return, put a time limit on it, and make sure the owner knows.

**The test:**

1. For each step, what undoes it, and has that undo been run?
2. When does undoing stop being possible, and who agreed to that?

**Example:** moving a table to a new layout. Copy into the new table, switch readers, and rename the old table instead of dropping it. Undo is switching readers back. The point of no return is dropping the renamed table, set for two weeks later, after the owner signs off.

Related: `principle-stay-compatible-during-rollout`, `principle-hand-production-to-a-person`.
