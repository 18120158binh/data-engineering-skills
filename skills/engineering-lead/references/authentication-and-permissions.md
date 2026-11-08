# Authentication and permissions

Read this when a task will or may need an external action (push, PR or MR, review, approval, merge, release, deploy, a change to an external system), before planning that action and again before the hand-back. A read-only or local-only task does not need it.

The engineering lead coordinates the checks. It does not store, provision, refresh, or revoke credentials; the execution environment owns those. It does not implement GitHub or GitLab either; it works through the capabilities the repository and the environment already provide.

## Contents

- [Four separate conditions](#four-separate-conditions)
- [Where the identity comes from](#where-the-identity-comes-from)
- [Git transport and provider API are separate channels](#git-transport-and-provider-api-are-separate-channels)
- [Checking without side effects](#checking-without-side-effects)
- [The preflight for one action](#the-preflight-for-one-action)
- [Choosing the tool](#choosing-the-tool)
- [Delegated workers](#delegated-workers)
- [When something fails](#when-something-fails)
- [What to record](#what-to-record)

## Four separate conditions

An external action needs authentication, technical permission, user authorization, and repository policy, all four and each on its own evidence. [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries) defines them and owns authorization: what the user's words cover, and why vague requests or available credentials never do. This guide covers the other three.

- **Authentication**: which identity is acting, and whether it can authenticate on the channel this action uses.
- **Technical permission**: whether that identity can do this action on this resource. Being logged in says nothing about whether it can push to `main` or approve a PR.
- **Repository policy**: branch protection, required checks and reviews, PR or MR templates, merge-strategy limits, release and deploy gates, organizational security controls.

Keep the four apart in the plan, in execution, and in the report. "Blocked" means little until it says which one is missing.

## Where the identity comes from

**Local execution.** Reuse what the user already configured: an SSH agent, a Git credential helper, `gh` or `glab` authentication, or a repository-native integration. Do not assume any of them is set up. Find the repository's provider and the transport its remote uses first, then check the mechanism that transport needs.

**Remote or container execution.** Use only the credentials the platform or an approved integration supplies for the session, with the identity and repository scope it assigns. You may read non-secret metadata about them: the runtime, the provider, the repository scope, the principal, whether authentication is available, and when it expires, if the platform says. Do not copy local credentials into the session, search its filesystem for secrets, read key or token contents, or write injected secrets into the workspace. If the platform provides no approved mechanism, the action is blocked: report the setup the environment needs.

Either way:

- Do not search repository files, shell history, dotfiles, or unrelated environment variables for credentials.
- Do not extract a credential's value from where the environment keeps it, whether a Git credential helper, a CLI's credential store, a keychain, or a platform secret, to copy it somewhere else. That rules out `git credential fill`, reading a helper's store, and writing a token to a file, a variable, a script, a `curl` header, or a worker's brief, even when the output is filtered. Act through the approved interface instead: let Git use its own helper on push and fetch, let `gh` or `glab` use their own login, and let the platform's integration authenticate. Credential handling belongs to the environment; the agent never holds the raw value.
- Do not ask the user to paste a token, key, or password into the chat. Point them to the secure setup instead, such as `gh auth login` or `glab auth login` run in their own terminal, or the platform's secret settings.

## Git transport and provider API are separate channels

| Channel | Operations | Needs |
|---|---|---|
| Git transport (SSH or HTTPS) | Clone, fetch | Read access to the repository |
| | Push | Write access, and the branch's protection allowing it |
| Provider API (CLI, MCP tool, REST) | Read a PR or MR | API read access |
| | Create or update a PR or MR, request a review | Those permissions on the repository |
| | Submit a review, approve | Review permission, and a policy that lets this identity approve |
| | Merge | Merge permission, and every required gate met |

An SSH key that pushes does not give API access, and a logged-in `gh` does not make a broken SSH remote work. Check each channel the action uses, even when one credential happens to serve both. Deployment has its own authentication, owned by the deployment platform.

## Checking without side effects

Use read-only checks, and keep their output out of files and logs when it can contain secrets. Some examples follow. The repository's own tools, or the platform's connectors, take precedence when they cover the same check.

| To find out | Examples |
|---|---|
| Provider and transport | `git remote get-url origin`. Report the host and path only; if the URL embeds a token, do not print it, and tell the user it should not be there. |
| Transport read access | `git ls-remote --heads origin` |
| API identity | `gh auth status`, `glab auth status` |
| Repository permission | GitHub: `gh api repos/{owner}/{repo} --jq .permissions`. GitLab: `glab api projects/:id`, then its `permissions` field |
| Branch rules | GitHub: `gh api repos/{owner}/{repo}/branches/BRANCH --jq .protected` for classic protection, and `gh api repos/{owner}/{repo}/rules/branches/BRANCH` for rulesets. GitLab: `glab api projects/:id/protected_branches`. Some of these need more than read access; a refusal leaves the policy unknown. |

No read-only check proves that a push to a particular branch will be accepted. Repository-level write access still meets branch protection and push rules. When the checks leave a permission open, report it as unknown. Do not push to find out.

Before any write the user authorized:

1. Work out the channels the write needs (Git transport, provider API).
2. Run the read-only authentication checks for each.
3. Establish the permission this action needs on this resource.
4. If the permission is denied or still unknown, stop before the write and say what would establish it, such as a provider CLI login or the user confirming that this identity can push. The user's authorization is not evidence of permission.
5. Never run the write to discover the permission. A write that fails for missing authentication or permission is not a permission check; it is the probe this rule forbids.

Statuses keep the report honest:

| Condition | Statuses |
|---|---|
| Authentication, per channel | authenticated, unauthenticated, expired, unknown, not required |
| Technical permission | granted, denied, unknown, not required |
| User authorization | granted, denied, requires approval, not authorized, unknown |
| Repository policy | satisfied, blocked, unknown, not applicable |

Never turn unknown into granted on the strength of a general account role.

## The preflight for one action

For each external action:

1. Name the action and its target: the provider, the repository or resource, the branches or IDs.
2. Note whether execution is local or remote.
3. Work out which channels the action needs, and check authentication on each. For a request with several steps, check every channel the whole request needs before the first side effect: a PR request whose API is unusable should not leave a pushed branch with no PR.
4. Check the technical permission for this action on this resource, with read-only checks only.
5. Check the user's authorization and its scope, per [conflict-resolution.md](conflict-resolution.md#side-effect-and-delivery-boundaries).
6. Check the repository's and the organization's policy and gates. A known gate that is not met blocks the action. Provider-side rules you could not read stay unknown. For an authorized push to a work branch or a new PR, the documented rules are enough and the provider enforces the rest. For a merge, a deploy, or an approval, where the gates decide the outcome, unknown blocks.
7. Run the action only when all four hold, and only that action and its direct prerequisites.
8. Confirm the result on the provider: the remote branch points at the pushed commit (`git ls-remote origin <branch>`), the PR or MR exists with the expected head, the merge or deploy shows as done. A command that exits 0 is not that confirmation when the state can be queried.
9. Record the result and the delivery state per [execution-lifecycle.md](execution-lifecycle.md#final-report).

When a condition fails, stop before that action's side effect and report which condition failed. Local work that does not depend on the action can go on.

How you express the action is up to you. A note such as "create_pull_request, github, org/repo, feature/x into main, asked by the user: 'open a PR'" is enough. There is no required format and no service to build.

## Choosing the tool

Pick the tool for a provider operation through [repository-adaptation.md](repository-adaptation.md#capabilities-for-external-actions), as for any phase: the repository's own skill or script first, such as a project `pull-request` skill, then installed provider skills, MCP tools, or connectors, then the provider's CLI or API. Do not require `gh`, `glab`, SSH, HTTPS, or any particular product when something the repository provides does the same job.

## Delegated workers

A subagent, a worker in another environment, a container, or a remote session resolves its own identity and permissions. It may have none, or different ones, from the parent. The brief for a worker whose task involves an external action carries:

- the provider and the repository;
- the actions it may perform, and the ones it must not;
- the project rules and gates that apply;
- the evidence it must return.

The user's approval given to the main session does not carry into a worker's session: the worker's harness decides on its own permission rules, and it may block a write the user approved in chat. Plan such writes as user steps, or get the permission in place before the work starts ([worker-contract.md](worker-contract.md#the-coder-brief), the side effects in the brief).

It never carries keys, tokens, passwords, credential files, or secret-bearing environment values. The parent still coordinates the work package, reconciles what the worker reports against the provider's state, and reports the final delivery.

## When something fails

| What happened | What to do |
|---|---|
| No authentication on the channel | Report which channel, and the secure way to set it up. Do not ask for the secret in chat. |
| Credentials expired | Ask for a refresh or re-provisioning through the environment that owns them. Do not hunt for others. |
| Permission denied or missing | Report the action and resource that lack the permission. Do not retry as another identity unless the user and the environment explicitly authorize that identity. |
| A policy gate blocks it | Report the gate and leave it in place. Do not work around branch protection, required reviews, CI, or deploy approvals. |
| Timeout or an unclear response | Query the provider first: does the PR, the pushed ref, the approval, or the merge already exist? Retry only when it did not happen and a retry is safe. |
| Partly done | Report each part on its own, such as branch pushed and PR not opened. Do not roll back the part that worked, and do not repeat it. |

## What to record

Record what helps the next decision, not every check. The trail gets a decision such as "PR creation blocked: provider API not authenticated", not where the credential lives.

Fine to record: the provider and repository, local or remote execution, a non-sensitive identity such as the account name or bot name, the action asked for and the one performed, the outcome of each check, the source of the authorization, the policy outcome, the resulting resource's ID or URL, and the final result.

Never record, in any artifact, plan, brief, decision record, log, or report: tokens, keys, passwords, secret-bearing headers or environment values, credential files, or unredacted authentication output.
