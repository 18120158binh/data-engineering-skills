---
tags: [pipeline-migration]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebSearch, WebFetch]
---

Our Spark Structured Streaming job writes events into a Delta table, events_v1, partitioned by user_id. The partitioning made the table slow and full of small files. Two downstream jobs read events_v1 as a stream and write Iceberg tables. We want a new table partitioned by event date without breaking those downstream streams. Write the migration plan to plan.md.
