---
tags: [tech-market-research]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebSearch, WebFetch]
---

We copy about 40 Postgres 15 databases into ClickHouse with a nightly cron job: COPY each table to CSV, then insert it with clickhouse-client. Dashboards are up to a day stale, and the full copy now takes 5 hours. The business wants data under 5 minutes old. We're in a pilot with 3 of the 40 databases, data must stay in the EU, and we prefer self-hosted. Research what we could use instead and write the report to cdc_report.md.
