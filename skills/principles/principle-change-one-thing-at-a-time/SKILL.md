---
name: principle-change-one-thing-at-a-time
description: Apply when tuning performance, debugging, or trying fixes against a measured number. Make one change, measure it against the same baseline, keep it only if it moved the number by more than the run-to-run spread, and revert it otherwise before trying the next.
metadata:
  version: "0.1"
---

# Change one thing at a time

Make one change, measure it, and keep it only if it moved the number. Revert it before trying anything else.

**Why:** with two changes at once, you cannot tell which one helped, or whether one helped while the other hurt. Over time the kept changes fill up with ones that did nothing but still have to be maintained.

**How:**

- Fix the baseline first: the same inputs, data size, and cache state, run several times to see the spread.
- A gain smaller than that spread is not a gain.
- Log each attempt with its result, kept or reverted.

**The test:**

1. For each kept change, which number did it move, and by more than the spread?
2. Was every change that did not help actually reverted?

Related: `principle-scale-the-bottleneck`.
