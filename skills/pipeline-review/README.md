# pipeline-review

Checks a data pipeline, Airflow DAG, stream job, CDC flow, or operations job against the principles that keep it correct under retries, reruns, replays, backfills, late data, and partial failure, and that make sure a person learns when it breaks.

## When to use it

Use it when you build, change, or review a pipeline, before a merge or a first deploy, or after an incident. Typical questions: "is this safe to rerun", "what happens if it fails halfway", "will this double count", "why did nobody get alerted".

## What it believes

- Review the side effects, not the code's structure. List every write, delete, message, external call, and state save first.
- Save a cursor or checkpoint only after the effect it covers succeeds, and save it with compare-and-set.
- Every sink is at-least-once and every write is idempotent. Exactly-once covers one hop, not the whole path.
- A failed or empty read is never "nothing there". It fails the run, and it never overwrites stored state or resolves an alert.
- Cap heavy work across the whole run, not per item, and keep backfills off the capacity monitors need.
- Alert on what is new and what lasts, and never let optional enrichment block the alert.
- Prove the one fact the pipeline's safety rests on by running code. A claim that was not run is labeled as inferred.
- A finding whose fix needs a different design goes to `architecture-review`, not into a patch.

## How it connects

| Skill | Relationship |
|---|---|
| [architecture-review](../architecture-review/README.md) | Its decision record lists the guarantees this skill checks. Design-level findings go back to it. |
| [data-modeling](../data-modeling/README.md) | Owns the rules for the tables a pipeline writes. |
| [airflow-dag-repo](../airflow-dag-repo/README.md) | Owns the Airflow-specific rules. |

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The review steps, severity, and the hand-back. Start here. |
| [references/principles.md](references/principles.md) | The rules in ten themes, each with the failure it prevents and the test a reviewer runs. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1.

| Case | What it checks |
|---|---|
| `review-error-monitor` | A monitor DAG with a time-window cursor, a save before the send, rerun duplicates, alert noise, and an LLM that blocks the alert. |
| `review-backfill-dag` | A backfill DAG with unbounded parallel copies, an empty listing treated as "no servers", a retry after a timeout, a wall-clock window, and the inventory written first. |
