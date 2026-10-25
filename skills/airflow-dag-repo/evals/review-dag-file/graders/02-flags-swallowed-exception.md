---
type: llm
focus: trace
weight: 1
---

review.md flags the except block that logs and returns instead of raising, because the failed task looks like success and Airflow does not retry or alert.
