---
tags: [data-modeling]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Our warehouse has a trips fact and a vehicles table. Vehicles sometimes move to another customer account, and analysts complain that old trips then show up under the new account, and vehicle names on old trips change when a vehicle is renamed. Fix the model: describe the tables and how trips get loaded so history is right. Write it to vehicle_history.md. Assume I approve your conceptual model; continue to the physical design without waiting for me.
