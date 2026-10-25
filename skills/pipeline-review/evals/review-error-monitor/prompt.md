---
tags: [pipeline-review]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Review this monitoring DAG before it ships. It reports new errors from our replication tool to a chat room every hour. List every problem, why it matters, and the fix. Write the review to review.md.

Input files: dags/error_monitor.py
