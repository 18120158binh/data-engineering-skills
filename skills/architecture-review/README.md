# architecture-review

Verifies or chooses a data architecture by debate: frame the decision with numbers, ground it in the current system and its history, lay out at least two structurally different options, have independent advocates and a challenger argue them, judge against explicit criteria, and write a decision record that only the owner accepts.

## When to use it

Use it when you design or change how data moves or is stored, review someone's design, choose between approaches, or revisit a decision after an incident. Typical questions: "should we use X", "is this design OK", "Kafka or CDC", "how should this scale".

## What it believes

- Frame first, with numbers. A missing number is an open question for the owner, never a guess taken from code.
- Always compare at least two whole shapes, including the baseline of fixing the current design. "Defer with an alarm" is a real option when the problem has not been seen yet.
- Prefer at-least-once with idempotent writes over exactly-once, one owner per key over locks, and one decider over copies that drift.
- Every new moving part must be created, secured, watched, and upgraded, so it needs evidence that the problem is real.
- Label every fact as measured, read from code or docs, or inferred. A measured result beats an argument.
- Advocates argue independently, and a challenger, on a different model when one is available, attacks every option.
- An agent proposes. Only the owner accepts a decision, and an accepted record is never edited to reverse it.

## How it connects

| Skill | Relationship |
|---|---|
| [tech-market-research](../tech-market-research/README.md) | Supplies the candidates and facts when an option needs a tool. |
| [data-modeling](../data-modeling/README.md) | Owns the tables inside the design. |
| [pipeline-review](../pipeline-review/README.md) | Checks the built pipeline against the guarantees the decision record lists, and sends design-level findings back. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The six steps and the hand-back. Start here. |
| [references/criteria.md](references/criteria.md) | The criteria to score options on, and the stance on each. |
| [references/red-flags.md](references/red-flags.md) | Shapes to reject or revise on sight. |
| [references/debate.md](references/debate.md) | Prompts for the advocates, the challenger, and the rebuttal. |
| [references/decision-record.md](references/decision-record.md) | The decision record rules and template. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1.

| Case | What it checks |
|---|---|
| `exactly-once-for-duplicates` | Rejects exactly-once as a fix for a Postgres sink, chooses idempotent writes, and leaves the record proposed. |
| `cache-on-hot-path` | Frames the numbers, compares a cache with other shapes, flags a cache that drifts after merges, and debates. |
