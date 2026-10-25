---
tags: [large-table-operations]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash, WebFetch, WebSearch]
---

Review this backfill job before we run it on our 900-million-row events table in Postgres:

```python
offset = 0
while True:
    rows = db.query("SELECT id, payload FROM events WHERE region IS NULL ORDER BY created_at LIMIT 10000 OFFSET %s", offset)
    if not rows:
        break
    for row in rows:
        try:
            db.execute("UPDATE events SET region = %s WHERE id = %s", derive_region(row.payload), row.id)
        except Exception:
            pass
    offset += 10000
```

Write the review to review.md.
