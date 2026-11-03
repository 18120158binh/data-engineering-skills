---
name: principle-scale-the-bottleneck
description: Apply when a pipeline lags, shows backpressure, or someone proposes adding resources to it. A multi-step pipeline runs only as fast as its slowest step, after accounting for how filters, joins, and aggregations change the record rate between steps. Find that step from measurements, and add capacity there and nowhere else.
metadata:
  version: "0.1"
---

# Scale the bottleneck

A pipeline runs only as fast as its slowest step. Find that step from measurements, and add capacity only there.

**Why:** capacity added anywhere else is wasted. More brokers do not help when the enrichment step is full, and more consumers do not clear a backlog when the sink writes slower than the source reads.

**How to find it:**

- Write each step's capacity in the same unit of work, and convert by the rate change between steps: a filter that keeps 10% lowers the load on every later step, and a join that emits three rows per record triples it.
- Read the signals, not CPU averages: consumer lag, the busy and backpressured time of each operator, sink latency, and checkpoint duration. The bottleneck is usually the first operator that is busy while the ones before it are backpressured.
- Change one thing, and measure again. The bottleneck moves once you fix it.

**The test:**

1. Which step limits throughput, and what measurement shows it?
2. Will the proposed resources go to that step?
3. After the change, where is the new bottleneck?

**Example (illustrative numbers):** source 1.5M events/s, transform 1.2M, stateful enrichment 0.8M, sink 1.1M. The pipeline tops out at 0.8M events/s, and adding brokers changes nothing. If input runs at 0.7M events/s but the sink writes only 0.5M, the backlog grows by 200,000 events every second, or 60 million in five minutes.

**Read:** Apache Flink, [Monitoring back pressure](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/monitoring/back_pressure/).

Related: `principle-cut-work-per-event`, `principle-change-one-thing-at-a-time`.
