---
name: airflow-dag-repo
description: Set up and work in an Airflow DAG repository where every DAG has a written contract, agents follow one rule index, and checks run against the deployed Airflow version. Covers the repo layout (one self-contained DAG file per region, shared code in utils/, contracts in docs/, contract tests in tests/), the AGENTS.md rule index with CLAUDE.md pointing at it, skills in .agents/skills, the contract-first workflow, the default DAG configuration, Airflow rules for the deployed version, the check order, and what an agent may not touch in production. Use it when you start or reorganize an Airflow DAG repo, add agent instructions to one, or build, change, or review a DAG, its contract, or the shared code it imports, even if the user only says "add a DAG", "change the schedule", or "why does this DAG fail to import".
metadata:
  version: "0.1"
---

# Airflow DAG repo

These are rules for an Airflow DAG repository that people and AI agents both work in. Every DAG has a contract that states what it must do, the code does it, and contract tests prove it. Each rule names the failure it prevents.

To set up a new repo, or to bring an existing one to this layout, follow [references/repo-setup.md](references/repo-setup.md). To work in a repo that already has this layout, read its `AGENTS.md` first. Its rules win over this skill where they differ.

## 1. Layout

| Path | What it holds |
|---|---|
| `<region>_dags/` | One folder of DAG files for each regional Airflow instance. |
| `utils/` | Code that more than one DAG file uses. SQL templates go in `utils/sql/`. |
| `docs/` | One contract for each DAG, plus `dag-contract-template.md` with the default DAG configuration. |
| `tests/` | Contract tests (`test_<topic>_contract.py`) and tests for shared code. |
| `AGENTS.md` | The rule index every agent loads first. |
| `CLAUDE.md` | One line, `@AGENTS.md`, because Claude Code loads that filename. |
| `.agents/skills/` | The repo's skills, one folder each. |

- Each region keeps its own self-contained DAG file, with the same `dag_id` in every region. No shared factory builds the regional DAGs. **Why**: a reader sees the whole DAG in one file, and one region can change without touching the others.
- Code that more than one DAG file needs goes in `utils/`. A DAG file keeps only its region's values (timezone, worker queue, cluster name), the DAG definition, and code no other file uses. See [references/shared-code.md](references/shared-code.md).
- A DAG file puts the repository root on `sys.path` before it imports from `utils`:

  ```python
  REPOSITORY_ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "utils").is_dir())
  if str(REPOSITORY_ROOT) not in sys.path:
      sys.path.insert(0, str(REPOSITORY_ROOT))
  ```

  Without it the DAG fails to import with "No module named utils".

## 2. Contract first

Every DAG has a contract in `docs/`. The contract for a DAG is the file whose first heading names the `dag_id` in backticks. How to write one is in [references/dag-contract.md](references/dag-contract.md).

- A DAG with no contract stops the work. Write the contract, then wait for the DAG's owner to confirm it. **Why**: a contract written from the code repeats whatever the code gets wrong.
- When a business decision is missing, stop and ask the DAG's owner. Never take the answer from existing code, because the code may be the part that is wrong.
- A change in behavior starts with a change to the contract. The contract change and the code change go in the same merge request.
- A DAG uses the default DAG configuration for every setting its owner did not mention. When the owner asks for a value, the contract lists it and the DAG uses it.

### What a contract binds

The code must guarantee every binding rule. Everything else is free.

Binding:

- every row of the DAG configuration, for each region, and the default for every setting with no row;
- every input the contract names, and every invalid input that must stop the run;
- every numbered step, each one a task, with the order, repetition, and failure handling its fixed phrases state;
- every limit, every choice a step states, and every point where a person must review, approve, or confirm;
- what the run writes or sends, what stays unchanged after a failure, and what a rerun does;
- any sentence that says "must", "never", or "only", and any formula.

Free: task names, function names, file layout, a helper task that only reshapes data between two steps, example code and payloads, the number of tasks when the contract has no numbered steps, and the diagrams. A diagram that disagrees with a step is a defect in the contract.

The code adds no effect that no rule covers, such as a write, a delete, a message, or an external call. Add the rule to the contract first.

## 3. Build or change a DAG

