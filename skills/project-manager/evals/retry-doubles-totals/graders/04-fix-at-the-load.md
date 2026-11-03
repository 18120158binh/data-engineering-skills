---
type: llm
focus: trace
weight: 1
---

The fix is in load.py and makes a repeated load of the same day produce the same rows, for example by deleting that day's rows and inserting in one transaction, or by an upsert keyed on order_id. Fail if the fix only dedupes or uses DISTINCT in report.py.
