# Integration contract

Read this in integration mode, before planning and again before the hand-back. It defines who owns the integration, what it may change, and when it is complete. [integration-playbook.md](integration-playbook.md) describes how to get there.

## Ownership

- The current agent owns the integration work package as a whole: it is the workflow owner and the execution orchestrator for the integration. This ownership covers only the integration process. It does not decide who owns normal engineering work in the target repository afterwards; that is resolved per request, as usual.
- Sub-agents may own bounded work packages: one repository's audit, one set of edits, one evaluation scenario.
- The current agent stays responsible for consolidating their results, resolving conflicts, verifying, and handing back.
- Every approval gate in the target repository stays in force.
- The user is the human approver for decisions about the integration itself.
- The repository's own approval gates are met by their designated approvers, such as a tech lead for schema design, a code owner for a pull request, or a security team for production permissions. Do not assume the user can satisfy or override them.

## Modification boundaries

- Audit before modifying.
- Keep existing project rules and workflows unless the user approved a change to them.
- Do not silently remove, override, or weaken an existing instruction.
- Do not change protected-branch, CI, merge, deployment, or production permissions without authorization.
- Keep changes scoped to the integration.

## Completion criteria

An integration of a repository is complete only when:

1. The project manager, the repository's instructions, and its capabilities are discoverable from where an agent starts.
2. Workflow resolution picks the expected mode for the repository's common work types.
3. Existing applicable workflows and custom skills are preserved and still work.
4. Every lifecycle phase has a named capability, or an acknowledged limitation.
5. Workflow ownership and execution orchestration are unambiguous for each work type.
6. Approval gates and delivery boundaries are preserved.
7. Every applicable standard scenario from the [playbook](integration-playbook.md#phase-5-evaluate-end-to-end) has been run, or replaced by an equivalent with the reason recorded.
8. Each scenario's result and the remaining integration gaps are reported with evidence.

Installing or copying files does not establish a successful integration. Do not report the integration as done while a required capability or evaluation remains unverified; report it as partially done, with what is missing.

## Evaluation status

Report each scenario as one of:

| Status | Meaning |
|---|---|
| Passed | Run, and every check met, with evidence |
| Failed | Run, and at least one check not met |
| Blocked | Could not run because of a missing access permission, dependency, or required approval |
| Not run | Not attempted, or the evaluation environment could not test the intended integration |

An unexecuted scenario is never passed.

## Delivery boundary

Integration does not authorize pushing, merging, or deploying anything unless the user asks for it, per [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries). Report each delivery step with its state, as defined in [handoff-contract.md](handoff-contract.md#result-and-delivery).

## Hand-back

Per repository:

- the expected mode per work type, and why;
- files added or changed;
- workflows and capabilities preserved;
- capabilities supplemented, and from which provider;
- each scenario with its status and evidence;
- known limitations and unresolved gaps;
- decisions the user must make;
- the delivery states;
- integration status: done, partially done, or blocked, where done requires every completion criterion above.
