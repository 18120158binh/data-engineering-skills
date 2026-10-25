# Pipeline principles

Each rule has the failure it prevents (**Why**) and the question a reviewer asks (**Test**).

## Contents

1. Reruns, cursors, and checkpoints
2. Writes under replay
3. Backfill and late data
4. Partial failure and failing dependencies
5. Concurrency, limits, and cost
6. Alerting
7. Data quality and schema change
8. Retention of state
9. Secrets and data boundaries
10. Human gates and production

## 1. Reruns, cursors, and checkpoints

**Read new records by an increasing id, not by time.**
- **Why**: a time window loses the records a late or skipped run should have read.
- **Test**: skip one run. Does the next run read everything the skipped one would have?

**Save the cursor or checkpoint only after the effect it covers succeeds.** Send first, then save.
- **Why**: a save before a failed send loses that work for good.
- **Test**: kill the run between the effect and the save. Does the retry redo exactly the unfinished work?

**Save with compare-and-set.** The save does nothing if the stored checkpoint moved since the run read it. Claim shared work with `UPDATE ... WHERE <expected value>`, and check the row count.
- **Why**: a rerun or two overlapping runs otherwise repeat the same effect.
- **Test**: run the same logical run twice, overlapping. Is there one effect or two?

**Check saved state and the source's behavior before acting.**
- State with the wrong shape stops the run before any effect.
- A source that ignores the cursor is an error, not a reason to read everything again.
- A limit set to zero or below is an error, not a silent fallback to a default.
- **Why**: corrupt state or an ignored cursor makes a run resend everything or loop. A limit of zero can silently drop everything it limits.
- **Test**: feed a malformed state, a page with ids at or below the cursor, and a limit of 0. Does each one fail loudly?

**A first run with no checkpoint starts from an explicit choice, `latest` by default.** Write down how to replay everything: delete the state, then start from `earliest`.
- **Why**: a first deploy otherwise reports all of history as news, and a replay needs guesswork.
- **Test**: what does the first run do? Is the replay procedure written down?

**Bound the work one run may do.** The next run continues where this one stopped, and the output says the pipeline is behind.
- **Why**: an unbounded catch-up overruns the timeout or memory, and a silent lag hides a backlog.
- **Test**: what is the limit per run? What happens when it is hit, and who learns of it?

**Compute a run's data window from its scheduled time, in the pipeline's timezone.** Never use the wall clock, and never use a UTC date for a schedule that runs at local midnight.
- **Why**: a run at local midnight in a timezone ahead of UTC still has the previous day's UTC date, so a UTC date can point at the wrong day or month. A retried run that reads the wall clock covers the wrong day.
- **Test**: retry a run a few hours late, and run a monthly job at local midnight in a timezone ahead of UTC. Is the window the same?

**A scheduled slot runs once.** Its idempotency key is the definition plus the slot, and the scheduler skips the slot when any run, finished or not, has the key.
- **Why**: a duplicate check that sees only active runs lets a job that already finished run again.
- **Test**: does the duplicate check also see finished runs?

## 2. Writes under replay

Table design is owned by the `data-modeling` skill: natural keys, one writer per row, upserts with a version guard.

**Every sink is at-least-once, and every write is idempotent.** Never generate a random id or a `now()` value in a sink or in an id that a replay derives. Give every outbound message a stable id built from its cause.
- **Why**: retries, checkpoint replays, and CDC snapshots repeat records. A random id writes a second row on replay. Exactly-once delivery covers only the hop between two systems that share a transaction, not a database sink or an outside consumer.
- **Test**: write the same record twice. Is the state unchanged? Search the sink path for random ids and clock reads.

**A consumer deduplicates across all history when a fresh start can re-snapshot the source.**
- **Why**: a snapshot replays every existing row as a new insert.
- **Test**: what does the consumer do when it sees every old row again?

**A rerun after a partial failure converges.**
- Reuse what already exists.
- Wait for work that is still running, and never start it a second time.
- Redo only the work that is missing.
- **Why**: external work may have partly finished, so a rerun that recreates blindly duplicates it or fails on it.
- **Test**: what happens if this runs twice, and if the last run crashed at each possible point?

**A stateful stream job moves state across versions on purpose.**
- Stop with a savepoint, and start the new version from it.
- Ask a person before any start without one.
- Give every stateful operator a fixed id, pinned by a test.
- **Why**: generated operator ids change with the graph, and a start that drops them forgets all state.
- **Test**: does the rollout plan name the savepoint? Does a test assert every operator id?

**CDC replication slots are kept, watched, and cleaned up.**
- Keep slots across stops, and delay the position they confirm by enough checkpoints that a rollback can re-read.
- Advance quiet slots with a heartbeat write.
- Alert on the log each slot holds.
- Drop a job's slots when you retire it.
- **Why**: a dropped slot makes a restored job skip every change since its checkpoint. A quiet slot holds the log that other tables write, and can fill the disk.
- **Test**: is each slot active, with a small amount of held log? Is there an alert?

## 3. Backfill and late data

