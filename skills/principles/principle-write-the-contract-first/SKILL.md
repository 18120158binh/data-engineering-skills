---
name: principle-write-the-contract-first
description: Apply before writing or changing a pipeline, job, DAG, service, or any code whose behavior others rely on. Write down what it must do (inputs, outputs, limits, failure and rerun behavior, approval points) and get the owner's confirmation before writing code. A change in behavior starts as a change to the contract, and each binding rule gets a test.
metadata:
  version: "0.1"
---

# Write the contract first

Before the code, write what it must do and have the owner confirm it. Any change in behavior starts as a change to that contract.

**Why:** when code comes first, it becomes the specification by default, and its mistakes become requirements. A contract written afterwards from the code repeats whatever the code gets wrong.

**What a contract binds:**

- the inputs, and which invalid inputs must stop the run;
- what it writes or sends, and what stays unchanged after a failure;
- what a rerun does;
- every limit, and every point where a person must approve;
- every sentence with "must", "never", or "only".

Names, file layout, and helper steps stay free.

**How:**

- Write one test for each binding rule.
- Change the contract and the code in the same merge request.
- If the code needs an effect no rule covers, such as a new write or call, add the rule first.

**The test:**

1. Which rule in the contract does each effect of the code satisfy?
2. Did the owner confirm the contract, and when?
3. Does every binding rule have a test?

Related: `principle-read-the-code-ask-the-owner`.
