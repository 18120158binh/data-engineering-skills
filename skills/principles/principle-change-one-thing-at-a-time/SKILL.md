---
name: principle-change-one-thing-at-a-time
description: Apply when tuning performance, debugging, trying fixes against a measured number, or comparing any run with a baseline (an evaluation, a benchmark, a quality score, a migration parity check). Make one change, measure it against the same baseline, keep it only if it moved the number by more than the run-to-run spread, and revert it otherwise before trying the next. A comparison counts only when the baseline and the run differ in nothing but the change.
metadata:
  version: "0.2"
---

# Change one thing at a time

Make one change, measure it, and keep it only if it moved the number. Revert it before trying anything else.

**Why:** with two changes at once, you cannot tell which one helped, or whether one helped while the other hurt. Over time the kept changes fill up with ones that did nothing but still have to be maintained.

**How:**

- Fix the baseline first: the same inputs, data size, and cache state, run several times to see the spread.
- A gain smaller than that spread is not a gain.
- Log each attempt with its result, kept or reverted.
- Record, with the baseline and with each run, everything that could move the number besides the change: configuration, inputs, the environment and build version, and the evaluator or grader (a model, a rubric, a script). Refuse a comparison where any of these differ, or name the difference beside the result. A run compared with a baseline that differed in one routing setting reported a regression the change did not cause.
- If the environment can change during a run, record its version per item.

**The test:**

1. For each kept change, which number did it move, and by more than the spread?
2. Was every change that did not help actually reverted?
3. Were the baseline and the run identical in everything but the change?

Related: `principle-scale-the-bottleneck`.
