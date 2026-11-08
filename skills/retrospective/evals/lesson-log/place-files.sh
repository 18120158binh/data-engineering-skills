#!/usr/bin/env bash
# Places a lead's lesson log, two project skills, and the generic engineering-lead skill the lead ran.
set -eu
here="$(cd "$(dirname "$0")" && pwd)"
cp -R "$here/files/." .
mkdir -p skills
cp -R "$here/../../../engineering-lead" skills/engineering-lead
rm -rf skills/engineering-lead/evals
git init -q -b main .
git add -A
git -c user.name="Lead" -c user.email="lead@example.com" commit -q -m "chore: snapshot after the staging rollout"
