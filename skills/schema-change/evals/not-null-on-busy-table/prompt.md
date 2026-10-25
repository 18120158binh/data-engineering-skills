---
tags: [schema-change]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

Our Postgres orders table has 400 million rows and takes about 3,000 writes per second. We want the column shipping_country to be NOT NULL. Some old rows have NULL, and one background importer still inserts orders without it. Write the migration plan, with the SQL for each step, to plan.md.
