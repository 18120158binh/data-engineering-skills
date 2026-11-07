#!/usr/bin/env python3
"""Wait until a worker's turn produces an event, then print it and exit.

Run it in the background after every hand-off, so the runtime wakes the main session when it ends.

Watch the PR (preferred):
  watch.py pr --cmd "<command printing the PR's head and reviews as JSON>" --head <sha> --seen <n>
           [--worker <herdr name>] [--interval 45] [--timeout 7200]

  The command must print {"head": "<sha>", "reviews": [{"commit": "<sha>", ...}, ...]},
  for example `python3 .agents/skills/pull-request/scripts/pr.py reviews 251`.
  Events:
    pushed    the PR head is no longer <sha>: the coder pushed (or anyone did)
    reviewed  more than <n> reviews, the newest on the current head: a verdict is in
    blocked   the Herdr worker is blocked on a prompt (needs the user)
    stalled   the Herdr worker is done or idle and nothing happened on the PR for 10 minutes:
              read its last message (`herdr agent read <name> --source recent-unwrapped`)
    timeout   nothing happened before --timeout

Watch the session (fallback, when the PR tool cannot list reviews):
  watch.py file --path <result file> [--worker <herdr name>] [--interval 15] [--timeout 7200]

  Events: written (the result file exists and is not empty), blocked, stalled, timeout.

Exit code 0 for written, pushed, or reviewed; 1 for blocked, stalled, or timeout; 2 on a usage error.
The script never reads a credential; the PR command does its own authentication.
"""

import argparse
import json
import os
import subprocess
import sys
import time

STALL_SECONDS = 600


def worker_status(name):
    if not name:
        return None
    try:
        out = subprocess.run(
            ["herdr", "agent", "get", name],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        ).stdout
        data = json.loads(out).get("result", {})
        return (data.get("agent") or data).get("agent_status")
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def pr_state(cmd):
    out = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=120, check=False
    ).stdout
    data = json.loads(out)
    return data["head"], data.get("reviews", [])


def finish(event, detail, code):
    print(json.dumps({"event": event, **detail}))
    sys.exit(code)


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="mode", required=True)
    pr = sub.add_parser("pr")
    pr.add_argument("--cmd", required=True)
    pr.add_argument("--head", required=True)
    pr.add_argument("--seen", type=int, required=True)
    f = sub.add_parser("file")
    f.add_argument("--path", required=True)
    for s in (pr, f):
        s.add_argument("--worker")
        s.add_argument("--interval", type=int, default=45 if s is pr else 15)
        s.add_argument("--timeout", type=int, default=7200)
    args = p.parse_args()

    start = time.time()
    quiet_since = None
    while time.time() - start < args.timeout:
        if args.mode == "pr":
            try:
                head, reviews = pr_state(args.cmd)
            except (OSError, ValueError, KeyError, subprocess.SubprocessError):
                head, reviews = args.head, []
            if head != args.head:
                finish("pushed", {"head": head, "reviews": len(reviews)}, 0)
            if len(reviews) > args.seen and reviews[-1].get("commit") == head:
                finish("reviewed", {"head": head, "review": reviews[-1]}, 0)
        elif os.path.exists(args.path) and os.path.getsize(args.path) > 0:
            finish("written", {"path": args.path}, 0)

        status = worker_status(args.worker)
        if status == "blocked":
            finish("blocked", {"worker": args.worker}, 1)
        if status in ("done", "idle"):
            quiet_since = quiet_since or time.time()
            if time.time() - quiet_since > STALL_SECONDS:
                finish("stalled", {"worker": args.worker, "status": status}, 1)
        else:
            quiet_since = None
        time.sleep(args.interval)
    finish("timeout", {}, 1)


if __name__ == "__main__":
    main()
