---
name: principle-plan-for-catch-up
description: Apply when sizing a streaming or batch system, setting its recovery objectives, or choosing its delivery guarantees. Provision capacity above the input rate so a backlog from an outage drains in a stated time, measure that capacity with checkpointing on, and make sure a failure neither loses nor duplicates data at the sinks.
metadata:
  version: "0.1"
---

# Plan for catch-up

A system that just keeps up with its input never recovers from an outage. Provision capacity above the input rate, sized so a backlog drains within a stated time, and make sure the recovery itself neither loses nor duplicates data.

**Why:** input keeps arriving while a job is down and while it restarts. At capacity equal to the input rate, the backlog never shrinks. The drain rate is the capacity minus the input, not the capacity itself.

**The arithmetic:**

- Backlog = input rate × outage time.
- Drain rate = capacity − input rate.
- Catch-up time = backlog ÷ drain rate.

Measure capacity with checkpointing on, because checkpoints use resources too.

**Correctness during recovery:**

- A restart replays records from the last checkpoint, so every write must be safe to repeat.
- A checkpoint does not make a sink exactly-once by itself. That depends on the connector and how the sink commits. Check each sink's guarantee.
- Retry with limits and backoff. An unbounded retry loop turns one bad record into an outage.

**The test:**

1. If the job stops for the longest outage you plan for, how long does catch-up take, from the arithmetic above?
2. Is that within the recovery objective?
3. For each sink, what happens to a record replayed after a restart: written once, written twice, or lost?

**Example (illustrative numbers):** input 700,000 events/s, a five-minute outage, capacity 1,000,000 events/s after restart. The backlog is 210 million events, the drain rate 300,000 events/s, so catch-up takes 700 seconds, almost 12 minutes, before any restore time.

**Read:** Apache Flink, [Tuning checkpoints and large state](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/large_state_tuning/), section "Capacity planning", and [Fault tolerance guarantees of data sources and sinks](https://nightlies.apache.org/flink/flink-docs-stable/docs/connectors/datastream/guarantees/).

Related: `principle-size-the-workload-first`, `principle-budget-the-state` (restore time).
