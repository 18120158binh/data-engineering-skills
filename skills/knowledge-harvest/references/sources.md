# Where knowledge hides

Richest first. Read what exists, and skip the rest.

| Source | What it tends to hold | How to read it |
|---|---|---|
| Decision records | Decisions, the alternatives they beat, criteria, and reversals through `superseded_by` | Read every record. Follow each supersede chain to the trigger. |
| Agent instructions (`AGENTS.md`, `CLAUDE.md`, repo skills) | Rules the owner enforces, troubleshooting tables, routing | Separate the owner's skills from vendored ones. Check for a third-party notice. |
| Contracts and specs | Limits as numbers, failure rules, approval points, and the incident behind a limit | Look for "Why" lines and dates. |
| Known issues and incident notes | Failure stories, causes, and evidence labels | Note what was fixed and what is still open. |
| Runbooks and deployment notes | Tool gotchas, version pins, the order of operations, and things learned the hard way | Look for "never", "must", "do not", and dates. |
| Commit history | Fixes, reverts, and the reason in the message | `git log --format='%h %ad %s' --date=short`, then filter for `fix`, `revert`, and `superseded`. Read the diff of commits that carry a reason. |
| Pull request reviews | Rules a reviewer enforced, and findings that reversed a call | Comments that repeat across pull requests are unwritten rules. |
| Decision logs | Each call with its reason, evidence, and result | Rows whose result says superseded, reverted, or overturned. |
| Benchmarks and eval reports | Measured numbers, methods, and limitations | Keep the run count and the spread with the number. |
| Code comments that say why | Constraints a reader would not guess | Skip comments that only say what the code does. |
| Tests named after behavior | Rules the code is held to | A test name such as `test_a_nightly_burst_never_alerts` is a rule. |
| Agent sessions | Corrections the owner made, especially the same one twice | Read only the sessions of this project. Never sweep other projects or unrelated private chats. |
| Personal notes and memory files | Preferences and context | Usually one person's preferences, not repo rules. Label them so. |