**Reload a trailing window on every incremental run, anchored in local time, into a target that replaces rows by natural key.** For example, the last three days.
- **Why**: rows that arrive or change after their day are otherwise never loaded.
- **Test**: if a source row from two days ago changes today, does the next run carry the change without a duplicate?

**Choose a backfill range from what the source holds, with a cap.** For example, the oldest valid partition, but at most one year back.
- **Why**: a source can hold history from long before it was connected. Backfilling from the connection date leaves a gap.
- **Test**: where does the backfill start and end? What is the cap, and what happens to history beyond it?

**Keep backfills off the capacity that monitors and regular runs use.** Give them their own pool, and fewer retries.
- **Why**: a backfill can hold a shared pool for hours, and a monitor queued behind it is blind.
- **Test**: can this backfill delay a monitor or an alert?

**Count every record dropped as late, export the count, and alert on it.**
- **Why**: when a producer is down longer than the lateness bound, its backlog is dropped as late. A counter that is never exported makes that loss silent.
- **Test**: is there a late-drop counter, is it exported, and does an alert read it?

**Starting from a backlog or empty state, keep event time from outrunning reference data that is still loading.** Pause rules that fire on absence ("no purchase within a day") until the backlog clears.
- **Why**: replaying a backlog can move event time hours ahead in seconds while a lookup table is still loading, so valid records are dropped and absence rules fire wrongly.
- **Test**: replay a backlog quickly while side inputs load. Is anything dropped or fired wrongly?

## 4. Partial failure and failing dependencies

**Every step says what must not run and what stays unchanged when it fails.** Write the record of truth (an inventory, a checkpoint, a summary) last, and only for the items whose every step succeeded.
- **Why**: a partial run otherwise records items as done that are not.
- **Test**: for each step, what stays unchanged on failure? Is the final write gated on every earlier step for that item?

**Isolate failures per item, and still fail the run.** A failed item is marked, the others continue, and the run ends failed without writing the summary.
- **Why**: one bad item otherwise blocks the rest, or a partial success is recorded as full.
- **Test**: fail one item of N. Do the others finish, and does the run still end failed?

**A failed or empty read is never "nothing there".**
- An upstream that returns nothing, or cannot be read, fails the run.
- Never write a default back as stored state.
- Never resolve an alert because data is missing.
- A permission error or a missing source table is a failure, not a skip.
- **Why**: a read that times out and is treated as empty can be written back with a higher version, and replace real history for good. An empty answer from a listing API reports everything as gone.
- **Test**: make the dependency fail, then return an empty result. Does anything get written, resolved, or deleted?

**No automated signal alone deletes data or stops replication.** A person submits that decision.
- **Why**: an item missing from an API list is often an API mistake, and acting on it loses data.
- **Test**: can any path remove a source or drop data without a person's decision?

**Sort errors by kind.**
- A record the target rejects for its content is skipped, counted, and sent to a dead-letter store.
- A transient error is retried, then fails.
- One record never restarts a job in a loop.
- A dead-letter entry fits under the producer's size limit.
- **Why**: a payload that grows past the message size limit fails the sink, and an at-least-once job then restarts on the same record forever.
- **Test**: feed one malformed and one oversized record. Does the job keep running?

**A timeout is not a retry.** Never retry a mutating step automatically while its first attempt may still be running. Bound long external work by the run timeout, and have a person check what is still running before a rerun.
- **Why**: some external jobs cannot be stopped once started, and a write that timed out may still commit, so an automatic retry can write everything twice.
- **Test**: after a timeout, can a second write start while the first is alive?

**Check the target's state again right before a heavy or destructive action**, and validate identifiers against an allow-list.
- **Why**: the target may have changed since the step that planned the action.
- **Test**: is there a check between the step that decides and the step that acts?

## 5. Concurrency, limits, and cost

**Cap heavy external work across the whole run, not per item.** State the number, and the incident behind it, in the contract.
- **Why**: starting one heavy job per item at the same moment can exhaust the worker's memory and take down the node it runs on. A cap per item does not prevent that when there are many items.
- **Test**: what is the most that runs at once, counted across all items?

**One active run per pipeline per environment, and one copy of a stream job per source.** Scope every lock and duplicate key by environment when environments share a store.
- **Why**: when environments share a cache or a database, a lock taken in one environment can make another skip its work.
- **Test**: does every lock and duplicate key include the environment?

**Bound every query and call.**
- Set a server-side time limit and a client timeout, with the outer timeout larger than the inner one.
- Put a time window on every query against a large history.
- Run generated SQL read-only, with row and byte caps.
- Check connection limits against parallelism times pool size.
- **Why**: a query without a time window reads more partitions as history grows, until it times out. A client timeout shorter than the server's hides the server's own error.
- **Test**: can any query run without a window or a time limit?

**On a rate limit, honor `Retry-After` within a retry budget, and fail when the wait exceeds it.** Run lookups with bounded concurrency and a bounded queue, so a slow dependency slows the pipeline instead of growing a queue.
- **Why**: retries that ignore `Retry-After` land inside the same rate-limit window, and an unbounded queue grows while a dependency is slow.
- **Test**: does the retry read `Retry-After`? What bounds the calls in flight?

