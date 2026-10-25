---
tags: [data-modeling]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Staff manage email templates in our admin app (Postgres table email_templates, names must be unique). They want to delete templates but also undo a delete made by mistake. Only the admin app and the notification sender read this table. Change the schema and describe how create, delete and restore work. Write it to templates.md. Assume I approve your conceptual model; continue to the physical design without waiting for me.
