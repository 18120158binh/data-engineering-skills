---
name: principle-extract-shared-rules
description: Apply when writing or reviewing skills and deciding whether a rule belongs inside a workflow or in its own principle. Split a rule out when two or more skills need it, it can be applied on its own with a reason and a test, and it does not depend on one workflow's order or tools. Then replace every copy with a citation by name.
metadata:
  version: "0.1"
---

# Extract shared rules

A rule gets its own principle when more than one skill needs it and it makes sense on its own. Otherwise it stays in the workflow that uses it.

**Why:** a rule copied into several skills drifts, and agents follow whichever copy they read last. A rule split out too early becomes a file nobody loads, and a workflow the reader must follow across many files.

**Split it out when:**

- two or more skills state it, or would;
- it can be applied outside any workflow, such as in a review comment;
- you would cite it by name in a review.

**Keep it in the workflow when:**

- one step of one workflow uses it;
- it only makes sense after the previous step;
- it names a specific tool's command or setting.

**How to extract:**

1. Write the principle: the rule, its reason, its test, an example.
2. In each skill that held a copy, replace it with the principle's name, and keep only what is specific to that skill.
3. Search the skills for the rule's key words, and check that no copy remains.

**The test:**

1. How many skills state this rule now?
2. Can someone apply it without reading the workflow around it?
3. After extracting, does any copy remain?
