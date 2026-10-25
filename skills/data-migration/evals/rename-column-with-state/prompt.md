---
tags: [data-migration]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We want to rename the column customer_email to email in our Postgres orders table. A Flink job writes the table, and a second Flink job keeps a per-customer cache of the email in its keyed state. Two dashboards read the column. Write the migration plan to plan.md.
