---
tags: [airflow-dag-repo]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our production Airflow runs 2.9.3. Add a DAG that uses the Airflow 3 `@asset` decorator to refresh the daily_sales table whenever the orders asset updates. Assume the contract is approved: it says refresh daily_sales after orders updates, in every region. Write the plan and code notes to asset_dag.md.
