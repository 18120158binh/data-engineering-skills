# Slice brief

The brief for one read-only subagent. Fill in the parts in angle brackets. Give each slice a different topic or set of repositories.

```
You are collecting knowledge from <owner>'s past work for <purpose>. Your slice is <topic or repositories>.

Read-only: do not edit, commit, or run anything that writes, and do not call any remote system.

Sources, richest first: <paths, with what each holds>.
Authorship: <owner> wrote <these>. <Teammate> wrote <those>. <These folders> are copied from another project, so label anything from them THIRD-PARTY.
Already captured, so note only briefly if you see it: <list, or a path to the existing skill>.

Find what is not captured yet: <the kinds of items this purpose needs, with a few examples of what to look for>.

Return, as your final message, a list of items in this shape:
<paste references/item-schema.md>

Rules:
- Every item has evidence: file:line or a commit hash, and a quote of at most two lines.
- Mark each item STATED, INFERRED, TEAM, or THIRD-PARTY.
- Prefer 20 well-evidenced items to 60 thin ones.
- Group the items by topic.
- Then list 3 to 6 failure stories worth using as examples, and anything you found that is wrong right now.
- Never copy a secret, a token, a password, a credentialed URL, an internal hostname, or customer data. Say that one exists and where.
```
