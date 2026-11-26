---
name: retrospective
description: Look back at finished work (a session, a pull request, a round of fixes, an incident, a migration, or a long-running design decision) and turn what it teaches into changes in files. Gathers facts from git history, reviews, decision logs, a lesson log (such as `retros.md`), incidents, and evals, finds reversals, rework, and late defects, checks each decision's prediction against what happened, asks why until it reaches a cause in the process, and routes each lesson to the one place that owns it (a test or lint first, then a contract, a decision record, a skill, AGENTS.md, or memory), keeping generic skills free of project facts and turning a lesson that returned after a text-only fix into a script or check, with the owner's approval. Use it after shipping or an incident, at the end of a round of work, when a lesson log piles up, when a revisit condition fires, to write up a lesson or explain an incident, or when someone says "retro", "what did we learn", "look back on this", or "why do we keep hitting this".
metadata:
  version: "0.3"
---

# Retrospective

A retrospective that changes nothing did not happen. This skill looks back at finished work and turns each lesson into one change in the file that owns it, so the next person or agent does not learn it again the hard way.

## Where this fits

| You need | Skill |
|---|---|
| Collect facts across a long period or many repositories | `knowledge-harvest` |
| Revisit a design decision that the retro shows was wrong | `architecture-review` |
| Check a pipeline against the rule a lesson produced | `pipeline-review` |

## Steps

**Writing up one lesson only.** When the task is to write up a single incident or failure as a lesson, not to run a retrospective, do step 2 (gather the facts) and step 4 (find the cause), then write the lesson with [references/lesson-writeup.md](references/lesson-writeup.md) and hand back as [Hand back](#hand-back) says for one lesson. Skip the routing, approval, and record steps unless the owner also asks for changes. **Why**: the full eight steps end in a retro file and proposed changes, which is not what the reader of a lesson needs.

Otherwise, open a todo list with one entry per step.

### 1. Scope

- Name what you look back on: a time range, pull requests, an incident, a session, or one decision.
- State what that work set out to do, and the definition of done it had.
- Read the last retrospective's actions. Step 6 checks them.

### 2. Gather the facts

Collect facts, not impressions, from the sources in [references/sources.md](references/sources.md). For a long period or many repositories, gather them with `knowledge-harvest` first. Look for:

- **Reversals**: superseded decisions, reverts, a fix that follows a feature in the same area, and instructions someone overturned.
- **Rework**: review rounds per change, work done twice, and changes made to a contract or plan after it was agreed.
- **Defects caught late**: found by a reviewer, CI, the owner, or production rather than by the check meant to catch them. Name that check.
- **Waits**: time blocked on a person, a missing answer, or a broken tool.
- **What went well**: a check that caught a real defect, or a decision that held under load. Keep doing these, so name them.
- **Claims of a fix**: when a lesson log says a lesson was already acted on ("Changed: the deploy skill says so"), open that file and check. A fix that never landed is still an open lesson.

Label each fact with its evidence: a commit, a pull request comment, a log line, or a measurement, per `principle-label-the-evidence`. Cite a line number only for a line you read; otherwise cite the file and quote it. **Why**: an invented line number sends the owner to the wrong place and makes every other citation suspect. Read only sources that belong to this work. Never sweep unrelated private chats or other projects.

### 3. Check the decisions

For each design decision made or relied on in scope:

- What did it predict, and what happened?
- Did its revisit condition fire? If so, it goes to `architecture-review`.
- Is a choice that was marked "pending owner review" still pending? List it for the owner.
- Did anyone take an answer from the code that only the owner could give?

A decision that turned out right is a finding too. Note what made it right.

### 4. Find the causes

For each problem, ask why until you reach something in the process: a brief, a contract, a template, a skill, a check, a missing script, a missing number, or a premise everyone assumed.

- Group problems that share a cause. Two fixes that failed on the same premise point at the premise, not at the fixes.
- **A one-off is not a lesson.** Keep a lesson when it happened at least twice, or once at a high cost. A fact about the owner's machine, clock, shell, or habits is not a one-off even when it happened once: it will hold next time, so it goes to memory.
- **A rule that existed and was not followed** is a different lesson from a missing rule. Find out why it was not followed: the skill did not load, its description did not match the task, the rule was buried, or it was wrong.
- **A lesson that came back after a text-only fix** means the text did not work. Search the whole log and history for the same symptom and count the earlier occurrences and how each was fixed; do not judge it from memory. The next change is a script, a check, or a test, and the old sentence goes. **Why**: a rule an agent must remember fails the same way every time it is under load; a fix in structure does not.

### 5. Turn each cause into one change

Each lesson becomes exactly one change, in the place that owns it. Prefer structure over text. If a test, a lint, a type, a template default, or a script can make the mistake impossible or loud, make that change and do not also add a sentence.

| The lesson is | It goes into |
|---|---|
| A mistake a machine can catch | A test, a lint rule, a type, a template default, or a script |
| What one pipeline or feature must do | That pipeline's contract |
| A design that was wrong | A new decision record that supersedes the old one. Never edit an accepted record to reverse it. |
| How to do one kind of work | The skill that owns that work |
| A rule every task in the repo follows | A row in `AGENTS.md` that names the skill or file owning the rule |
| A skill that did not load when it should have | That skill's description |
| A repeated manual step | A script |
| One person's preference, or a fact about their machine or setup | That person's agent memory, not the repo |
| A quirk of one tool, shell, or runtime | The reference that covers that tool, or a script that wraps it, not the main steps of a workflow |

**Generic or local.** For each lesson about how work is done, ask: would the next project, with a different stack, hit this too? If yes, the generic skill gets the rule, and the project gets only its own facts (names, paths, sizes, versions) as an example or a setting. If no, it stays in the project. **Why**: a lesson sent only to the project fixes this repository and leaves the next one to learn it again; a project fact in a generic skill misleads every other project.

Write each change with its reason beside it, and the failure it prevents. Do not edit skills vendored from another project. Change them at their source.

### 6. Check the last retro's actions

For each action from the last retrospective: did it help? Say **keep**, **adjust**, or **revert**, with the evidence. An action nobody can judge yet stays open, with the date to judge it.

### 7. Get approval, then apply

Present the facts, the causes, and the proposed changes. Apply only what the owner approves. Changes to shared files, such as skills, `AGENTS.md`, contracts, and templates, go in through their own pull request, not inside unrelated work.

### 8. Record it

Write the retrospective with [references/retro-template.md](references/retro-template.md), and add a dated summary line to the repo's retrospective log. When the input was a lesson log, end each entry you covered with its outcome, `Next action: <where> / <change> / <status>`, so the next retrospective sees which lessons are still open. If the work kept no decision log, start one for the next round, so the next retrospective has facts to read.

When a lesson is written up to teach, such as an incident write-up, a postmortem, or a lesson for the team, follow [references/lesson-writeup.md](references/lesson-writeup.md): the mechanism, how it works normally, why the root cause happened, the fix, the result with numbers, and the takeaway, in that order. **Why**: a lesson that starts at the symptom loses every reader who does not already know how the system works; once the mechanism is explained, the error and the fix make sense.

## Hand back

1. Five lines for the owner: what the work set out to do, what shipped, what hurt most, what you propose to change, and what needs the owner's decision.
2. The retrospective file.
3. The proposed changes, one per lesson, each with its file, its reason, and the failure it prevents.

For one lesson only, hand back instead:

1. The lesson file.
2. One line naming any fact you could not verify, or any part the notes did not give (such as a measured result), so the owner fills it in rather than finds it invented.
