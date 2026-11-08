# Runtime adapters

Read this when the main session is about to start workers. The coder and reviewer roles, their briefs, and their results are the same in every runtime ([worker-contract.md](worker-contract.md)); this guide covers how each runtime creates, talks to, watches, and closes them.

## Contents

- [The logical interface](#the-logical-interface)
- [Choosing the runtime](#choosing-the-runtime)
- [Herdr: persistent sessions](#herdr-persistent-sessions)
- [Native subagents](#native-subagents)
- [Waiting without going deaf](#waiting-without-going-deaf)
- [Ownership and cleanup](#ownership-and-cleanup)

## The logical interface

| Operation | Purpose |
|---|---|
| detect | Find which worker runtimes are usable here |
| spawn | Create a worker for a role |
| send | Give it an assignment or a follow-up |
| wait | Wait for a result or a change of state |
| read | Get its output and status |
| close | End a worker the main session owns |

These are concepts. Runtimes expose them differently, and some not at all: never claim persistent workers when the runtime only has one-shot subagents.

## Choosing the runtime

Use **Herdr** by default when the main session runs inside a Herdr pane (`HERDR_ENV=1`) and the `herdr` CLI answers, unless the user or the repository says to use subagents. Running this skill inside Herdr is the user's choice of Herdr for its workers.

Otherwise use **native subagents** (Claude Code's agent tool, or the equivalent in the harness). If neither is available, say so and execute directly only where the task is small enough ([SKILL.md](../SKILL.md)). Record which runtime was used and why.

## Herdr: persistent sessions

One coder session and one reviewer session per task, each in its own pane, kept across rework rounds so they keep their context. Commands below were checked against Herdr's CLI; the installed `herdr --help` and `herdr agent` output win over this table if they differ.

Use [`scripts/workers.py`](../scripts/workers.py) for spawn and send. It calls Herdr with argument lists, so no shell rewrites a path or expands `$` in a brief; it refuses the home folder, a folder that is not a repository, and starting past the machine's cap; and it confirms a slash prompt was submitted. **Why**: the same quoting failure (Git Bash rewriting `/paths`, `$id` kept literal, backslashes lost from `--cwd`) came back four times after each was answered with a written rule. The table shows the underlying commands.

| Operation | How |
|---|---|
| spawn | `workers.py spawn --repo <repository> --branch <task branch> --base <base> --label <task-id> --name <task>-coder [--max <n>]`, which runs: `herdr worktree create --cwd <repository> --branch <task branch> --base <base> --label <task-id> --no-focus` gives the task its own workspace and a ready pane; take the pane id from the JSON reply. The reviewer gets its own worktree on a review branch from the task branch (`herdr worktree create ... --branch review/<task-id> --base <task branch>`), so it never touches the coder's checkout; each round it resets its own worktree to the PR's new head. Never split from your own pane: `HERDR_PANE_ID` can be stale, and other sessions may share your folder. Without a worktree, create a new workspace for the task instead of guessing your pane. Then `herdr agent start <name> --kind claude --pane <pane id>`. Names are unique, lowercase, such as `<task>-coder`, `<task>-reviewer`. Read identifiers from the JSON replies; do not guess them |
| send | `workers.py send <name> --brief-file <path> [--slash poteto-mode]`, which runs: `herdr agent prompt <name> "<text>"`. A plain prompt is submitted by `agent prompt` itself: do not send another Enter, or it submits Claude's own input suggestion. A prompt that starts with a slash command, such as `/poteto-mode <brief>`, is a three-step protocol, not an option: send the text with `agent prompt`, then submit it with `herdr agent send-keys <name> Enter` (Claude's command menu takes the first Enter), then confirm in `agent read` that the command was submitted and the status became `working`. A prompt sent right after the agent starts can sit unsubmitted; the script presses Enter once more when the brief is still in the input box |
| wait | `herdr agent prompt ... --wait --until done --timeout <ms>` for a plain prompt, or `herdr agent wait <name> --until done --until idle --timeout <ms>` after the status has become `working`. A wait on an agent that is already idle returns at once, so check that work started |
| read | `herdr agent read <name> --source recent-unwrapped --lines <n>`, plus `herdr agent get <name>` for the status. The read includes screen chrome and Claude's own input suggestions, so use it only for short replies. A full result goes in a result file ([below](#result-files)) |
| close | `herdr pane close <pane id>` ends the pane and the agent in it |

The number of live workers is bounded by the machine (memory, CPU), not by the plan. Keep the owner's cap in their memory or the repository's settings and pass it as `--max`; a harness short of memory kills background processes such as the main session's watcher first.

Things that stop a Herdr worker:

- **Folder trust.** Claude blocks at startup in a folder it has not trusted (status `blocked`, `agent_not_ready`). Start workers in a trusted folder, such as a worktree inside an already-trusted repository path, or ask the user to confirm. Never answer a trust or permission prompt for the user.
- **Permission prompts mid-task.** Status `blocked` means a question or an approval is waiting. Read it; if it is a permission request, report it to the user rather than approving it.
- **The coder runs `poteto-mode`.** Start the coder's assignment with `/poteto-mode <brief>` where pstack is installed. That is how a user-only skill gets started legitimately: in the worker's own session, as its first prompt.

The reviewer can be started with the coder and left idle, or started when there is a commit to review.

### Result files

In Herdr, the screen is a poor channel for a long result, so a worker writes its full result (changes, commit SHA, checks and their output, findings, blockers) to `.pm/<task-id>/<role>-<round>.md` and replies with the path. A native subagent returns its result as its final message instead; no file is needed. Either way, that is the worker's report. `state.md` is the main session's record and only the main session writes it; it reads the result file, checks it, and records the outcome. Where `.pm/` is not ignored by Git, use the same outside location as the task state ([execution-lifecycle.md](execution-lifecycle.md#where-it-lives)).

### Blocked is not failed

A worker in `blocked` is waiting on a prompt: folder trust, a permission request, or a question. Record it as blocked with the prompt it shows, tell the user what it needs, and keep the worker. Do not mark it finished or failed and spawn a replacement; two workers would then do the same assignment.

## Native subagents

The harness creates a fresh agent per assignment and ends it when it returns.

| Operation | How |
|---|---|
| spawn and send | One call to the agent tool, with the brief. The coder is `poteto-agent` when pstack defines it (it follows poteto-mode's principles, but cannot run poteto-mode's playbooks); otherwise a general-purpose agent with the same coder contract, told which principles to follow. The reviewer is a fresh general-purpose agent |
| wait | The call returns with the result; a background agent sends a notice when done |
| read | The returned message, and any file the brief asked for |
| close | Handled by the harness. A background agent still running can be stopped with the harness's stop mechanism |

Keep one coder and one reviewer for the whole task here too: send each later round to the same agent through the harness's message-to-agent mechanism, and close both only after the merge. Start a new instance only when the harness cannot continue an agent; its brief then carries every open finding and the current commit. **Why**: a fresh agent each round pays a cold start every time and loses findings in the hand-over. The main session keeps the task state.

## Waiting without going deaf

Wait with `scripts/watch.py` in the background, never with a blocking loop and never on screen text. It watches the PR (head changes and new reviews, through the repository's PR tool) or, as the fallback, the worker's result file, and it also reports a worker that is blocked or has stopped without producing anything. [SKILL.md](../SKILL.md) lists the events and what to do on each.

While a watcher runs, the main session stays free to answer the user: answer from the task state and the worker's current status, then carry on ([execution-lifecycle.md](execution-lifecycle.md#answering-a-status-question)).

## Ownership and cleanup

Record each worker in the task state as soon as spawn succeeds:

| Field | Why |
|---|---|
| Task id | Which issue it belongs to |
| Role | Coder or reviewer |
| Name | The name the main session gave it |
| Pane id | The pane the main session created (Herdr) |
| Agent session id | The agent in that pane, from the spawn reply |
| Working directory | The repository or worktree it was given |
| Status | Starting, working, blocked, done, or closed |

Act only on workers whose identity came from the main session's own spawn. Never pick an agent from Herdr's list because it is called `coder` or `reviewer`, or because it is idle.

- The main session owns only the workers it started, by the names it gave them. Herdr lists every agent in the user's session, including other projects' sessions and other reviewers: never send to, close, or rename those.
- Never stop the Herdr server or close panes the main session did not create.
- Close the coder and reviewer after the task is merged, or when the user cancels or asks to stop early; not before. Closing a pane ends its agent; for native background agents, use the harness's stop mechanism. If the runtime cannot end a worker, say so: marking it closed in the state does not stop it.
- Remove worktrees and branches the task created, following the repository's rules, and only those.

## Workspace for the task

Use a worktree only where the repository's rules allow one; follow its documented path and branch conventions when it has them.

- **Herdr:** `herdr worktree create --cwd <repository> --branch <task branch> --base <base ref> --path <path per the repository's convention> --label <task-id> --no-focus` creates the Git worktree and a Herdr workspace for it with a ready pane. Start the coder in that pane, and the reviewer in a pane split from it. A worktree of a repository the agent already trusts started without a trust prompt in the probe; a path outside any trusted repository may still prompt.
- **Native subagents, or Herdr not in use:** `git worktree add`, at the repository's conventional path.
- **Cleanup**, after the merge or on cancellation: `herdr worktree remove --workspace <id>` removes the worktree, its Herdr workspace, and the agents in it. It leaves the branch; delete the task branch only per the repository's rules, and only once it is merged or the user agrees. Use `git worktree remove` for a worktree made with Git.
