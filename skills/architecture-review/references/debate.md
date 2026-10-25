# Debate prompts

Fill in the parts in angle brackets. Every subagent gets the frame from step 1 and the grounding from step 2 as files or inline text, and runs read-only.

## Advocate

```
You argue for one option in an architecture decision. Other advocates argue for the other options, and you will not see their work.

Decision: <one sentence>
Frame: <questions, numbers, constraints, owner>
Grounding: <current design, history, measured numbers, each labeled measured / read from code or docs / inferred>
Your option: <the option, in a paragraph>
Criteria: <paste references/criteria.md>

Write:
1. The case for your option, criterion by criterion. Skip the criteria that do not apply, and say which.
2. For each claim, the evidence: a measurement, a doc or source at a version, an incident, or "inferred, not run".
3. The strongest case against your option, as a fair opponent would put it.
4. The conditions under which your option is the wrong choice.
5. The one measurement or prototype that would most change the outcome.

Do not argue against the other options. Argue for yours, honestly.
```

## Challenger

```
You attack every option in an architecture decision. You are not on any side. Your job is to find what each option hides.

Decision, frame, grounding: <as above>
Options: <each option, in a paragraph>
Red flags: <paste references/red-flags.md>

For each option, find:
1. The failure it hides: walk a concrete event (a retry, a replay, a late record, a slow dependency, an upgrade, a second tenant) through it to a bad end state.
2. The number it needs that nobody measured.
3. The cost it moves somewhere else: to operations, to another team, to the next change.
4. Any red flag it shows.

Trace each failure step by step. "This could fail" without the path is not a finding. Say how likely each one is and how much it would cost.
```

## Rebuttal

```
You argued for <option>. A challenger raised these points against it: <the challenger's findings for this option>.

For each point, either:
- concede it, and say whether the option survives with a rule that handles it, or
- refute it with evidence, tracing why the failure does not reach.

Do not restate your original case.
```
