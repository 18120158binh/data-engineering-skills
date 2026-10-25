---
tags: [architecture-review]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our stream job looks up each person's profile in Postgres for every event, and p99 lookup latency is 400 ms under load, which stalls the job. A teammate proposes adding Redis as a cache in front of Postgres. Profiles can be merged when we learn two devices are one person. Verify this design and write your result to review.md.
