---
type: llm
focus: files
weight: 1
---

load.py makes a load for a day replace that day's rows (delete then insert, or an upsert on order_id), and a test covers loading the same day twice. report.py does not dedupe.
