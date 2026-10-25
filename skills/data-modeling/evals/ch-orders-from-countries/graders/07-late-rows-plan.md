---
type: llm
focus: trace
weight: 1
---

The design explains how late or corrected rows are handled (re-extract window or reload) and runs OPTIMIZE only on touched partitions, not a blanket OPTIMIZE FINAL.
