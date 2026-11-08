# Lesson log: orders-stream rollout to the staging cluster

Started 2026-10-03. The lead appends here as things happen. Format per entry: what happened, the cost, the lesson, and what changed.

## Lessons

1. **The cloud dry run does not check account limits.** `create-node-group --dry-run` passed for 8 nodes; the real call failed on the account's vCPU quota. Cost: a resize to 5 nodes mid-rollout. Lesson: read the quota before sizing. Changed: the rollout-layer skill says so.
2. **The billing page lags by hours.** It showed $0 spend six hours into the rollout. Lesson: trust the cost projection script, not the page.
3. **The vendor console spells "retention" wrong on one form.** Harmless.
4. **A change under `services/` rebuilt every image**, so a docs-site change restarted all four Flink jobs. Lesson: separate builds per artifact. Changed: added `docs/**` to paths-ignore.
5. **Changing a FlinkDeployment's flinkConfiguration restarts the job** with a savepoint upgrade. Lesson: put UI access rules in the ingress, not in Flink config.
6. **Git Bash rewrote `/metrics/...` to `C:/Program Files/Git/metrics/...`** in a worker prompt, and the worker read the wrong path. Lesson: export MSYS_NO_PATHCONV=1 before sending a prompt.
7. **The reviewer found a real defect in every PR** (an unauthenticated /metrics path, a retry that doubled rows, a token with global read). Keep the coder/reviewer split.
8. **The lead's fix brief for PR #41 round 2 named only the newest finding** and dropped round 1's two required findings; the reviewer caught it on round 3. Cost: one extra round.
9. **The agent harness blocked `terraform apply`** for the worker. Lesson: plan applies as user steps with paste-ready commands.

## Delivery log

- 2026-10-04: PRs #41, #42 merged after review. Cleaned up their worktrees.
- 2026-10-04: Lesson 10: the laptop ran out of memory with 6 workers plus two Maven builds; the harness killed the lead's watcher. Rule for this machine: at most 4 live workers.
- 2026-10-05: Lesson 11: a load test showed the job "RUNNING" while it restarted every 30 minutes. The runner only watched job state. Lesson: watch restart count and exception history.
- 2026-10-05: Lesson 12 (lesson 4 recurred): a change to `.github/workflows/test-sim.yml` was not in paths-ignore, so all four Flink jobs restarted again. A deny-list misses new files. Fixed in #47 with per-image change detection (each image builds only when its own folder changed).
- 2026-10-05: Lesson 13: the harness blocked a worker from writing a secret to the cluster. Plan secret creation as a user step.
- 2026-10-06: Lesson 14: lesson 6 again. A prompt with `"C:\work\$id-brief.md"` kept `$id` literal; the worker opened a file that did not exist. Rule: build paths with forward slashes.
- 2026-10-06: Lesson 15: PR #49's v2 pages relied on the layout's session check, which the framework does not rerun on client navigation; a signed-out user could still read data. The reviewer caught it. The rule went to the two other page coders by message.
- 2026-10-06: Lesson 16: PRs #50 and #51 each passed CI, merged back to back, and broke a test on the base together. Only a trial merge on the current base would have caught it.
- 2026-10-07: Lesson 17: the harness blocked the lead's batched cleanup (forced worktree removal plus remote branch deletes). Do cleanup in small steps.
- 2026-10-07: Lesson 18: a reviewer's test fixture copied the code's assumption about a metrics label, so the test passed while the real query never matched. Use captured real responses.
- 2026-10-07: Lesson 19: the console showed a greyed-out suggestion in a worker's input box; the lead read it as the user's unsent text.
- 2026-10-08: Lesson 20: lesson 6 a third time. A double-quoted Windows `--cwd` lost its backslashes and two workers opened in the home folder. Rule: forward slashes for every path, always.
- 2026-10-08: Lesson 21: the owner set the rule for review rounds: ONE coder and ONE reviewer per task, kept alive across all rounds; the lead sends the review to the same coder and the new head to the same reviewer, and closes both only after merge. Starting fresh workers each round cost a cold start every time and is how lesson 8 happened.
- 2026-10-08: Lesson 22: the harness blocked a worker's database write during an approved recovery; the owner's approval in chat did not reach the worker's session. The recovery stopped half-done with jobs suspended. Lesson: before an approved live operation, list every write it needs and get permission in place first.
- 2026-10-08: Lesson 23: the lead wrote local time with a `Z` suffix in a brief. The laptop is UTC+7.
