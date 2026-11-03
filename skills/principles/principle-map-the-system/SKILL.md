---
name: principle-map-the-system
description: Apply before changing, reviewing, or designing anything that is part of a larger system, such as a pipeline, a service, a schema, or a job. Write down the system's boundaries, the people and systems around it, what flows through it, who writes each piece of state, its side effects, how it fails, and its numbers, before judging any part of it.
metadata:
  version: "0.1"
---

# Map the system

Before you change or judge one part, write a map of the whole it belongs to.

**Why:** reading a system file by file checks each part and misses what two parts share, such as one table both write or one message both depend on. A change designed from inside one component breaks whoever sits on the other side of its boundary.

**The map:**

| Item | Write down |
|---|---|
| Boundary | What is inside, what is outside, and the contract at each crossing |
| Actors | The people and systems that read from it, write to it, or trigger it |
| Flows | What comes in, what happens to it, what goes out, and whether it moves in batches or as a stream |
| State | Every store, and the one process that writes each part of it |
| Side effects | Every write, delete, message, outside call, and lock, with what depends on it |
| Failure | What happens when each dependency is slow, down, or sends the same thing twice |
| Numbers | Volume, rate, latency, and size, each measured or labeled as an estimate |

Keep the map short enough to read in a minute. A table or a diagram is enough.

**The test:**

1. Can you list every side effect, and who depends on each one?
2. For each store, which process writes it?
3. What happens when the slowest dependency stops answering?

Related: `principle-size-the-workload-first` for the numbers.
