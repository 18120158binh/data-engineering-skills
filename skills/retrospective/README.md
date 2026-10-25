# retrospective

Looks back at finished work (a session, a pull request, a round of fixes, an incident, or a design decision that has been running for a while) and turns each lesson into one change in the file that owns it.

## When to use it

Use it after shipping, after an incident, at the end of a round of work, or when a decision's revisit condition fires. Typical requests: "retro", "what did we learn", "look back on this", "why do we keep hitting this".

## What it believes

- A retrospective that changes nothing did not happen.
- Facts, not impressions: reversals, rework, defects caught late, and waits, each with a commit, comment, or log line.
- Ask why until you reach the process: a brief, a contract, a skill, a check, a missing number, or a shared premise.
- A one-off is not a lesson. Keep a lesson that happened twice, or once at a high cost.
- Prefer structure over text. If a test, a lint, or a template default can stop the mistake, change that and add no sentence.
- Each lesson goes to the one place that owns it, and shared files change only with the owner's approval, in their own pull request.
- Check whether the last retrospective's actions helped, then keep, adjust, or revert them.

## How it connects

| Skill | Relationship |
|---|---|
| [knowledge-harvest](../knowledge-harvest/README.md) | Gathers the facts when the period is long or spans many repositories. |
| [architecture-review](../architecture-review/README.md) | Takes a decision the retrospective shows was wrong, or whose revisit condition fired. |
| [pipeline-review](../pipeline-review/README.md) | Checks pipelines against the rules a retrospective adds. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The eight steps, the routing table, and the hand-back. Start here. |
| [references/sources.md](references/sources.md) | Where the facts are, with commands, and the questions to ask the people involved. |
| [references/retro-template.md](references/retro-template.md) | The retrospective file template. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1.

| Case | What it checks |
|---|---|
| `repeated-fixes` | Finds one shared cause behind three fixes in git history, notes a test that checks nothing, and proposes a structural change. |
| `round-with-decision-log` | Turns two repeated review findings into structural changes, drops a one-off, and judges the last retro's actions. |
