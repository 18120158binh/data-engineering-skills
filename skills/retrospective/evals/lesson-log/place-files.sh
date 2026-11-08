#!/usr/bin/env bash
# Places a lead's lesson log, two project skills, and the engineering-lead skill as it was when the log was written.
set -eu
cp -R "$(dirname "$0")/files/." .
git init -q -b main .
git add -A
git -c user.name="Lead" -c user.email="lead@example.com" commit -q -m "chore: snapshot after the staging rollout"
