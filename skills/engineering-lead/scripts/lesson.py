#!/usr/bin/env python3
"""Write the lesson log: lessons, round lines, and lesson status, one line each.

  lesson.py add --log <file> --task <task> --where <where> --change <change> --text <text>
                [--repeats <n>]
      Appends "<YYYY-MM-DD> <task> lesson <n>: [Repeats lesson <m>. ]<text>
      Next action: <where> / <change> / open", where <n> is the highest lesson number
      in the log plus one (1 when there is none). Refuses an empty --where or --change:
      a lesson without a destination is read once and lost.

  lesson.py round --log <file> --task <task> --round <n> --verdict <verdict> --sha <sha>
      Appends "<YYYY-MM-DD> <task> round <n>: <verdict> on <sha>".

  lesson.py done --log <file> --n <n> --ref <commit or PR>
      Changes lesson <n>'s status from "open" to "done <ref>". Exit 1 when lesson <n>
      is missing or not open.

  lesson.py open --log <file>
      Prints the open lessons: number, task, where, change.

Every write appends, except done, which rewrites that one line.
Exit code 0 on success, 1 when done finds nothing to close, 2 on a usage error.
"""

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

LESSON = re.compile(r"^\S+ (?P<task>\S+) lesson (?P<n>\d+): (?P<body>.*)$")
NEXT = re.compile(
    r" Next action: (?P<where>.*?) / (?P<change>.*) / (?P<status>open|done\b.*)$"
)


def one_line(text):
    return " ".join(str(text).split())


def read_lines(log):
    path = pathlib.Path(log)
    return path.read_text(encoding="utf-8").splitlines() if path.exists() else []


def append(log, line):
    path = pathlib.Path(log)
    lead = ""
    if path.exists() and path.stat().st_size:
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            lead = "" if f.read(1) == b"\n" else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{lead}{line}\n")
    print(line)


def lessons(lines):
    """Yield (index, number, task, match of the Next action) for every lesson line."""
    for i, line in enumerate(lines):
        m = LESSON.match(line)
        if m:
            yield i, int(m["n"]), m["task"], NEXT.search(line)


def today():
    return datetime.datetime.now().astimezone().date().isoformat()


def refuse(reason):
    print(json.dumps({"event": "refused", "reason": reason}))
    sys.exit(2)


def add(args):
    where, change, text = (
        one_line(args.where),
        one_line(args.change),
        one_line(args.text),
    )
    if not where or not change:
        refuse("--where and --change must not be empty")
    n = max((num for _, num, _, _ in lessons(read_lines(args.log))), default=0) + 1
    repeats = f"Repeats lesson {args.repeats}. " if args.repeats else ""
    append(
        args.log,
        f"{today()} {one_line(args.task)} lesson {n}: {repeats}{text} Next action: {where} / {change} / open",
    )


def round_line(args):
    append(
        args.log,
        f"{today()} {one_line(args.task)} round {args.round}: {one_line(args.verdict)} on {args.sha}",
    )


def done(args):
    lines = read_lines(args.log)
    for i, num, _, nxt in lessons(lines):
        if num == args.n and nxt and nxt["status"] == "open":
            lines[i] = lines[i][: nxt.start("status")] + f"done {one_line(args.ref)}"
            pathlib.Path(args.log).write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(lines[i])
            return
    print(json.dumps({"event": "not_open", "lesson": args.n}))
    sys.exit(1)


def list_open(args):
    for _, num, task, nxt in lessons(read_lines(args.log)):
        if nxt and nxt["status"] == "open":
            print(f"{num}\t{task}\t{nxt['where']}\t{nxt['change']}")


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    for flag in ("--task", "--where", "--change", "--text"):
        a.add_argument(flag, required=True)
    a.add_argument("--repeats", type=int)
    r = sub.add_parser("round")
    for flag in ("--task", "--round", "--verdict", "--sha"):
        r.add_argument(flag, required=True)
    d = sub.add_parser("done")
    d.add_argument("--n", type=int, required=True)
    d.add_argument("--ref", required=True)
    o = sub.add_parser("open")
    for s in (a, r, d, o):
        s.add_argument("--log", required=True)
    args = p.parse_args()
    {"add": add, "round": round_line, "done": done, "open": list_open}[args.cmd](args)


if __name__ == "__main__":
    main()
