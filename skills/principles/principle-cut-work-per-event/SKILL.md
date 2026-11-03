---
name: principle-cut-work-per-event
description: Apply before adding machines to a slow or expensive pipeline. Reduce the work each record costs first, by filtering early, aggregating before expensive steps, batching I/O, and keeping running state instead of recomputing, as long as no downstream consumer needs the records you drop.
metadata:
  version: "0.1"
---

# Cut work per event

Before you add machines, make each record cheaper to process. Halving the cost per record doubles capacity without a new machine.

**Why:** cost scales with records processed times cost per record. Adding machines only divides the first factor among more hosts, while every saving on the second applies to every record the system will ever see.

**The levers:**

- **Filter early**, before enrichment, lookups, and writes, so expensive steps see only the records that need them. Check that the filter itself is cheap. A filter that queries a database can become the bottleneck.
- **Aggregate before expensive steps**, when the result only needs totals per key and window.
- **Batch I/O.** One request carrying many records instead of one request per record. Too small a batch saves little, and too large a batch costs memory and latency.
- **Keep running state instead of recomputing.** Update a count per user and window as records arrive, instead of querying the full history for every record.
- **Avoid a call to an outside system per record.** Cache, batch, or move the data into the job's state.

**The limit:** never drop or aggregate away records that a consumer needs one by one, for audit, replay, or a business process. Check every consumer before you cut.

**The test:**

1. What does one record cost in CPU, I/O, and network at each step?
2. Which step does work that a later step throws away?
3. Could the same result come from fewer calls, fewer bytes, or less recomputation?

**Example (illustrative numbers):** at 1,000,000 events/s, if only 10% matter to the use case, filtering before enrichment means enrichment handles 100,000 events/s instead of 1,000,000.

**Read:** Apache Kafka, [documentation](https://kafka.apache.org/documentation/), the producer settings for batching and compression.

Related: `principle-scale-the-bottleneck` (where the saving matters), `principle-budget-the-state` (what running state costs).
