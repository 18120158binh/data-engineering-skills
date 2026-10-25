# Shared code in utils/

`utils/` holds the code that every region shares. Each region keeps its own DAG file, so the regional files of one DAG have a lot in common. `utils/` holds the common part once, so a fix there reaches every region and the regional files cannot drift apart.

## What belongs in utils/

Put code in `utils/` when more than one DAG file needs it:

- a client for an external system, such as a database, a replication tool, or a chat webhook;
- a helper that several DAG files call;
- the rules of one business area that every region applies the same way;
- SQL that the code fills in, under `utils/sql/`.

## What stays in the DAG file

- The region's own values, such as its timezone, worker queue, and cluster name.
- The DAG definition and the order of its tasks.
- Code that only one DAG file uses.

## How to write shared code

- Take the region's values as arguments. Shared code does not decide which region it runs in.
- Keep a client general. It knows its own system, and it knows nothing about a DAG or a business area.
- Log each call to an external system and what came back. Never log a secret: redact passwords and tokens in the client, and never log a webhook URL.
- Make every step that a retry or a rerun may repeat reach the same end state.

## How to change shared code

A change in `utils/` reaches every DAG file that imports the module, in every region. Treat it as a change to all of them.

1. Find every DAG file that imports the module:

   ```bash
   grep -rl "utils.<module>" <region>_dags/
   ```

   Include the DAGs the task did not name.
2. Read the contract of each DAG you found.
3. Find what the change could break beyond those callers: data formats, SQL templates, Variables, and anything else a symbol search misses. Prove the one fact the change's safety rests on by running real code.
4. When you change what a function takes or returns, move every caller in the same change and delete the old form. Do not leave a wrapper that keeps the old form alive.
5. Run the checks in section 6 of [SKILL.md](../SKILL.md) for every DAG file you found.
