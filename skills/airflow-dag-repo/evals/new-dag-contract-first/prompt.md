---
tags: [airflow-dag-repo]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We need a new DAG in our airflow-dags repo that copies yesterday's orders from the regional Postgres into ClickHouse every night. We run it in EU and SG. Get it built. Write what you did to new_dag.md.
