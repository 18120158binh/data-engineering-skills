# Red flags

Reject or revise an option that shows one of these, and record why.

- **A lock to serialize writers, or a retry or a sorted batch to dodge a deadlock.** These move the contention instead of removing it. Give each row one writer.
- **A shared row that many owners update**, such as a counter or a total. Derive it with a view over the owners' rows.
- **A random id or a plain insert on a path that can replay.** A replay writes a second row.
- **A fix for one case that every new case would need again.** A rule that holds for one case, but needs its own patch for every new function, is a design problem.
- **Every worker polling a database for its configuration.** It brings version skew between workers, a thundering herd on start, and threads the framework does not manage. Stream the changes instead.
- **A second decider or a copy that can drift**: a cache that ignores later merges, a duplicate schema file, a second copy of the rules behind a lookup.
- **Silent loss or a silent default.** A drop, a cap, or a fallback that nobody counts or alerts on. A loss without an alert is a loss nobody will fix.
- **A changeable attribute used as identity**, such as an email. Identify by values that never change, such as an issuer and a subject.
- **A truncation cap whose answers depend on how active a user is.**
- **Content or personal data in logs.**
- **Free-form nested structures that the publish step cannot check**, such as condition trees of any depth. Prefer a typed shape that can be validated, unless the gain is worth the ordering and cycle checks it needs.
- **A feature the deployed version does not have.**
- **An agent that changes production.** It writes the command for a person to run.
- **Unbounded concurrency against a fragile dependency.** Cap it across the whole run.
- **An LLM or other optional step that can block the main result.** An optional step can cost time, never the answer or the alert.
- **Exactly-once assumed end to end** across systems that do not share a transaction.