1. Find the contract. A change to a DAG file reaches that DAG's contract. A change under `utils/` reaches the contract of every DAG that imports the changed code. A change to a contract reaches every DAG file with that `dag_id`.
2. If the task changes what the DAG must do, change the contract first and wait for the owner to confirm it.
3. List the binding rules the task touches. Keep the list in your notes, not in a committed file.
4. Write or update one contract test for each rule on the list (section 5).
5. Write the code, following section 4.
6. Run the checks in section 6.
7. Report each rule on the list with the code that implements it and the test that proves it. Mark a rule unverified when only a production run can prove it.
8. Commit only when a person asks. A merge to the main branch deploys to production.

To review a change, check that it did every step above.

## 4. Airflow rules

- **Write for the deployed Airflow version.** Before you use an operator, decorator, parameter, or import, look up which version added it. If a request needs a later feature, stop and tell the person, then build it with what the deployed version offers or plan the upgrade first. **Why**: a DAG that uses a later feature fails to import, or fails at run time, on the deployed scheduler.
- **No mapped task inside a mapped task group.** A task that runs once for each item cannot sit inside a task group that already runs once for each item. Make the inner work one task that loops over its items. **Why**: Airflow 2 cannot nest them, and the DAG fails to load.
- **Top-level code is imports, constants, and the DAG definition.** Read Variables, query databases, and call APIs inside tasks. **Why**: the scheduler parses every DAG file again and again, and top-level work runs on every parse.
- **Let a failed task fail.** Catch an exception only to add context, then raise it again. **Why**: Airflow retries and alerts on a failed task. A swallowed exception looks like success.
- **XCom carries small values**: names, counts, paths. Never a DataFrame or a large payload.
- **A rerun reaches the same end state.** A rerun for the same logical date, or the same submitted decision, must not write twice or skip work.
- **Credentials come from Airflow Connections and Variables**, read inside a task at run time. Never log a password, a token, or a webhook URL.

## 5. Contract tests

A contract test proves one binding rule. It lives in `tests/test_<topic>_contract.py`.

- Assert what the run leaves behind: what it wrote, what it refused, what stayed unchanged after a failure, and what a rerun reused.
- Assert the order when a rule states one, for example that a write happens only after the step it depends on succeeds.
- Assert the configuration values of each regional DAG file.
- Replace each external system with a fake at the point where the code calls it.
- Make sure the test fails when the code breaks the rule.
- Tests that need Airflow skip when it is not installed, and say so. A failing test is a finding. Do not weaken an assertion to make it pass.

## 6. Checks

Run every check that applies, in this order.

```bash
# 1. Compile: every changed Python file
python3 -m py_compile <file.py>

# 2. DAG import: every changed DAG file, and every DAG file that imports changed shared code
python3 -c "from airflow.models import DagBag; bag = DagBag(dag_folder='<path/to/dag.py>', include_examples=False); assert not bag.import_errors, bag.import_errors"

# 3. Crash lint: every changed Python file
ruff check --no-fix --select E9,F63,F7,F82 <changed .py files>

# 4. Tests
python3 -m unittest discover -s tests

# 5. Lint and format
ruff check --no-fix <files> && ruff format --check <files>
```

- The DAG import check needs the deployed Airflow version installed. A later version accepts features the deployed one rejects.
- The crash lint finds names that fail only when their line runs, such as an undefined name in an error path. Compile and import checks do not reach those lines.
- When you cannot run a check, say so and name it. Never report a check you did not run as passed.

## 7. Production

An agent does not change a production system: no change to a production database, replication tool, or Airflow Variable from an agent session. Write the exact command or SQL, and let a person run it. **Why**: a person then sees and owns every production change.

## 8. Rules belong in the repo

When a person asks you to remember a rule, a constraint, or a decision, write it into the repository, not into your own memory. Memory belongs to one agent on one machine. A file in the repository reaches every teammate and every agent.

- A rule about what one DAG must do goes into that DAG's contract.
- A rule about how to write, build, or review goes into the skill that owns that work.
- A setting every DAG shares goes into the default DAG configuration.
- A rule that applies to every task also gets a row in `AGENTS.md`.

Write each rule once, with its reason beside it.
