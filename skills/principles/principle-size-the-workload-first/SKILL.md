---
name: principle-size-the-workload-first
description: Apply before choosing machines, worker counts, partition counts, or an architecture for a data system. Write the workload down as numbers (records and bytes per second, average and peak, latency target, retention, recovery time) and show the arithmetic that proves the capacity is enough.
metadata:
  version: "0.1"
---

# Size the workload first

Before you choose how many machines, workers, or partitions a system needs, write down what it must handle, as numbers, and derive the capacity from them.

**Why:** a design chosen before the workload is known is a guess. The same "one million events per second" is about 100 MB/s at 100-byte events and about 10 GB/s at 10 KB events, a hundredfold difference in network, storage, and cost.

**The numbers to write down:**

- Throughput in records per second **and** bytes per second, average and peak.
- Latency target, as a percentile such as p99.
- Fan-out: how many pipelines or consumers read each record.
- Growth per day, and how long data is kept.
- Recovery: how long an outage may last, and how fast the backlog must clear (see `principle-plan-for-catch-up`).

**Then derive, showing the arithmetic:**

- Bandwidth = records per second × average record size, before replication and fan-out.
- Storage = bytes per day × retention days × replication factor.
- Workers = peak records per second ÷ measured records per second per worker, plus headroom.
- Per-worker throughput comes from a benchmark with production-like data and logic, never from a generic number for the engine.

**The test:**

1. Can you state peak load in both records and bytes per second?
2. Is every capacity number derived from a measurement, with the arithmetic written down?
3. Does the plan include headroom for peaks and for recovery?

**Example (illustrative numbers):** a peak of 1,000,000 events/s at 1 KB each is about 1 GB/s, or about 86 TB a day before replication. If a benchmark shows one worker handles 10,000 events/s with this logic, the floor is 100 workers, and 130 with 30% headroom.

**Read:** Apache Flink, [Tuning checkpoints and large state](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/large_state_tuning/), section "Capacity planning".

Related: `principle-scale-the-bottleneck` (capacity of the whole pipeline).
