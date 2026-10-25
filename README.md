# data-engineering-skills

This repo holds Binh Ly's data engineering experience, written as skills. Each skill is a set of opinionated rules, and each rule names the failure it prevents. Every skill is tested by running the same tasks with and without it.

## What a skill is

A skill is a folder with a `SKILL.md` file. An AI agent reads the short description at the top of `SKILL.md` and loads the whole file when a task matches it. The agent then reads the files in `references/` only when the task needs them. People can read the same files as a guide.

The skills follow the [Agent Skills specification](https://agentskills.io/specification), so any agent that reads that format can use them.

## Skills

Each folder under [skills/](skills/) is one skill. Its `README.md` says what the skill covers, when to use it, what it believes, and how it is tested. Browse the folder to see every skill.

## How to use the skills

With the `skills` CLI, which needs Node.js and `npx`:

```bash
npx skills add 18120158binh/data-engineering-skills
```

With Claude Code, copy or link a skill folder into one of these places:

- `~/.claude/skills/` to use it in every project;
- `.claude/skills/` inside a project to use it only there.

```bash
git clone https://github.com/18120158binh/data-engineering-skills.git
ln -s "$PWD/data-engineering-skills/skills/<name>" ~/.claude/skills/<name>
```

With another agent that reads Agent Skills, such as Cursor, Codex, or Gemini, copy the skill folder into that agent's skills folder or into `.agents/skills/` in your project. Check your agent's documentation for the folder it reads.

As a person, start at `skills/<name>/README.md`, then read `SKILL.md` and follow its links into `references/`.

## Adding a skill

Add one folder under `skills/`, named like the skill, with:

- `SKILL.md`: the frontmatter (`name`, `description`, `metadata.version`) and the rules;
- `README.md`: what the skill covers, when to use it, what it believes, its files, and its test cases;
- `references/`: the detail an agent reads on demand;
- `evals/`: the test cases.

This README does not list the skills, so a new skill needs no change here.

## How the skills are tested

Each skill has an `evals/` folder with one folder per test case. A case has:

- `prompt.md`: the task given to the agent;
- `case.yaml`: the outcome a good answer reaches;
- `graders/`: one check per file, each judged by a language model against the agent's work;
- sometimes `files/` and a script that copies them in, for tasks that review existing work.

Each case runs twice, once with the skill and once without, and the graders score both runs so the results can be compared.

## Contributing

Open an issue or a pull request. A change to a rule says which failure it prevents, ideally with an eval case that fails without the change.
