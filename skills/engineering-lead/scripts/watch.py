#!/usr/bin/env python3
"""Wait until a worker's turn produces an event, then print it and exit.

Run it in the background after every hand-off, so the runtime wakes the main session when it ends.

Watch the PR (preferred):
  watch.py pr --cmd "<command printing the PR's head and reviews as JSON>" --head <sha> --seen <n>
           [--acked <sha>] [--worker <herdr name>]... [--log <lesson log>]
           [--interval 45] [--timeout 7200]

  Give --worker once per worker in the loop. In a Herdr pair that hands rounds to itself,
  give both: one of them is always idle while the other works.

  The command must print {"head": "<sha>", "reviews": [{"commit": "<sha>", ...}, ...]},
  for example `python3 .agents/skills/pull-request/scripts/pr.py reviews 251`.
  Events:
    pushed    the PR head is no longer <sha>: the coder pushed (or anyone did)
    reviewed  more than <n> reviews, the newest on the current head: a verdict is in.
              Also at start, whatever <n> says, when the newest review already approves the
              current head ("already": true): a watcher restarted after a crash or a memory kill
              must not treat an approval nobody acted on as seen. To wait on a head you
              already acted on as approved (for CI, the user's go-ahead, or a held merge),
              pass it as --acked <sha>.
              A review counts as an approval when its "state" or "verdict" is approved or
              approve, or its body contains "Verdict: approve" or "Verdict: approved".
    blocked   a Herdr worker is blocked on a prompt (needs the user)
    stalled   every Herdr worker given is done or idle and nothing happened on the PR for 10 minutes:
              read each listed worker's last message (`herdr agent read <name> --source recent-unwrapped`);
              a worker waiting on its own background shells (a build, a test run) also
              shows idle, so check the screen before acting
    unreadable  the PR command failed 3 times in a row: fix the command or the access
    timeout   nothing happened before --timeout
    unlogged  (with --log) the lesson log has not changed since the last stage this target
              closed: write its log line, then watch again

  --log makes logging part of the loop. The events that close a stage (reviewed, written,
  stalled) record the log's size in a stamp beside it, one per watched PR command or result
  file (<log>.<id>.watched); the next watcher of that target refuses to start until the log's
  size has changed.

Watch the session (fallback, when the PR tool cannot list reviews):
  watch.py file --path <result file> [--worker <herdr name>]... [--log <lesson log>]
           [--interval 15] [--timeout 7200]

  Events: written (the result file exists and is not empty), blocked, stalled, timeout.

Exit code 0 for written, pushed, or reviewed; 1 for blocked, stalled, unreadable, unlogged,
or timeout; 2 on a usage error.
The script never reads a credential; the PR command does its own authentication.
"""

import argparse
import json
import hashlib
import os
import re
import subprocess
import sys
import time

STALL_SECONDS = 600
MAX_FAILED_READS = 3


def worker_status(name):
    if not name:
        return None
    try:
        out = subprocess.run(
            ["herdr", "agent", "get", name],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        ).stdout
        data = json.loads(out).get("result", {})
        return (data.get("agent") or data).get("agent_status")
    except (
        AttributeError,
        OSError,
        TypeError,
        ValueError,
        subprocess.SubprocessError,
    ):
        return None


def pr_state(cmd):
    out = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    ).stdout
    data = json.loads(out)
    return data["head"], data.get("reviews") or []


def all_quiet(statuses):
    """True when there are workers and none of them is working; one working worker keeps the loop alive."""
    return bool(statuses) and all(s in ("done", "idle") for s in statuses.values())


def is_approval(review):
    for key in ("state", "verdict"):
        if str(review.get(key) or "").lower() in ("approved", "approve"):
            return True
    return bool(re.search(r"verdict:\s*approved?\b", str(review.get("body") or ""), re.I))


STAMPED_EVENTS = ("reviewed", "written", "stalled")


def log_size(log):
    return os.path.getsize(log) if os.path.exists(log) else -1


class LogGate:
    """One stamp per watched target, holding the log's size when its last stage closed."""

    def __init__(self, log, target):
        self.log = log
        digest = hashlib.sha1(target.encode("utf-8")).hexdigest()[:10]
        self.stamp = f"{log}.{digest}.watched"

    def logged(self):
        if not os.path.exists(self.stamp):
            return True
        with open(self.stamp, encoding="utf-8") as f:
            return log_size(self.log) != int(f.read().strip() or -1)

    def close_stage(self):
        with open(self.stamp, "w", encoding="utf-8") as f:
            f.write(f"{log_size(self.log)}\n")


def finish(event, detail, code, gate=None):
    if gate and event in STAMPED_EVENTS:
        gate.close_stage()
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
    pr.add_argument("--acked")
    f = sub.add_parser("file")
    f.add_argument("--path", required=True)
    for s in (pr, f):
        s.add_argument("--worker", action="append", default=[])
        s.add_argument("--log")
        s.add_argument("--interval", type=int, default=45 if s is pr else 15)
        s.add_argument("--timeout", type=int, default=7200)
    args = p.parse_args()
    log = None
    if args.log:
        log = LogGate(args.log, args.cmd if args.mode == "pr" else args.path)
        if not log.logged():
            finish("unlogged", {"log": args.log}, 1)

    start = time.time()
    first_read = True
    quiet_since = None
    failed_reads = 0
    while time.time() - start < args.timeout:
        if args.mode == "pr":
            try:
                head, reviews = pr_state(args.cmd)
            except (
                OSError,
                TypeError,
                ValueError,
                KeyError,
                subprocess.SubprocessError,
            ) as err:
                failed_reads += 1
                if failed_reads >= MAX_FAILED_READS:
                    finish("unreadable", {"error": repr(err)}, 1, log)
                head, reviews = args.head, []
            else:
                failed_reads = 0
                newest = reviews[-1] if reviews else {}
                if (
                    first_read
                    and newest.get("commit") == head
                    and head != args.acked
                    and is_approval(newest)
                ):
                    finish("reviewed", {"head": head, "review": newest, "already": True}, 0, log)
                first_read = False
            if head != args.head:
                finish("pushed", {"head": head, "reviews": len(reviews)}, 0, log)
            if len(reviews) > args.seen and reviews[-1].get("commit") == head:
                finish("reviewed", {"head": head, "review": reviews[-1]}, 0, log)
        elif os.path.exists(args.path) and os.path.getsize(args.path) > 0:
            finish("written", {"path": args.path}, 0, log)

        statuses = {w: worker_status(w) for w in args.worker}
        blocked = [w for w, s in statuses.items() if s == "blocked"]
        if blocked:
            finish("blocked", {"worker": blocked[0]}, 1, log)
        if all_quiet(statuses):
            quiet_since = quiet_since or time.time()
            if time.time() - quiet_since > STALL_SECONDS:
                finish("stalled", {"workers": statuses}, 1, log)
        else:
            quiet_since = None
        time.sleep(args.interval)
    finish("timeout", {}, 1)


if __name__ == "__main__":
    main()
