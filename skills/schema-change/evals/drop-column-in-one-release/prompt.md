---
tags: [schema-change]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

Review this migration before it ships with today's release, which also removes the code that used the column:

```sql
ALTER TABLE users DROP COLUMN legacy_plan;
ALTER TABLE users ADD COLUMN plan_id bigint NOT NULL DEFAULT 0 REFERENCES plans(id);
CREATE INDEX index_users_on_plan_id ON users (plan_id);
```

users has 80 million rows and is read on every request. Write the review to review.md.
