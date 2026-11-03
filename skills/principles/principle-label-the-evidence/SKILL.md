---
name: principle-label-the-evidence
description: Apply when writing a review, a design, a research brief, a catalog of lessons, or any report a decision will rest on. Label every claim with how it is known (measured, read from code or docs at a version, stated by the owner, inferred, or a vendor or third-party claim), and raise every claim that could change the decision to a primary source or a run.
metadata:
  version: "0.1"
---

# Label the evidence

Every claim a decision rests on says how it is known. A claim that could change the outcome must reach a primary source or a run before anyone relies on it.

**Why:** a guess written in the same voice as a measurement reads exactly like one. Without labels, the reader cannot tell which facts to check, and the weakest one ends up deciding.

**Labels:**

| Label | Means | Carries |
|---|---|---|
| Measured | You ran it and saw the result | The command or run, and its output |
| Read from code | From the source | The commit or release tag |
| Read from docs | From the vendor's documentation | The link and the version |
| Stated | The owner said or wrote it | Who, and when |
| Inferred | Your reading of code, history, or behavior | What you inferred it from |
| Claimed | A vendor page, blog, or forum | The link; treat it as a lead |
| Unverified | No source yet | What would verify it |

A skill may use its own label set when it needs one, such as who wrote a lesson. It still answers the same question: how is this known?

**The test:**

1. Does every claim the decision rests on carry a label?
2. Which deciding claims are still inferred or claimed, and what would settle each one?
