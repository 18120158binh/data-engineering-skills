#!/usr/bin/env bash
# Builds the orders pipeline with rules, a feature workflow, and one custom skill, as a target for integration mode.
set -eu

git init -q -b main .
git config user.name "Data Engineer"
git config user.email "engineer@example.com"

mkdir -p data logs notes tests

cat > AGENTS.md <<'AGENTS'
# AGENTS.md

Loads one CSV of orders per day into SQLite and reports daily totals. Run `python3 -m unittest discover -s tests` before you commit.
AGENTS

cat > load.py <<'PY'
import csv
import sqlite3


def load(db_path, csv_path, day):
    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE IF NOT EXISTS orders (order_id TEXT, day TEXT, amount REAL)")
    with open(csv_path, newline="") as f:
        rows = [(r["order_id"], day, float(r["amount"])) for r in csv.DictReader(f)]
    con.executemany("INSERT INTO orders VALUES (?, ?, ?)", rows)
    con.commit()
    con.close()
    return len(rows)
PY

cat > report.py <<'PY'
import sqlite3


def daily_total(db_path, day):
    con = sqlite3.connect(db_path)
    (total,) = con.execute("SELECT COALESCE(SUM(amount), 0) FROM orders WHERE day = ?", (day,)).fetchone()
    con.close()
    return total
PY

cat > data/orders-2026-10-13.csv <<'CSV'
order_id,amount
A-100,20.00
A-101,35.50
CSV

cat > data/orders-2026-10-14.csv <<'CSV'
order_id,amount
B-200,40.00
B-201,12.25
B-202,7.75
CSV

cat > logs/load-2026-10-14.log <<'LOG'
2026-10-15T01:00:02 run=1 load day=2026-10-14 file=data/orders-2026-10-14.csv
2026-10-15T01:00:03 run=1 inserted rows=3
2026-10-15T01:10:03 run=1 task timed out waiting for the success marker, scheduler will retry
2026-10-15T01:12:00 run=2 load day=2026-10-14 file=data/orders-2026-10-14.csv
2026-10-15T01:12:01 run=2 inserted rows=3
2026-10-15T01:12:01 run=2 success
LOG

cat > logs/load-2026-10-13.log <<'LOG'
2026-10-14T01:00:02 run=1 load day=2026-10-13 file=data/orders-2026-10-13.csv
2026-10-14T01:00:03 run=1 inserted rows=2
2026-10-14T01:00:03 run=1 success
LOG

cat > notes/bug.md <<'NOTE'
# Revenue doubled on 2026-10-14

The daily report shows 120.00 for 2026-10-14. The source file has three orders totalling 60.00. 2026-10-13 shows 55.50, which is right.
NOTE

cat > tests/__init__.py <<'PY'
PY

cat > tests/test_report.py <<'PY'
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from load import load
from report import daily_total

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ReportTest(unittest.TestCase):
    def test_total_for_one_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "orders.db")
            load(db, os.path.join(ROOT, "data", "orders-2026-10-13.csv"), "2026-10-13")
            self.assertAlmostEqual(daily_total(db, "2026-10-13"), 55.50)


if __name__ == "__main__":
    unittest.main()
PY

cat > CONTRIBUTING.md <<'DOC'
# Contributing

## Feature workflow

1. Open a proposal in `proposals/<slug>.md`: the goal, the data it touches, and how it will be tested.
2. A maintainer approves the proposal before any code is written.
3. Build on a branch named `feature/<slug>`, with tests.
4. Run `python3 -m unittest discover -s tests`.
5. Open a pull request; a maintainer reviews and merges.
DOC

mkdir -p proposals .claude/skills/data-quality-check
touch proposals/.keep
cat > .claude/skills/data-quality-check/SKILL.md <<'SKILL'
---
name: data-quality-check
description: Check a loaded day of orders for duplicates, negative amounts, and missing order ids before it is reported. Use after any change to the load step.
---

# Data quality check

Run `python3 -m unittest discover -s tests`, then query the orders table for the day: count duplicate order ids, negative amounts, and empty ids. Any non-zero count fails the check.
SKILL

git add -A
git commit -q -m "feat: load daily orders and report totals"
