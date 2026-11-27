#!/usr/bin/env python3
"""Start, brief, and list the main session's Herdr workers without a shell in between.

Every call to herdr passes its arguments as a list, so no shell rewrites a path
(Git Bash turns "/x/y" into "C:/Program Files/Git/x/y") or expands "$id" inside a brief.

  workers.py spawn --repo <path> --branch <b> --base <ref> --label <task-id> --name <worker>
                   [--max <n>]
      Creates the task's worktree and starts Claude in it. Refuses a repository path
      that is the home folder or not a Git repository, and, with --max, refuses when
      <n> or more agents are already live. The cap is the machine's, not the task's:
      take it from the owner's memory or the repository's settings. Prints {"event": "started", "name", "pane_id", "status"},
      or {"event": "blocked", ...} with the screen when the new session waits on a
      prompt only the user may answer (folder trust, a first-run dialog).

  workers.py send <worker> --brief-file <path> [--slash poteto-mode] [--settle 20]
      Sends the brief read from the file. With --slash, sends "/<slash> <brief>",
      presses Enter (Claude's command menu takes the first one), and confirms the
      worker started; if the brief still sits on the input line, presses Enter once more.
      Prints {"event": "working" | "blocked" | "not_started" | "failed", ...}; "failed"
      means herdr gave no state counter, so the script did not send.

  workers.py handoff --repo <main checkout> --name <lead name> [--resume .pm/state.md]
                     [--previous <old lead name>] [--settle 20]
      Hands the run to a fresh main session. Refuses a path that is the home folder, not a
      Git repository, or a linked worktree (the run belongs to the main checkout). Starts
      Claude there in a new Herdr workspace, sends "/engineering-lead resume <state>"
      (with "--previous <old lead name>", so the new session can close the old pane) as
      send --slash does, and prints {"event": "started" | "blocked" | "not_started" | "failed", ...}.
      Stop the old session only after "started".

  workers.py list [--task <task-id>] [--max <n>]
      Lists live agents named <task-id> or <task-id>-<role> (all named agents without it),
      with status and folder, and the live count against <max>. Run it after a merge:
      close every worker it lists for the task.

Exit code 0 on success, 1 when the worker is blocked, not started, or over the cap,
2 on a usage error.
"""

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time

ENV = {**os.environ, "MSYS_NO_PATHCONV": "1", "MSYS2_ARG_CONV_EXCL": "*"}
PROMPT_MARK = "❯"


