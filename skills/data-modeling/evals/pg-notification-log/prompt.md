---
tags: [data-modeling]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We need to keep a record in Postgres of every notification our outbox job sends (email, sms, webhook, push), so support can see what a customer got and when, and so we can tell if the same notification went out twice. The outbox is a Flink job that can replay after a restart. Design the table(s) and write the DDL. Save your design to notification_log.md. Assume I approve your conceptual model; continue to the physical design without waiting for me.
