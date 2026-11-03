# Workflow resolution

Read this at stage 2, after discovery, to decide between the project's workflow, a hybrid, and the default workflow. Discovery gathered and assessed the evidence; this guide makes the decision. How the default capabilities are then organized is [default-workflow.md](default-workflow.md)'s job.

## Contents

- [Does a workflow fit this request](#does-a-workflow-fit-this-request)
- [The three modes](#the-three-modes)
- [Decision table](#decision-table)
- [When applicability is uncertain](#when-applicability-is-uncertain)
- [One execution path in hybrid mode](#one-execution-path-in-hybrid-mode)
- [Recording the choice](#recording-the-choice)
- [When the request changes](#when-the-request-changes)

## Does a workflow fit this request

Judge fit against the request in front of you, not by how many instruction files the project has. A project workflow fits when it answers five questions for this work type:

1. Where does the work start?
2. Which phases does it go through?
3. What has to be true to move from one phase to the next?
4. Who, or which skill, does each phase?
5. How is it confirmed done?

A project with a full feature process and nothing on database migrations has a workflow for features, and none for a migration request. Answers can be implicit. A PR template with a "design doc link" field and a required reviewer answers questions 3 and 4 for review, even if no document spells out the process.

Keep the three kinds of finding apart. Working rules are constraints, a workflow is a process, and a capability is something that can carry out a process. Only a workflow decides the mode; rules apply in every mode.

## The three modes

**Project-native.** The project's workflow covers the request and gives it enough structure to go from start to done. Follow its required phases, gates, ownership, and completion criteria. Bring in a default capability only where the workflow names a phase but leaves its method open, such as "verify the change" with no method given. Example: a repository with its own documented feature and bug-fix processes, and a request for a feature.

**Hybrid.** The project has an applicable but incomplete workflow for this request. Keep its confirmed phases, gates, and ownership, and fill only the uncovered parts from the [default workflow](default-workflow.md). Example: the project requires an approved design and a code-owner review for all changes, but says nothing about planning or verification. Use the project's design approval and review, and the default for the rest.

Working rules alone do not make a workflow partial. They stay constraints that apply in every mode.

**Default.** No applicable project workflow covers the request. Use the [default workflow](default-workflow.md) with Superpowers and pstack, and obey every applicable project instruction and working rule. Example: a new repository with only source code and a README, or a project whose `AGENTS.md` holds only rules such as "use pytest", "every database change needs a migration", and "do not commit to main".

## Decision table

| Discovery found | For this request | Mode |
|---|---|---|
| A workflow answering all five questions | Fully covers this work type | Project-native |
| An applicable workflow covering only some phases or gates | Some parts are defined, others are not | Hybrid |
| A workflow for another work type | No phases or gates are stated to apply to all changes | Default |
| A workflow for another work type | Some phases or gates are stated to apply to all changes | Hybrid |
| Working rules only | No applicable process | Default, with the rules applied |
| Nothing relevant | No applicable process or rules | Default |

A workflow written for another work type contributes only what it says applies beyond that type. A feature process with design, approval, plan, implement, review, and release does not become a migration process by borrowing its phases; the migration may need a different process, or have one discovery has not found. A section headed "All changes must..." with an approved design when architecture is affected, passing tests, and a code-owner review does apply to a migration.

## When applicability is uncertain

Discovery labels a workflow applies, doubtful, or superseded. Doubtful is not applies.

- Use only the parts confirmed to apply to this request.
- Choose hybrid if at least one project-defined phase or gate is confirmed to apply, and take the uncovered parts from the default workflow.
- Choose default if no part of a project workflow can be confirmed.
- Do not treat a doubtful instruction as mandatory. Record the uncertainty, and ask the user when it affects a consequential decision: an approval, a data migration, a deployment, or release policy.
- Ignore a superseded workflow, and note that you did.

The context note's workflow confidence and unresolved conflicts feed this step directly. Low confidence on a part that matters is a question for the user, not a reason to guess.

## One execution path in hybrid mode

A hybrid is one composed execution path, not two workflows running side by side. Keep the project-owned phases and mandatory gates, choose one workflow owner for the whole path per [default-workflow.md](default-workflow.md#choose-the-workflow-owner), and fill the uncovered activities with default providers under that workflow owner's execution contract.

For example, the project owns design approval by the technical lead and requires integration tests. The default path supplies requirements discovery, planning, delegation, and final verification, under one workflow owner such as a pstack playbook. That workflow owner treats the lead's approval as a gate it waits for and the integration tests as a check it must pass. It does not run its own design approval in parallel.

Record the source of each phase and the role responsible for it. Do not start a second orchestration loop for work another workflow already owns.

## Recording the choice

Put the decision at the top of the decision trail. Refer to the context note rather than repeating it. Record:

- the mode and the reason;
- the workflow owner;
- the source of each phase (project, default, or both);
- the constraints that shape the run;
- what is still open.

```text
Mode: hybrid
Reason: CONTRIBUTING.md requires design approval and code-owner review for all changes,
  but defines no process for planning a migration.
Workflow owner: pstack, through the playbook poteto-mode selects for this migration
Phase sources:
  understand, plan: default
  design approval, compatibility review: project
  build: default, under the project's migration rules
  test, review: project
  verify, hand-off: default
Constraints: backward-compatible migrations; no direct commits to main
Open: rollback procedure not documented
```

The example is illustrative. It does not mean every migration goes to pstack; choose the workflow owner per [default-workflow.md](default-workflow.md#choose-the-workflow-owner).

## When the request changes

A request can change type or scope mid-run: a bug fix turns out to need a schema migration, an investigation becomes an implementation request, or a change spreads into another service. A second service may have its own `AGENTS.md`, migration policy, and testing workflow, which discovery has not read yet. When this happens:

1. Extend discovery to the newly affected areas, work types, instructions, workflows, and capabilities. Only the affected part, not the whole repository.
2. Resolve the workflow again with the updated context. The mode can change.
3. Recompose the affected work packages and their ownership.
4. Record the change, its reason, and any approvals it needs.

Tell the user when the new scope brings a decision that needs their approval, such as an interface change, a data migration, or a change to how something is deployed.