## 6. Alerting

**Alert on what is new.**
- Group errors by a normalized signature, with numbers and ids replaced.
- Report a known error again at once when it reaches a new source.
- Space reminders out, for example after 1 hour, then 4, then every 24.
- Hold back known self-healing errors until several runs in a row see them.
- **Why**: a broken flow logs the same error on every retry, and a message per retry buries the next new error.
- **Test**: how many messages does a three-day outage of one error on ten sources produce? Does a new source still alert?

**Alert only on the final failure, never on retries in between.** Give each signal one owner, batch open problems into one reminder, and never alert on a total that only grows.
- **Why**: rules that repeat for known state flood the channel until people stop reading it. A total that only grows fires forever after one bad event.
- **Test**: how many messages per hour does known steady state produce? Can the metric ever fall below its threshold?

**Page on a condition that lasts.** Require a minimum sample and two checks in a row, and hold an open incident until it clears. Scope any debounce to one rule.
- **Why**: a single slow call should not wake anyone, and a debounce shared by every rule delays the pages that matter.
- **Test**: can one blip page someone? Does this suppression delay any other alert?

**Keep the alert path reliable.**
- A failed delivery does not mark the alert as sent.
- Optional enrichment, such as an LLM summary, never delays or fails the alert.
- Test that a new alert route reaches a person.
- **Why**: a lost alert recorded as sent is never retried, and an alert rule routed to no receiver notifies no one.
- **Test**: make the webhook fail. Is the alert retried next run? Make the enrichment fail. Does the alert still go out?

**Monitor the monitor.** A job that cannot read its source fails and alerts. Every backup or operations job has its own alert for failed, stale, or missing runs. A health endpoint is not proof that the data is healthy.
- **Why**: a job that fails without alerting looks exactly like a job with nothing to do, and can stay broken for months.
- **Test**: if this job stops tonight, who learns of it, and when?

## 7. Data quality and schema change

**Check the source schema at ingestion, before any consumer.** A record that fails is dropped, counted under a reason, and dead-lettered. Log the field path and type, never the value. Measure how much traffic would fail before you turn a check on.
- **Why**: drifted payloads otherwise count or match the wrong things, and nothing says why.
- **Test**: where is the schema checked, and what does a violation produce?

**Roll out schema changes as expand and contract.** Readers that tolerate the new shape deploy before writers, and a column is dropped only after every job stops naming it.
- **Why**: a writer that does not know a new field may drop or reject every change that carries it.
- **Test**: what is the deploy order?

**Prove a change against a baseline.** Where the change must be a no-op, compare before and after, with a control that must fail. Never present a partial total as the total; count what is missing separately. Done means running and checkpointing, not applied.
- **Why**: a change can degrade data without raising any error, and a rollout can look healthy while the old version still serves and the new one crash-loops.
- **Test**: what baseline did you compare against, and which check would have failed if the change were wrong?

## 8. Retention of state

**Bound every piece of state a pipeline keeps, and make dropping safe.**
- State kept between runs has a size limit and a retention window, and dropping an entry costs at most one extra alert, never a hidden one.
- Dead-letter and personal-data topics get an explicit short retention, never the broker's default.
- A cleanup job keeps the newest N, refuses a bad retention value, and is safe to repeat.
- **Why**: state held in a small store grows without bound, topics created with defaults keep personal data, and a broken cutoff would delete every backup.
- **Test**: what is the cap, what is dropped first, and what does dropping cost?

## 9. Secrets and data boundaries

**Log every external call and its answer, with secrets redacted.**
- Never log a password, a token, a webhook URL, row content, or a payload.
- Alert messages carry error names and links, not raw exception text.
- Read credentials inside tasks, at run time.
- Pin the production log level.
- **Why**: exception text and database error details carry credentials and personal data. A production setting that falls through to debug logging can print tokens and result rows.
- **Test**: search the log, alert, and response paths for interpolated exceptions, URLs, and payloads. What does debug logging print?

**Data that crosses a boundary, such as a region or an LLM provider, is bounded, and the contract says it may go there.**
- **Why**: scanning across regions breaks data residency law such as GDPR.
- **Test**: what leaves its region or system, and where is that allowed in writing?

## 10. Human gates and production

**An agent does not change a production system.** It writes the exact command or SQL for a person to run.
- Repair, backfill, and intake jobs are dry runs by default and need an explicit apply.
- A production deploy needs an explicit production target and a version that already ran in development.
- A destructive plan refuses the whole run on any unexpected target.
- **Why**: a change from an agent session cannot be reviewed or rolled back. A mix-up of cluster contexts can deploy one environment's config to another and still report success.
- **Test**: can this job write by default? Can an agent session reach a production write?

**Every approval point is in the contract, and a person's decision is a checked run input.** A readiness label is not an approval. Reject unknown or invalid decisions before the first change.
- **Why**: the record of what runs must not drift from what a person reviewed.
- **Test**: where does a person approve, and what is checked before the first write?
