# airflow-dag-repo

Rules for an Airflow DAG repository that people and AI agents both work in. Every DAG has a written contract, the code does what the contract says, and contract tests prove it.

## When to use it

Use it when you set up or reorganize an Airflow DAG repo, add agent instructions to one, or build, change, or review a DAG, its contract, or the shared code it imports.

## What it covers

The repo layout, the `AGENTS.md` rule index with `CLAUDE.md` pointing at it, skills in `.agents/skills/`, the contract-first workflow, the default DAG configuration, Airflow rules for the deployed version, contract tests, the order of checks, and what an agent may not touch in production.

## What it believes

- Every DAG has a contract in `docs/`, and the DAG's owner confirms it before anyone writes code. A change in behavior starts with a change to the contract.
- When a business decision is missing, the agent asks the owner. It never takes the answer from existing code, because the code may be the part that is wrong.
- Each binding rule in a contract has a test that fails when the code breaks it.
- Each region keeps its own self-contained DAG file. Code that more than one region needs lives in `utils/`.
- DAGs are written for the Airflow version that production runs, and checked against it.
- `AGENTS.md` routes to the rules and does not repeat them. A rule someone asks an agent to remember goes into the repo, not into the agent's memory.
- An agent never changes production. It writes the command for a person to run.

## Files

| File | What it holds |
|---|---|
| [SKILL.md](SKILL.md) | The layout, the contract-first workflow, Airflow rules, contract tests, and checks. Start here. |
| [references/repo-setup.md](references/repo-setup.md) | How to set up a new repo: `AGENTS.md`, `CLAUDE.md`, skills, the contract template, version sync, tooling, and the index test. |
| [references/dag-contract.md](references/dag-contract.md) | How to write a contract: what to ask the owner, the default DAG configuration, the skeleton, behavior steps, and diagrams. |
| [references/shared-code.md](references/shared-code.md) | What belongs in `utils/` and how to change it without breaking a region. |
| [evals/](evals/) | The test cases. |

## Tests

These cases have not been run yet, so the skill is at version 0.1.

| Case | What it checks |
|---|---|
| `new-dag-contract-first` | A new DAG starts with a contract and stops for the owner to confirm. |
| `airflow-version-mismatch` | A request for an Airflow 3 feature on a 2.9.3 deployment is flagged and solved with what 2.9.3 offers. |
| `review-dag-file` | A review that catches six planted flaws in a DAG file. |
| `remember-a-rule` | A rule the person asks to remember goes into the repo, in the place that owns it. |
