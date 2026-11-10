# Writing a lesson

A lesson is an incident or a failure written up to teach: for the team wiki, a postmortem, or a lesson log entry someone will read cold. It is different from the retrospective file, which lists many problems in a table. A lesson tells one story so that a reader who was not there understands it and can avoid it.

## The order

Write the six parts in this order.

1. **The mechanism.** The system or concept involved, explained from the basics for a reader who does not know it: what the parts are, and what each one remembers or decides.
2. **How it works normally.** The normal flow, step by step, with a small diagram or example when it helps.
3. **Why the root cause happened.** What changed, the chain from that change to the symptom, the exact error, and why the checks that existed did not catch it.
4. **The fix.** The immediate recovery and the root fix, step by step. Say which steps are done and which are still open.
5. **The result.** What was verified after the fix, with numbers: downtime, whether data was lost and how you know, and the measured values.
6. **The takeaway.** The short rule to remember, generic enough for the next project.

**Why this order**: a lesson that opens at the symptom ("the restore failed with `Cannot map savepoint state`") is hard to follow for anyone who does not already know how the system keeps state, so the error reads as noise and the fix as a magic step. Once the reader knows the mechanism (state is saved per operator id) and the normal flow (restore matches ids), the error explains itself and the fix is obvious. Start where the reader is, not where the pager went off.

## Notes on each part

- **Mechanism**: explain only what the story needs. If the failure is about how a slot remembers a position, explain the slot and the position, not the whole database. Name the parts the way the error message and the docs name them, so the reader can search for them later.
- **Normal flow**: a lesson that skips this leaves the reader unable to see what changed. A five-line diagram or a two-row example is enough.
- **Root cause**: quote the error exactly, as it appeared in the log. Show the chain as steps (change, then effect, then effect, then symptom), not one sentence. Name each check that should have caught it and why it did not: it tested a fresh start, it alerted on the wrong metric, nobody ran it. That last part is where the next structural fix comes from.
- **Fix**: separate the recovery (what got the system running again) from the root fix (what stops it happening again). Mark each step done or open, with an owner for the open ones. A lesson that reads as finished while the root fix is open teaches the wrong thing.
- **Result**: use the numbers you measured, labelled with where they came from, per `principle-label-the-evidence`. If you did not measure something, say so rather than estimate it. "No data lost" needs its evidence: a row count, a checksum, or an offset comparison.
- **Takeaway**: one to three lines, written as a rule. Leave out this project's names, hosts, and sizes so it holds for a different stack. If the rule can become a check, say which check, and route it with step 5 of the retrospective.

## Template

```markdown
# Lesson: <what failed, in plain words>, <YYYY-MM-DD>

## The mechanism

<The system or concept, from the basics. The parts, and what each remembers or decides.>

## How it works normally

<The normal flow, step by step. A small diagram or example.>

## Why it broke

- What changed: <the change>
- The chain: <change> → <effect> → <effect> → <symptom>
- The error: `<exact error, quoted from the log>`
- Why the checks missed it: <each check, and why it did not fire>

## The fix

| Step | Kind | Status |
|---|---|---|
| <step> | recovery / root fix | done / open (owner) |

## The result

- Downtime: <duration, from when to when>
- Data lost: <none / how much, and the evidence>
- Measured: <values after the fix, and where they came from>

## Takeaway

<The rule, in one to three lines, generic enough for the next project.>
```

## Worked example

The numbers below are illustrative.

```markdown
# Lesson: a stream job lost its restore path after an added step, 2026-03-04

## The mechanism

A stateful stream processor (here, Apache Flink) runs a job as a graph of operators:
a source, some transformations, and a sink. Some operators keep state, such as a
running count per customer or a window of recent events.

To survive a restart or an upgrade, the job writes a savepoint: a snapshot of every
operator's state, plus the source offsets it had read up to. The savepoint does not
store state by operator name or position in the code. It stores it by **operator id**.

Each operator gets its id in one of two ways:

- the code sets it explicitly, with `.uid("dedupe-by-order")`;
- or, when the code does not, Flink generates one from the shape of the job graph
  (the operator and the operators around it).

## How it works normally

1. The running job takes a savepoint. Each stateful operator's state is saved under its id.
2. The new version of the job starts from that savepoint.
3. Flink matches each saved id to an operator in the new graph and loads its state.
4. The sources resume from the saved offsets, so no event is lost or read twice.

    savepoint            new job graph
    id a1f3 → state  →   operator a1f3 (same id: state restored)
    id 9c07 → state  →   operator 9c07

This works as long as every stateful operator keeps its id across versions.

## Why it broke

- What changed: a release added a filter step between the source and the dedupe
  operator. None of the operators had an explicit `uid`.
- The chain: the new step changed the graph's shape → Flink generated new ids for
  the operators after it → the savepoint's ids for the dedupe and window state no
  longer matched any operator → the restore refused to start.
- The error:
  `Cannot map checkpoint/savepoint state for operator 9c07... to the new program,
  because the operator is not available in the new program.`
- Why the checks missed it:
  - unit and integration tests start the job from empty state, so ids never matter;
  - staging deploys from a fresh start, not from a production savepoint;
  - the error offers `--allowNonRestoredState`, which would have started the job by
    silently dropping the dedupe state, so it is not a fix.

## The fix

| Step | Kind | Status |
|---|---|---|
| Redeploy the previous version from the same savepoint | recovery | done |
| Read the generated ids from the savepoint metadata and pin them on the existing operators with `setUidHash`, then set an explicit `uid` on every stateful operator | root fix | done |
| Set `pipeline.auto-generate-uids: false`, so a stateful operator without a `uid` fails at submit time | root fix | done |
| Add a CI step that takes a savepoint on the current version and starts the new version from it without `--allowNonRestoredState` | root fix | open (pipeline owner) |

## The result

- Downtime: 38 minutes, from the failed restore to the old version running again
  (job manager log).
- Data lost: none. The old version resumed from the savepoint's offsets; the sink's
  row count for the hour matched the source topic's count (12,480,112 both).
- Measured: consumer lag peaked at 2.1 million events and drained in 14 minutes.
  The new version, with pinned ids, restored from a fresh savepoint with every
  operator's state mapped.

## Takeaway

State is saved by operator id, not by code. Give every stateful operator an explicit,
stable id, make a missing id fail the build, and test an upgrade by restoring from a
real savepoint, not from a fresh start.
```
