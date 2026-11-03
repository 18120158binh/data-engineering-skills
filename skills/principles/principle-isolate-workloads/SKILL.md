---
name: principle-isolate-workloads
description: Apply when many pipelines or teams share a cluster or platform, when choosing an autoscaling policy, or when one workload's backlog slows others. Scale along the axis the workload can use (more workers only when there are more independent units, bigger workers otherwise), and isolate workloads by priority, quota, and capacity class so one cannot starve another.
metadata:
  version: "0.1"
---

# Isolate workloads

On a shared platform, scale each workload along the axis it can actually use, and keep workloads from taking each other's capacity.

**Why:** adding workers to a job whose parallelism is capped, for example by its partition count, adds cost and no throughput. And when every pipeline shares one pool without limits, a backlog in a pipeline that can wait slows the ones that cannot.

**Scaling axis:**

- **Add workers** when there are more independent units of work than workers (`principle-partition-by-independent-work`).
- **Make workers bigger** when the number of units is fixed but each needs more CPU or memory.
- **Scale on the real signal**: consumer lag and load per worker, not average CPU across the cluster. Load is often uneven between workers.

**Isolation:**

- Group workloads by how much delay they can take, for example seconds, minutes, and hours, and give each group its own priority, quota, and capacity class, such as reserved or on-demand machines for the urgent group and cheaper interruptible machines for the patient one.
- Cap what one workload can consume, so its backlog stays its own problem.
- Give the platform a control plane that manages pipelines' deployment, resources, and limits, rather than leaving each team to size its own.

**The test:**

1. Would one more worker increase this job's throughput, or sit idle?
2. If the largest workload builds a backlog, which other workloads slow down?
3. Do the most urgent pipelines have capacity no other workload can take?

**Read:** Apache Kafka, [documentation](https://kafka.apache.org/documentation/) (consumer groups and partitions).

Related: `principle-partition-by-independent-work`, `principle-scale-the-bottleneck`.
