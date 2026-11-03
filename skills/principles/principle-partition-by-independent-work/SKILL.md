---
name: principle-partition-by-independent-work
description: Apply when scaling a pipeline or job by adding workers, choosing Kafka partition counts or a Flink keyBy, or seeing some workers overloaded while others idle. Scale out only along units of work that can run independently, choose the key that keeps business semantics, and check for hot keys and skew.
metadata:
  version: "0.1"
---

# Partition by independent work

Adding workers helps only when the work splits into units that can run independently. Find those units first, and choose the partition key from them.

**Why:** parallelism is capped by the number of independent units. In a classic Kafka consumer group, each partition is read by at most one member, so eight consumers on four partitions leave four idle. And work that must run in order for one key runs on one worker, however many workers there are.

**The idea:**

- Ask what can be processed independently without changing the result: per user, per order, per region, per time window.
- Choose the partition or `keyBy` key from that answer. The key also decides ordering: records with the same key stay in order, and records with different keys do not.
- Make the partition count at least the parallelism you will need at peak. Raising it later reshuffles which key lands where.
- Check the key's distribution on real data. One hot key, such as a very large tenant, keeps one worker busy while others idle.

**When one key is too hot:**

- Choose a finer key, if the business result allows it.
- Split additive work into a partial aggregation per sub-key and a final aggregation per key.
- Ask whether every step needs per-key order. Often only one step does.

**The test:**

1. What is the unit of independent work, and is the key built from it?
2. What is the most work one key produces at peak, and can one worker handle it?
3. Is the partition count at least the parallelism needed at peak?

**Read:** Apache Kafka, [documentation](https://kafka.apache.org/documentation/) (topics, partitions, and consumer groups), and Apache Flink, [DataStream operators](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/overview/) (`keyBy`).

Related: `principle-isolate-workloads`.
