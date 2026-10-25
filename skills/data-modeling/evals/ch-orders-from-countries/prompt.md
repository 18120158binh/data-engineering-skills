---
tags: [data-modeling]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Design a ClickHouse table for orders replicated from 6 shop Postgres databases in different countries (each database stores local time, order ids are only unique per database). Loads come from a CDC tool at a few inserts per second. Dashboards ask per merchant per day and per month, and we keep 13 months. Write the DDL and explain your choices in orders_table.md. Assume I approve your conceptual model; continue to the physical design without waiting for me.
