---
tags: [data-modeling]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We're launching a referral program. Customers invite friends with a link; when an invited friend makes a first purchase, both get a reward, and invited friends can invite others too. Marketing wants to see referral chains (who brought in whom, how deep), fraud wants to spot rings of accounts that refer each other, and finance wants monthly reward totals by campaign. We use Postgres for the app and ClickHouse for analytics. How should we model this? Write your answer to referral_model.md.
