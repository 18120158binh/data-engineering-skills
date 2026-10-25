---
tags: [pipeline-review]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Review this backfill DAG a teammate wrote. It copies history for every source server into the warehouse. List every problem, why it matters, and the fix. Write the review to review.md.

Input files: dags/backfill_servers.py
