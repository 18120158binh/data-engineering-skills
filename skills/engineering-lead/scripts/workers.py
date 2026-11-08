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
      worker started; if the prompt still sits unsubmitted, presses Enter once more.
      Prints {"event": "working" | "blocked" | "not_started", ...}.

  workers.py list [--task <task-id>] [--max <n>]
      Lists live agents whose name starts with <task-id> (all named agents without it),
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
        return json.loads(out).get("result", {})
    except (AttributeError, ValueError):
        return {}


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
    return parse(herdr("agent", "list")).get("agents", [])


def status(name):
    data = parse(herdr("agent", "get", name))
    return (data.get("agent") or data).get("agent_status")


def screen(name, lines=15):
    return herdr("agent", "read", name, "--source", "visible", "--lines", str(lines))


def finish(event, code, **detail):
    print(json.dumps({"event": event, **detail}, ensure_ascii=False))
    sys.exit(code)


def repo_path(raw):
    path = pathlib.Path(raw).expanduser().resolve()
    if path == pathlib.Path.home().resolve():
        finish("refused", 2, reason="the repository path is the home folder", path=path.as_posix())
    if not (path / ".git").exists():
        finish("refused", 2, reason="not a Git repository", path=path.as_posix())
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
            "worktree", "create", "--cwd", repo, "--branch", args.branch,
            "--base", args.base, "--label", args.label, "--no-focus",
        )
    )
    pane = find_key(created, "pane_id")
    if not pane:
        finish("failed", 1, step="worktree create", reply=created)
    herdr("agent", "start", args.name, "--kind", "claude", "--pane", pane)
    current = wait_for(args.name, ("idle", "blocked"), 60)
    if current == "blocked":
        finish("blocked", 1, name=args.name, pane_id=pane, screen=screen(args.name))
    finish("started", 0, name=args.name, pane_id=pane, status=current)


def send(args):
    brief = pathlib.Path(args.brief_file).read_text(encoding="utf-8").strip()
    text = f"/{args.slash} {brief}" if args.slash else brief
    herdr("agent", "prompt", args.worker, text, timeout=120)
    if args.slash:
        herdr("agent", "send-keys", args.worker, "Enter")
    current = wait_for(args.worker, ("working", "blocked"), args.settle)
    if current not in ("working", "blocked") and brief.splitlines()[0][:30] in screen(args.worker, 30):
        herdr("agent", "send-keys", args.worker, "Enter")
        current = wait_for(args.worker, ("working", "blocked"), args.settle)
    if current == "working":
        finish("working", 0, worker=args.worker)
    if current == "blocked":
        finish("blocked", 1, worker=args.worker, screen=screen(args.worker))
    finish("not_started", 1, worker=args.worker, status=current, screen=screen(args.worker))


def list_workers(args):
    agents = live_agents()
    owned = [
        {"name": a["name"], "status": a.get("agent_status"), "cwd": a.get("cwd"), "pane_id": a.get("pane_id")}
        for a in agents
        if a.get("name") and (not args.task or a["name"].startswith(args.task))
    ]
    print(json.dumps({"live": len(agents), "max": args.max, "workers": owned}, indent=2, ensure_ascii=False))
    sys.exit(1 if args.max is not None and len(agents) > args.max else 0)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
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
    ls = sub.add_parser("list")
    ls.add_argument("--task")
    ls.add_argument("--max", type=int)
    args = p.parse_args()
    {"spawn": spawn, "send": send, "list": list_workers}[args.cmd](args)


if __name__ == "__main__":
    main()
