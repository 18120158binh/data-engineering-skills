---
name: pipeline-migration
description: Move a running pipeline to a new engine version, framework, sink, or table layout while its downstream consumers keep working, then stop the old pipeline. Covers listing every downstream reader and how it tracks its position, running the old and new pipelines side by side on the same input with downstream fed from both until the outputs match, handing a streaming writer's checkpoint over to a new sink after checking the official docs that the checkpoint survives the change, giving downstream streaming readers new checkpoints with start positions that skip and repeat nothing, switching readers, and stopping and retiring the old pipeline. Use it when you upgrade the database or engine a pipeline runs on, replace a badly laid out output table, change a stream job's sink, or rewrite a pipeline, even if the user only says "upgrade ClickHouse", "move the job to the new table", "repartition this streaming table", or "switch the consumers over".
metadata:
  version: "0.1"
---

# Pipeline migration

A pipeline migration changes what a pipeline runs on or writes to, while data keeps flowing and downstream consumers keep reading. A data migration moves stored data. A pipeline migration moves the flow. It is done when every consumer reads only the new path, nothing was skipped or read twice at the switch, and the old pipeline has stopped.

## Where this fits

| You need | Skill |
|---|---|
| Decide whether to change the engine, the sink, or the layout | `architecture-review` |
| Move stored history, or reconcile two tables row by row | `data-migration` |
| Check the new pipeline before it runs | `pipeline-review` |
| Look back once the old pipeline is gone | `retrospective` |

## Steps

Open a todo list with one entry per step.

### 1. Frame

Write down:

- **What changes**: the engine or database version, the framework, the sink, or the table layout.
- **Every downstream consumer**: each job, table, view, and report that reads the pipeline's output, and how it tracks where it is, such as a streaming checkpoint, a consumer offset, a cursor, or a scheduled query.
- **The owner**, who approves the switch and the stop.

When the list of consumers is not certain, find them before going further. A consumer you did not list keeps reading the old output after the switch.

### 2. Choose the pattern

| Pattern | Use it when |
|---|---|
| **Run side by side** | The engine or the logic changes, such as a database or engine version upgrade, so you cannot show by reading the code that the output stays the same. |
| **Hand over the checkpoint** | Only the sink changes, such as a new table with a better layout, and the engine can carry the reading position across. |

Write the choice and the reason into the plan.

### 3a. Run side by side

1. **Run the old and the new pipeline at the same time, on the same input.** Each writes to its own output.
2. **Feed downstream from both.** Run the downstream jobs on the new side too, so the comparison covers what consumers actually get, not only the first table.
3. **Compare the outputs** until they match, or every difference has a written cause. The reconciliation rules are in the `data-migration` skill.
4. **Move the consumers to the new output.**
5. **Stop the old pipeline, and check that it stopped.**
6. **Keep the old side able to run** until the owner agrees there is no switching back.

**Test**: did both pipelines read the same input over the same window, and was the comparison made on what consumers read?

### 3b. Hand over the checkpoint

1. **Create the new output with the layout you want.** Do not repartition the old table in place while streaming readers depend on it.
2. **Check whether the writer's checkpoint can be reused with the new sink.** Read the official documentation for the exact engine and connector versions you run. Whether a checkpoint survives a change of sink depends on the engine, the sink, and the version, so do not assume it.
   - If it can, keep the writer's checkpoint and point the job at the new output. The job continues from the exact source position where it stopped writing to the old output, so nothing is skipped and nothing is read twice.
   - If it cannot, choose an explicit start position in the source, and deduplicate the overlap in the new output. Write down which records the overlap covers.
3. **Give every downstream streaming reader a new checkpoint on the new output.** A reader's checkpoint records positions in the old output, such as table versions or offsets, and those mean nothing in the new one. Set each reader's start position so it neither skips nor repeats the records written around the switch.
4. **Stop the old pipeline, and check that it stopped.** Only one writer may remain.
5. **Decide how the old output's history reaches consumers** if they need it: copy it into the new output with `data-migration`, or keep reading it from the old output until it ages out. Record the decision.

**Test**: name the source position where the old sink stopped and the new one started, and each reader's start position on the new output. Can any record fall between them, or land on both sides?

### 4. Stop the old pipeline

- Write into the plan who stops the old pipeline, in which order relative to the consumers' switch, and how they confirm it stopped: no running job, and no new writes to the old output.
- **Why**: a pipeline that keeps writing to the old output, or two pipelines writing at once, leaves consumers with data that depends on which output they follow.

### 5. Retire the old output

Once no consumer reads the old output and the owner has agreed there is no switching back, retire it with step 8 of the `data-migration` skill: record it before dropping, and set a date.

## Hand back

1. The plan: what changes, the chosen pattern and why, every consumer with how it tracks its position, and the switch order.
2. For a handover: the source position where the writer switched, each reader's new start position, and the documentation that says the checkpoint survives the change, with its version.
3. For a side-by-side run: the comparison, with the window, what was compared, and every difference with its cause.
4. Proof that the old pipeline stopped.
