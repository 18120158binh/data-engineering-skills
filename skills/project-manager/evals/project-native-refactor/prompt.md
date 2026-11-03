---
tags: [project-manager]
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

load.py and report.py each open and close their own SQLite connection with the same boilerplate. Pull the connection handling into one db.py module that both use.
