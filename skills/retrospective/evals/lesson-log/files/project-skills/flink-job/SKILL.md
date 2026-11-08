---
name: flink-job
description: Suspend, resume, or upgrade one of the orders-stream Flink jobs on the staging cluster.
---

# Flink job operations

- Suspend: set `spec.job.state: suspended` in the job's overlay, commit, and wait for the operator to report SUSPENDED.
- Resume: set `spec.job.state: running`, commit, and wait for RUNNING and STABLE.
- Upgrade: change the image tag; the operator takes a savepoint and restarts the job from it.
