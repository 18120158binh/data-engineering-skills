---
tags: [architecture-review]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

After every restart, our Flink job writes duplicate rows into a Postgres table of sent notifications. The team proposes turning on Kafka exactly-once transactions to fix it. Review the proposal and write a decision record to decision.md. The job reads from Kafka and writes to Postgres with a plain INSERT keyed by a generated UUID.
