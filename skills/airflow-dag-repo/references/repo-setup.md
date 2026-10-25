# Set up the repo

How to lay out an Airflow DAG repository so that people and agents follow the same rules. Do the steps in order. Each one is small enough to review on its own.

## Contents

1. Folders
2. AGENTS.md, the rule index
3. CLAUDE.md
4. Skills
5. The contract template
6. Version sync
7. Tooling
8. Tests that keep the index honest

## 1. Folders

Create the layout in section 1 of [SKILL.md](../SKILL.md): one `<region>_dags/` folder for each Airflow instance, `utils/`, `utils/sql/`, `docs/`, `tests/`, and `.agents/skills/`.

Move legacy DAGs that nobody maintains into `old_dags/`, and exclude that folder from lint. Agents leave it alone unless the task names a file in it.

## 2. AGENTS.md, the rule index

`AGENTS.md` at the repository root is the short file every agent loads first. It routes to the rules and does not repeat them. A rule lives in exactly one place, a skill or a contract, and `AGENTS.md` points at that place.

Give it these sections, in this order.

| Section | What it holds |
|---|---|
| Opening | One sentence on what the repo holds, and one paragraph saying that `AGENTS.md` routes and the skills and contracts own the rules. |
| Quick start | The commands for tests, compile check, lint, crash lint, and the local Airflow stack, with the Python and deployed Airflow versions and the commit style. |
| Rules and conventions | A table: each binding rule in one sentence, and the skill or file that owns it. Only rules that apply to every task. |
| Where things are | A table: each top-level path and what it holds. |
| Skills | A table: "When you are about to" and the skill to open. Name the main skill to start from. |
| Rules and notes | Rules belong in the repo, not in an agent's memory, and where each kind of rule goes. See section 8 of [SKILL.md](../SKILL.md). |
| Security | No credentials in source, credentials from Connections and Variables at run time, what never gets logged, and that an agent writes production commands for a person to run. |
| Version sync | See section 6 below. |
| Testing | How to run all tests, one contract's tests, and the index test. Which tests skip without Airflow. |
| Troubleshooting | A table of symptoms and what to check, one row for each failure someone already spent time on. |
| Keeping this file current | What to update when a skill or the Airflow version changes, and which test fails when you forget. |

Write it plainly. A row says the rule, not the story of how the rule came about.

## 3. CLAUDE.md

`CLAUDE.md` holds one line:

```
@AGENTS.md
```

Claude Code loads `CLAUDE.md` and follows the `@` import. Other agents read `AGENTS.md` directly. **Why**: one file holds the rules, so the two cannot drift apart.

## 4. Skills

Put every skill the repo uses in `.agents/skills/<name>/SKILL.md`. That folder is the source of truth.

- Split the work into one main skill and smaller skills that it sends work to:
  - the main DAG skill: layout, contract-first workflow, Airflow rules, contract tests, checks;
  - a contract skill: how to write a contract ([dag-contract.md](dag-contract.md));
  - a shared-code skill: what belongs in `utils/` and how to change it ([shared-code.md](shared-code.md));
  - a development skill that only names which general skill to open at each moment of a coding task (testing, debugging, idempotency, commits), with no rules of its own.
- Copy general skills, such as commit style or secret handling, into the repo unchanged, so every teammate's agent gets them. Change a copied skill at its source, not in place.
- For Claude Code, link the repo's skills into `.claude/skills/`, which is where it discovers project skills:

  ```bash
  mkdir -p .claude/skills
  for skill in .agents/skills/*/; do
    ln -sfn "../../$skill" ".claude/skills/$(basename "$skill")"
  done
  ```

  Use relative links, so the links work in every clone. If you link only some skills, link at least the main skill and the ones it sends work to.
- When a tool cannot load a skill by name, it reads `.agents/skills/<name>/SKILL.md`. Say so in `AGENTS.md`.

## 5. The contract template

Create `docs/dag-contract-template.md` with two parts:

1. **The default DAG configuration**: the settings every DAG inherits. A contract lists only the settings its owner changed.
2. **The contract skeleton**: the text to copy into a new contract.

Both are in [dag-contract.md](dag-contract.md), sections 2 and 3. Fill in your regions' timezones, worker queues, and pools.

A change to a default changes every DAG that inherits it. Change a default only when every one of those DAGs should change.

## 6. Version sync

Write the deployed Airflow version and the Python version into a table in `AGENTS.md`, with every file that names them.

| Tool | Files | Version |
|---|---|---|
| Python | `ruff.toml` (`target-version`), "Quick start" in `AGENTS.md` | `<x.y>` |
| Airflow | the main DAG skill, "Quick start" in `AGENTS.md` | `<x.y.z>` |

- The Airflow version follows production. Name the file that is the source of truth for it, such as `airflowVersion` in your deployment's Helm values.
- Upgrade production first, then change every file in the row.
- Pin the local Airflow image (`docker-compose.yaml`) to the deployed version. If it differs, say so in `AGENTS.md`, because a DAG that loads locally may then fail in production, or the reverse.

## 7. Tooling

- `ruff.toml` at the root: `target-version` matching the deployed Python, the `AIR` rules on, and `old_dags/**` excluded from strict rules. A DAG file that sets `sys.path` before importing `utils` needs `E402` ignored for that file.
- Tests run with `python3 -m unittest discover -s tests`, so they need nothing beyond the standard library and Airflow.
- A test module that needs Airflow sets `AIRFLOW_HOME` to a temporary folder, `AIRFLOW__CORE__LOAD_EXAMPLES=False`, and `AIRFLOW__CORE__UNIT_TEST_MODE=True` before it imports Airflow, and skips its Airflow tests when the import fails.

## 8. Tests that keep the index honest

Add `tests/test_skill_map.py`. It fails when:

- the "Skills" table in `AGENTS.md`, or a skill that sends work to other skills, names a skill that does not exist in `.agents/skills/`;
- a skill in `.agents/skills/` cannot be reached from `AGENTS.md`;
- `AGENTS.md` and the main DAG skill name different Airflow versions.

**Why**: an index that points at a missing skill sends agents nowhere, and nobody notices until an agent ignores a rule.
