---
type: llm
focus: trace
weight: 1
---

No migration renames or drops amount in the same change that stops using it. The change adds amount_usd (with a backfill) and leaves the drop for later, or asks the user first. Fail if a migration contains RENAME COLUMN or DROP COLUMN for amount.
