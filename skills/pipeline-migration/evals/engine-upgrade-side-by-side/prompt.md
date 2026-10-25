---
tags: [pipeline-migration]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebSearch, WebFetch]
---

We need to upgrade the ClickHouse cluster that runs our hourly aggregation pipeline from 23.8 to 24.8. The pipeline fills summary tables through materialized views, and two downstream jobs read those tables to build reports and push numbers to a billing system. Write the upgrade plan to plan.md.