def herdr(*args, timeout=60):
    out = subprocess.run(
        ["herdr", *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        env=ENV,
        check=False,
    )
    return out.stdout


def parse(out):
    try:
        result = json.loads(out).get("result")
    except (AttributeError, ValueError):
        return {}
    return result if isinstance(result, dict) else {}


def find_key(data, key):
    if isinstance(data, dict):
        if key in data:
            return data[key]
        data = list(data.values())
    if isinstance(data, list):
        for item in data:
            found = find_key(item, key)
            if found is not None:
                return found
    return None


def live_agents():
    agents = parse(herdr("agent", "list")).get("agents")
    if not isinstance(agents, list):
        finish(
            "failed", 1, step="agent list", reason="herdr did not return an agent list"
        )
    return agents


def state(name):
    data = parse(herdr("agent", "get", name))
    agent = data.get("agent") if isinstance(data.get("agent"), dict) else data
    return agent.get("agent_status"), agent.get("state_change_seq")


def status(name):
    return state(name)[0]


def unsubmitted(name, brief):
    """True when the brief sits on Claude's input line (the last line with its prompt mark).

    A long brief shows there as "[Pasted text #1 +N lines]". Any other text there may be
    Claude's own greyed suggestion, which an Enter would submit, so it does not count.
    """
    lines = [line for line in screen(name, 12).splitlines() if PROMPT_MARK in line]
    if not lines:
        return False
    return brief.splitlines()[0][:30] in lines[-1] or "[Pasted text" in lines[-1]


def wait_started(name, before_seq, seconds):
    """Wait until the worker works, blocks, or finishes a turn that began after before_seq.

    A worker kept across rounds sits in "done" between them, so "done" alone does not
    show that this prompt was taken.
    """
    end = time.time() + seconds
    while True:
        current, seq = state(name)
        if current in ("working", "blocked") or (
            current == "done" and seq != before_seq
        ):
            return current, True
        if time.time() >= end:
            return current, False
        time.sleep(2)


def screen(name, lines=15):
    return herdr("agent", "read", name, "--source", "visible", "--lines", str(lines))


def finish(event, code, **detail):
    print(json.dumps({"event": event, **detail}, ensure_ascii=False))
    sys.exit(code)


def repo_path(raw, main_only=False):
    path = pathlib.Path(raw).expanduser().resolve()
    if path == pathlib.Path.home().resolve():
        finish(
            "refused",
            2,
            reason="the repository path is the home folder",
            path=path.as_posix(),
        )
    if not (path / ".git").exists():
        finish("refused", 2, reason="not a Git repository", path=path.as_posix())
    if main_only and not (path / ".git").is_dir():
        finish(
            "refused",
            2,
            reason="a linked worktree, not the main checkout",
            path=path.as_posix(),
        )
    return path.as_posix()


def wait_for(name, wanted, seconds):
    end = time.time() + seconds
    current = status(name)
    while current not in wanted and time.time() < end:
        time.sleep(2)
        current = status(name)
    return current


def spawn(args):
    repo = repo_path(args.repo)
    live = len(live_agents())
    if args.max is not None and live >= args.max:
        finish("over_cap", 1, live=live, max=args.max)
    created = parse(
        herdr(
            "worktree",
            "create",
            "--cwd",
            repo,
            "--branch",
            args.branch,
            "--base",
            args.base,
            "--label",
            args.label,
            "--no-focus",
        )
    )
    pane = find_key(created, "pane_id")
    start_claude(args.name, pane, "worktree create", created)
    finish("started", 0, name=args.name, pane_id=pane, status="idle")


def start_claude(name, pane, step, reply):
    """Start Claude named <name> in <pane> and wait until it is idle; finish on anything else."""
    if not pane:
        finish("failed", 1, step=step, reply=reply)
    herdr("agent", "start", name, "--kind", "claude", "--pane", pane)
    current = wait_for(name, ("idle", "blocked"), 60)
    if current == "blocked":
        finish("blocked", 1, name=name, pane_id=pane, screen=screen(name))
    if current != "idle":
        finish(
            "failed",
            1,
            step="agent start",
            name=name,
            pane_id=pane,
            status=current,
            screen=screen(name),
        )


def deliver(worker, text, first_line, slash, settle):
    """Send text, confirm the worker started on it, and return (current status, took)."""
    before_seq = state(worker)[1]
    if before_seq is None:
        before_seq = state(worker)[1]
    if before_seq is None:
        finish(
            "failed",
            1,
            step="agent get",
            reason="herdr gave no state_change_seq, so a new turn cannot be told from the last one",
        )
    herdr("agent", "prompt", worker, text, timeout=120)
    if slash:
        herdr("agent", "send-keys", worker, "Enter")
    current, took = wait_started(worker, before_seq, settle)
    if not took and unsubmitted(worker, first_line):
        herdr("agent", "send-keys", worker, "Enter")
        current, took = wait_started(worker, before_seq, settle)
    return current, took


def send(args):
    brief = pathlib.Path(args.brief_file).read_text(encoding="utf-8").strip()
    if not brief:
        finish("refused", 2, reason="the brief file is empty", path=args.brief_file)
    text = f"/{args.slash} {brief}" if args.slash else brief
    current, took = deliver(args.worker, text, brief, args.slash, args.settle)
    if took and current in ("working", "done"):
        finish("working", 0, worker=args.worker, status=current)
    if took and current == "blocked":
        finish("blocked", 1, worker=args.worker, screen=screen(args.worker))
    finish(
        "not_started", 1, worker=args.worker, status=current, screen=screen(args.worker)
    )


def handoff(args):
    repo = repo_path(args.repo, main_only=True)
    created = parse(
        herdr("workspace", "create", "--cwd", repo, "--label", args.name, "--no-focus")
    )
    pane = find_key(created, "pane_id")
    start_claude(args.name, pane, "workspace create", created)
    prompt = f"resume {args.resume}" + (
        f" --previous {args.previous}" if args.previous else ""
    )
    current, took = deliver(
        args.name, f"/engineering-lead {prompt}", prompt, True, args.settle
    )
    if took and current in ("working", "done"):
        finish("started", 0, name=args.name, pane_id=pane, status=current)
    if took and current == "blocked":
        finish("blocked", 1, name=args.name, pane_id=pane, screen=screen(args.name))
    finish(
        "not_started",
        1,
        name=args.name,
        pane_id=pane,
        status=current,
        screen=screen(args.name),
    )


def list_workers(args):
    agents = live_agents()
    owned = [
        {
            "name": a["name"],
            "status": a.get("agent_status"),
            "cwd": a.get("cwd"),
            "pane_id": a.get("pane_id"),
        }
        for a in agents
        if a.get("name")
        and (
            not args.task
            or a["name"] == args.task
            or a["name"].startswith(args.task + "-")
        )
    ]
    print(
        json.dumps(
            {"live": len(agents), "max": args.max, "workers": owned},
            indent=2,
            ensure_ascii=False,
        )
    )
    sys.exit(1 if args.max is not None and len(agents) > args.max else 0)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("spawn")
    for flag in ("--repo", "--branch", "--base", "--label", "--name"):
        s.add_argument(flag, required=True)
    s.add_argument("--max", type=int)
    m = sub.add_parser("send")
    m.add_argument("worker")
    m.add_argument("--brief-file", required=True)
    m.add_argument("--slash")
    m.add_argument("--settle", type=int, default=20)
    h = sub.add_parser("handoff")
    h.add_argument("--repo", required=True)
    h.add_argument("--name", required=True)
    h.add_argument("--resume", default=".pm/state.md")
    h.add_argument("--previous")
    h.add_argument("--settle", type=int, default=20)
    ls = sub.add_parser("list")
    ls.add_argument("--task")
    ls.add_argument("--max", type=int)
    args = p.parse_args()
    {"spawn": spawn, "send": send, "handoff": handoff, "list": list_workers}[args.cmd](
        args
    )


if __name__ == "__main__":
    main()
