# Where the facts are

Read the sources that exist for this work. For each one, the commands or places to look, and what to look for.

## Git history

```bash
git log --since=<date> --format='%h %ad %an %s' --date=short
git log --since=<date> --format='%h %s' | grep -iE '^[0-9a-f]+ (fix|revert)'
git log --follow --format='%h %ad %s' --date=short -- <file>
```

- A `fix` that follows a `feat` in the same files: what the feature missed, and which check should have caught it.
- A `revert`, or a commit that undoes an earlier one: the premise that was wrong.
- Several fixes in one area within a short time: a shared cause.
- A file that every change touches: a hot spot, or two concerns in one place.

## Pull requests and reviews

```bash
gh pr list --state merged --search "merged:>=<date>" --json number,title,reviews,comments
gh pr view <number> --comments
```

- Review rounds per pull request, and what each round asked for.
- Findings a reviewer raised that the author's own checks should have caught.
- A reviewer's finding that reversed an earlier call.
- Comments that repeat across pull requests: a rule that is missing or not loading.

## Decision records and logs

- Decision records with status `superseded`, and the record that replaced each one. What triggered the reversal?
- Records whose revisit condition has fired.
- Choices marked "pending owner review" that are still pending.
- A decision log, if the work kept one (for example a table of time, phase, decision, why, evidence, result). Rows whose result says superseded, reverted, or overturned are the richest.

## Incidents and known issues

- The incident timeline: when it started, when someone noticed, and how. The gap between the two often matters more than the cause.
- Known-issue entries opened and closed in scope, and their severity.
- Alerts that fired with nothing wrong, and failures that fired no alert.

## Plans, contracts, and briefs

- What the plan or contract said, and what changed after it was agreed.
- Questions that were missing from the brief, so someone guessed.
- Requirements that turned out wrong, and who found out.

## Tests and evals

- Tests that were weakened to pass, or skipped.
- Eval cases that failed, and whether the skill or the case was wrong.
- Checks that passed while the defect was present: the check measured the wrong thing.

## The session itself

When the retrospective covers an agent session, read only that session's own transcript and reports. Look for:

- corrections the person had to make, especially the same correction twice;
- tool calls that failed the same way more than once;
- answers given and then retracted;
- work redone after a misunderstanding about the goal.

## Questions to ask the people involved

When people or agents took part, ask each one before closing:

1. What slowed you down or made you redo work?
2. What in your brief, the contract, or the plan was missing, wrong, or unclear?
3. What one change would have saved the most time?
