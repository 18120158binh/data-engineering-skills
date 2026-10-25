---
tags: [database-upgrade]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

We run PostgreSQL 13 on three VMs (a primary and two replicas) behind PgBouncer, with batched background jobs that rewrite data, and we want to move to PostgreSQL 17 with as little downtime as possible. Write the upgrade plan to plan.md.
