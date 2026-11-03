---
name: principle-separate-ingest-from-query
description: Apply when designing where processed data lands and how it is read, or when one system is expected to ingest fast, serve queries, and keep history all at once. Give ingestion, stream processing, serving, and long-term storage each the layer built for its access pattern, and optimize each for its own workload.
metadata:
  version: "0.1"
---

# Separate ingest from query

Fast ingestion does not make storage and queries fast. Give each workload the layer built for it, and optimize each layer for its own access pattern.

**Why:** the layers fail in different ways. A broker that ingests a million events a second can still keep only a few days of replay. A data lake that holds petabytes can still answer slowly because of small files, metadata listing, and scans that read files they do not need. No single engine is best at all of these, and asking one engine to do everything makes it bad at most of it.

**The layers:**

| Layer | Built for | Optimize for |
|---|---|---|
| Message broker | Moving records, and replay within a retention window | Throughput, partitioning, retention |
| Stream processor | Computing as records arrive | Cost per record, state, recovery |
| Serving or analytical database | Answering queries fast | The access pattern of the main queries |
| Data lake | Keeping history cheaply, and large analytical scans | File size, partition pruning, metadata cost, compaction, data skipping |

**The idea:**

- Start from each consumer's access pattern: what it reads, how fresh it must be, and how far back it looks.
- Optimizing one layer does not speed up another. A better table format improves lake queries, and does nothing for broker or stream throughput.
- In a data lake, many small files and large metadata listings cost more as data grows. Compact files, and lay data out so queries can skip what they do not need.

**The test:**

1. For each consumer, which layer serves it, and why that layer?
2. Is any one system expected to ingest, serve, and keep history at the same time?
3. How does each layer's cost grow with data: files, partitions, metadata?
