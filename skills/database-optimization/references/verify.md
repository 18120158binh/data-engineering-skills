# Verifying an optimization

## Same conditions as the baseline

- The same query text, parameters, and data. A different tenant or date range measures a different query.
- The same cache state. Report a cold run and a warm run for both the baseline and the change.
- The same load, or report the difference. A quiet replica and a busy primary are different machines.

## Enough runs

- Run each side several times, and report the run count and the spread, such as the median and the slowest run.
- When the difference is smaller than the spread, there is no proven gain.
- Prefer buffer counts and rows read over timings. They reproduce across runs, while timings depend on cache and disk.

## Explain the number

Before reporting a gain, answer:

- **What limited it before, and what limits it now?** If you cannot say why it is not twice as fast again, you do not know what you measured.
- **What else could the number be measuring?** Rule out each with evidence: an error that returned early, a cached result, a plan that skipped the work, a warm cache on one side only, noise, or a piece too small to matter end to end.

## Side effects

| Check | How |
|---|---|
| The result is unchanged | Compare the rows the query returns before and after, on the same inputs |
| Writes did not slow down | Insert and update latency on the table, before and after |
| Storage | Table and index size, before and after |
| Other queries | The plans of the other main queries on the same table, which a new index or new statistics can change |
| Upkeep | The refresh job, the backfill, or the cleanup the change needs, and their cost |

## Report

```markdown
## Optimization: <what>

Target: <number>
Baseline: <median and slowest of N runs, buffers, cold and warm, parameters>
Limiter: <what, and the evidence>
Change: <what changed>
After: <median and slowest of N runs, buffers, cold and warm>
Result unchanged: <how checked>
Side effects: <writes, storage, other plans>
Not measured: <what>
```

## Sources

This follows the explain-the-number and prove-it-works principles from pstack, and the owner's benchmark practice: run the baseline at the same time as the candidate, in a realistic setup, and record the limitations.
