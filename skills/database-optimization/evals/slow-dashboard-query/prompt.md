---
tags: [database-optimization]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

A dashboard query on our Postgres database got slow, about 8 seconds. A teammate already added three indexes and a Redis cache in front of it, and says it is faster now because the second load is instant. The query sums order amounts per day for one account over 90 days. Write how you would optimize it and how you would prove the result to plan.md.
