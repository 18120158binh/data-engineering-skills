---
name: principle-budget-the-state
description: Apply when designing or changing a stateful stream job, a window, a join, a deduplication, or anything that keeps data per key between records. Budget the state's size, access rate, lifetime, checkpoint cost, and recovery time before building it, because a stateful step costs far more than a stateless one.
metadata:
  version: "0.1"
---

# Budget the state

Before you add state to a stream job, write down what it holds, how big it gets, how long each entry lives, and how long it takes to restore.

**Why:** a stateful step does more work than a stateless one. It reads and writes state for each record, its state is snapshotted at every checkpoint, and after a failure it must be restored before the job runs again. A job that filters a million records a second may manage far fewer when each record also updates per-user state.

**The budget:**

- **Size:** number of keys × bytes per key. Say whether it fits in memory, or needs a disk-backed state backend, which costs serialization and disk reads on every access.
- **Access:** state reads and writes per record, and any call to an outside system while the record waits.
- **Lifetime:** the window, or the time to live, after which an entry is dropped. State without a limit grows until it fails.
- **Checkpoints:** how long a checkpoint takes and how large it is as state grows, and whether incremental checkpoints apply.
- **Recovery:** how much state a failed worker must reload, and how long that takes. This feeds `principle-plan-for-catch-up`.
- **Rescaling:** state is redistributed when parallelism changes. Check that the job can rescale from a savepoint.

**The test:**

1. What does the state hold per key, and how many keys exist at peak?
2. When is each entry removed?
3. How long do checkpoint and restore take at the expected state size, measured?

**Read:** Apache Flink, [Stateful stream processing](https://nightlies.apache.org/flink/flink-docs-stable/docs/concepts/stateful-stream-processing/), [State backends](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/state_backends/), [Working with state](https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/fault-tolerance/state/) (including state time to live), and [Tuning checkpoints and large state](https://nightlies.apache.org/flink/flink-docs-stable/docs/ops/state/large_state_tuning/).

Related: `principle-cut-work-per-event`.
