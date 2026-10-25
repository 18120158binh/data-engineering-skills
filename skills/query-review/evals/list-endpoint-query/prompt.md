---
tags: [query-review]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

We are adding an API endpoint that lists a project's open issues, newest first, 20 per page, with a page number. The query is:

```sql
SELECT * FROM issues WHERE project_id = $1 AND state = 'open' ORDER BY created_at DESC LIMIT 20 OFFSET ($2 - 1) * 20;
```

The only index is on (project_id). The table has 50 million rows and the largest project has 2 million issues. We tested on a dev database and it took 3 ms. Review the query and write the result to review.md.
