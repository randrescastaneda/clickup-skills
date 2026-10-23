# GitHub and ClickUp setup

## Contents

1. [Choose the integration layer](#choose-the-integration-layer)
2. [Enable native activity links](#enable-native-activity-links)
3. [Optional ClickUp automations](#optional-clickup-automations)
4. [Use the workflow tools](#use-the-workflow-tools)
5. [Use host MCPs directly](#use-host-mcps-directly)
6. [Ownership and continuous operation](#ownership-and-continuous-operation)
7. [Verify and troubleshoot](#verify-and-troubleshoot)

## Choose the integration layer

| Layer | What it does | Setup |
| --- | --- | --- |
| This repository's CLI / `clickup_work` MCP | Creates a GitHub target before each subtask, records backlinks, mirrors progress, reconciles discussion snapshots, gates completion | Install `cu-work`, `gh`, and the selected ClickUp runtime; bind the project |
| Host ClickUp + GitHub MCPs | Agents perform the same workflow with available service tools | Authenticate both MCPs; load the shared skills |
| Native ClickUp GitHub connection | Associates GitHub activity with tasks outside an agent session | Workspace/repository administrator setup below |
| Native GitHub Automations | Runs selected task/issue actions on configured events | Optional ClickUp plan feature below |

Connecting an MCP authenticates an agent. It does not prove the native GitHub
connection or an automation rule is enabled. Our remote URL markers are portable
crosslinks; they are not an API for installing native integrations.

## Enable native activity links

The native GitHub integration is available on every ClickUp plan. Repository
admins add repositories; ClickUp owners/admins configure Workspace connections
and Space mappings. Guests and limited members cannot use it.

1. In ClickUp, open Workspace avatar → Apps → GitHub → Workspace → Connect.
   Authorize the intended GitHub account and select/save repositories.
2. In GitHub's App Center page, open Settings → Add repo; select the working repo.
3. Select that repo → + Add Space; choose the Space containing the bound tasks.
4. Teammates needing personal commands connect their own account under Apps →
   GitHub → Connect.
5. Include `CU-TASK_ID` in branch names, commits, or PR descriptions. Our PR
   managed block includes it. Check the task's GitHub panel/activity feed.

Use an actual native ID, for example `CU-86native`; `Closes #86native` is not a
ClickUp reference. A pasted URL alone does not replace the repository/Space
mapping. See [ClickUp's integration instructions][integration] for screenshots
and account-specific authorization details.

## Optional ClickUp automations

GitHub Automation integrations require Business or above, the Automation
ClickApp enabled by a Workspace owner/admin, and repository admin permission.
Existing-task actions require an already linked commit, branch, or PR.

From the target List/Folder/Space: robot icon → Create Automation → GitHub.
Connect the account, choose the exact repository, configure trigger/conditions/
action, and create the rule. Branch and label conditions are case-sensitive.

Suggested team rules:

| Trigger | Condition | Action policy |
| --- | --- | --- |
| Pull Request Linked | Base equals the binding's base | Add a review reminder; agent decides readiness |
| Pull Request Review Created/Updated | Intended repository/branches | Notify the task owner |
| CI/CD Status Changed | Intended repository/branches | Record a check reminder; preserve failed/pending state |
| Pull Request Merged | Intended base | Request acceptance verification; agent runs the completion gate |
| Task created | Explicit intake scope | Optional Create Issue action, **only if agents are not also creating that issue** |

Choose one issue-creation owner to prevent duplicates. Avoid automatic Done on
merge: merge alone does not verify task acceptance. See [ClickUp's automation
instructions][automations] for available triggers/actions and conditions.

## Use the workflow tools

Run commands from a bound worktree with each teammate's own authentication.
The helper executes GitHub operations through `gh`, even when called through
our MCP. Host GitHub MCP calls are a separate agent-driven path.

```bash
# Default: create/reuse an issue, then a child with the issue URL already present.
cu-work --project-dir /absolute/project subtask --task 86native \
  --title 'Validate response' --description-file /tmp/acceptance.md \
  --key '86native:validate:v1'

# Reuse an existing issue or PR; no additional issue is created.
cu-work --project-dir /absolute/project subtask --task 86native \
  --title 'Test edge cases' --description-file /tmp/acceptance.md \
  --github-target https://github.com/OWNER/REPO/issues/42 --key '86native:edges:v1'

# Associate an existing task, or use --target new-issue --title '...' to create one.
cu-work --project-dir /absolute/project link-github --task 86child \
  --target https://github.com/OWNER/REPO/issues/42 --key '86child:issue42:v1'

# Link every implementation PR, preserving its existing description.
cu-work --project-dir /absolute/project link-pr --task 86child --pr 43 --key '86child:pr43:v1'

# Linked progress is posted on ClickUp and associated issue/PR discussions.
cu-work --project-dir /absolute/project progress --task 86child \
  --message-file /tmp/progress.md --key '86child:tests:v1'

# Import human discussion snapshots from either side; repeat safely.
cu-work --project-dir /absolute/project sync-comments --task 86child
# Or: --direction to-clickup / --direction to-github
```

Use an explicit repository URL as `--github-target` for repository-level
planning that needs no issue. Such tasks have no GitHub discussion thread;
progress contains the repository URL, and comment sync requires an issue/PR.

| CLI | Workflow MCP tool |
| --- | --- |
| `subtask` | `create_bound_subtask` (`github_target` optional) |
| `link-github` | `link_github_target` (`target`, optional new-issue `title`/`description`) |
| `link-pr` | `link_pull_request` |
| `progress` | `record_progress` |
| `sync-comments` | `sync_task_comments` (`direction` optional) |
| `phase` | `set_task_phase` |

Supply the absolute `project_dir` and native task ID to MCP tools. Every new
subtask gets a verified target. If no target exists, the default creates an
issue in the bound repository first. If creating the child/backlink fails,
preserve the successful issue and resume with identical arguments/key. Read
pending receipts and remote markers before any uncertain retry.

A nonexistent issue/PR URL is an error, not permission to invent that number.
Use `new-issue` to allocate an issue. Create a PR through `gh`/GitHub MCP only
after a branch with meaningful changes exists, then link it. Missing repository
creation requires explicit owner/name/visibility and a new binding; never
silently create or redirect work to a different repository.

## Use host MCPs directly

For **OAuth-only onboarding**, use
[the fail-closed host issue-first protocol](../../skills/clickup-github/references/official-mcp-issue-first.md)
*before any write*. Hosted official ClickUp OAuth does not authenticate the
separate local `cup` CLI or provide helper receipts/locks. When the agent
cannot verify a bound Workspace/List/root/repository or a complete prior
operation outcome, stop instead of creating a duplicate.

## Use host MCPs directly

Without the local executables, load `clickup-github` and `clickup-work-task`.
Discover current tool schemas, then:

1. Verify task identity, workspace, home list, ancestry, repository, and base.
   Some official compact task responses omit `team_id`; verify the explicit
   Workspace via hierarchy and the task's Space/List rather than assuming it
   from the URL. Request descriptions/subtasks/status definitions when needed.
   Read `text_content` for plain markers when returned Markdown escapes brackets
   or wraps URLs; the live official-MCP pilot exhibited that formatting.
2. Search/read the complete relevant issue/child/comment sets. Create or reuse
   the GitHub target before creating the ClickUp subtask. Include
   `[cu-work-github:TARGET_URL]` in its description.
3. Preserve the issue/PR body and add a task-specific block containing the
   ClickUp URL, `CU-TASK_ID`, and objective. Record the GitHub URL on ClickUp.
4. Include source URLs/IDs and stable provenance markers in mirrored comments;
   skip generated mirrors. Reconcile each service separately after failures.
5. Enforce the same merged-PR/latest-head-CI/acceptance gate before Done.

The [official ClickUp tool inventory][mcp] exposes task/comment operations. It
does not currently document tools for installing native GitHub connections or
automation rules. Its task-link tools relate ClickUp tasks to each other. Use
the setup steps above for native integration and automation configuration.

## Ownership and continuous operation

| Data | Authority / conflict rule |
| --- | --- |
| Task objective and acceptance criteria | ClickUp; do not replace it with an issue description |
| Code, reviews, CI, merge state | GitHub; link original evidence |
| Task-to-artifact identity | Remote managed markers plus verified canonical URLs |
| Issue/PR human body text | Preserve; change only our task-specific block |
| Discussion | Source comment remains authoritative; copies carry provenance |
| Completion | Explicit agent verification; a closed issue alone is insufficient |

`sync-comments` runs when invoked. It imports GitHub issue comments, PR
conversation comments, submitted reviews, and inline review comments; it
exports ClickUp **top-level** comments. Mirrored comments are snapshots with
source links/IDs. An edited source produces a new content revision, while
deletions are not propagated. It does not synchronize arbitrary task fields,
assignees, labels, or status in both directions.

Host agents should use the [shared provenance format](../../skills/clickup-github/references/synchronization.md)
so helper reconciliation can recognize their existing copies after handoff.

The reviewed local ClickUp backends expose a single comment page. The helper
stops at 25 comments instead of assuming a complete history. For complete local
histories, explicitly select routing.comment_reader=clickup-api with its private
environment credentials as described in the worker guide; all writes remain
on the selected upstream runtime. Fetch threaded replies with host tools. GitHub
discussion reads paginate completely. Replies to pending/unsubmitted GitHub
reviews are not available until the service exposes them.

Run reconciliation at session start and handoff. Native integration continues
activity links while agents are offline; configured native automations handle
their selected events. Neither installing these skills nor authenticating MCPs
starts an always-on, bidirectional comment synchronizer. Teams needing that
can prepare the optional [polling worker](../sync-worker.md) on one authenticated
machine. It uses the same receipts, scope checks and echo suppression, defaults
to a read-only preview, and bounds new mirrors per pass. The current local
25-comment limit applies to the default readers. The explicit complete-history
reader supports longer discussions; live worker acceptance remains unfinished. One writer per task across
machines is still required. This package does not start a service or install
a webhook automatically.

## Verify and troubleshoot

- Test one child with an issue; verify the target exists before the child,
  both URLs are recorded, and original issue/PR text remains intact.
- Repeat the same operation key, then repeat comment reconciliation. Confirm
  no duplicates. Test a partial failure without replaying the successful side.
- Add a `CU-TASK_ID` branch/PR reference; verify native activity separately.
  If absent, check repository/Space mapping, account permissions, and ID format.
- If an expected tool is absent, reload/select that plugin in the actual agent
  session. Another editor's sign-in does not authenticate this environment.
- If GitHub reads succeed but writes return `403 Resource not accessible by
  integration`, check the app installation for the **repository owner account
  or organization**, not only the signed-in user's personal installation. The
  wbpip pilot was fixed by installing the app on `PIP-Technical-Team`. Select
  the intended repositories and review requested permissions/organization
  approval. User-level repository admin permission does not establish app access.
  See [GitHub's installation settings guide](https://docs.github.com/en/apps/using-github-apps/reviewing-and-modifying-installed-github-apps).
- Keep failed CI, draft/open/unmerged PRs, and unverified acceptance out of Done.
- Sharing comments also shares their content with the bound repository's
  audience. Bind the intended project and use directional sync where appropriate.

Verified source pages: 2026-10-19. UI and plan details can change; consult the
linked primary instructions when setting up a Workspace.

[integration]: https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration
[automations]: https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations
[mcp]: https://developer.clickup.com/docs/mcp-tools
