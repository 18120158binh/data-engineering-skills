---
name: principle-analyze-trade-offs
description: Apply when choosing between designs, tools, or approaches, or when someone proposes one option without alternatives. Write the criteria before the options, compare at least two whole options including keeping what exists, score each against the same criteria with evidence, and state what the chosen option costs.
metadata:
  version: "0.1"
---

# Analyze trade-offs

Decide the criteria first, then compare whole options against them. Keeping the current design is always one of the options, and every option states its cost.

**Why:** criteria written after the options tend to describe the favorite. A comparison without the current design only shows that the new one beats nothing. An option that lists no cost has a cost nobody has found yet.

**How:**

- Take the criteria from the decision's numbers and constraints, and say which few of them decide this case.
- Make the options different in shape, not tunings of one idea. Add "wait, with an alarm" when the problem has not happened yet: build the alert that would show it, and decide when it fires.
- Score each option criterion by criterion, and label each piece of evidence (`principle-label-the-evidence`).
- Sort every objection into one of four: it changes the decision, it becomes a rule the chosen design must follow, it is a cost we accept, or it is dismissed with a reason.
- When the evidence cannot separate two options, name the measurement or prototype that would, and make that the next step.

**The test:**

1. Were the criteria written down before the options?
2. Is the current design one of the options?
3. What does the chosen option cost, and who pays it?
4. What new evidence would reverse the choice?

Related: `principle-follow-the-common-shape`.
