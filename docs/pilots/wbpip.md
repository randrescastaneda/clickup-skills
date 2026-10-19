# wbpip pilot results and handoff

## Selected target and current status

- Repository: `PIP-Technical-Team/wbpip`.
- ClickUp task supplied by the user: `https://app.clickup.com/t/37469623/868mjzgzh`.
- GitHub access: confirmed through the connected GitHub integration.
- GitHub default branch: `PROD`, confirmed from repository metadata.
- Package: R package `wbpip` (DESCRIPTION version 0.1.4 at inspection).
- Repository agent/binding files: none found in the inspected PROD tree.
- ClickUp connection: confirmed by authenticated official-MCP reads on 2026-10-19.
- Bound task: `Test task for MCP testing`, native ID `868mjzgzh`, status `backlog`.
- Verified Workspace: `37469623`; Space: `61389751` (`PIP Technical Team`).
- Verified home list: `193304782` (`PIP backend development`).
- Available statuses: `backlog`, `to do`, `in progress`, `in review`, `done`.
- Task description/acceptance: empty; pilot objective is the user's authorized
  test of scoped agent integration, not an inferred business deliverable.
- Created child: [Verify scoped agent updates](https://app.clickup.com/t/868mjzvmu),
  native ID `868mjzvmu`, parent `868mjzgzh`, same verified home list.
- GitHub target in the child's initial description: the existing wbpip repository.
- Progress comment: `90110280795570`, containing both URLs and a stable marker.
- Child status changed to `in progress`, read back, then restored to `backlog`.
- Repeated reads found one pilot child and one matching progress comment;
  the host workflow reused these records instead of repeating writes.
- Supplied parent status/description: preserved (`backlog`, empty description).
- wbpip issues/PRs/code changes: none. Issue creation returned HTTP 403,
  `Resource not accessible by integration`; the successful repository read/admin
  flag did not establish integration write permission.

These results validate the official **host MCP** path, including authenticated
scope reads, repository-associated child creation, linked progress, and a scoped
status update. They do not validate the local CLI/helper journal against live
services, live issue/PR backlinks, native activity hooks, or continuous sync.
The local helper behavior is covered separately by offline tests.

The official compact task response omitted `team_id`. Workspace hierarchy
verified the actual Workspace/Space, and list metadata matched the task's
Space/List. The task's plain markers were returned intact under `text_content`;
`markdown_description` escaped their brackets and wrapped URLs.

No binding file or agent instructions were published to wbpip. The `PROD` branch
is a target base, not a place for the pilot agent to push changes directly.

## Remaining pilot steps

Resolve the GitHub integration's issue-write permission failure, then create or
reuse an issue target and verify reciprocal backlinks/discussion reconciliation.
Check the GitHub App's repository access/Issues permission and organization
approval as applicable, or use a separately authenticated local `gh` environment
after the definite 403 rejection. Do not replay an uncertain mutation.

Verify a real draft PR linkage when a meaningful setup/documentation change is
needed, and independently verify native repository-to-Space mapping/automation
behavior. Test actual installed Codex, Claude Code, Copilot, and Kilo clients;
rendered configuration tests do not establish those clients' live behavior.

## Connect the agent that will run the pilot

The authenticated tools must be available in the environment running the test.
Signing into a local Codex instance does not authenticate a different ChatGPT
Work session.

For this ChatGPT Work session, the user can add a personal custom MCP plugin
under ChatGPT Plugins, using the server URL `https://mcp.clickup.com/mcp` and
OAuth authentication. Install/select that plugin when continuing the task.
Availability depends on the account/workspace's custom-MCP settings. The user
completes the sign-in; no token or password should be pasted into chat.

Alternatively, run the pilot in the user's own authenticated Codex environment.
Add the official server using Codex's MCP settings or its documented CLI flow,
then authenticate it there. Use the same task/repository and skills below.

## Repeatable pilot sequence

1. Read the task with an authenticated ClickUp tool. Verify native `id`,
   Workspace, home `list.id`, actual objective/acceptance criteria, and available
   statuses. Use hierarchy evidence for the official compact response's missing
   `team_id`; helpers still require their raw scope fields. Read existing children
   and creation markers so the pilot does not create a duplicate.
2. Read GitHub state and project instructions, confirm `PROD` is still the
   intended base, and use an isolated branch/worktree. Never push to PROD.
3. Bind the verified scope and objective. Include `--base-branch PROD` in
   `cu-work init`. Keep real task metadata local until its intended repository
   visibility is reviewed; wbpip is public.
4. Reuse child `868mjzvmu` after verifying scope and its creation marker. Resolve
   the intended GitHub target first; default issue creation must succeed before
   a new child. Use that child explicitly for test comments/status changes.
   Leave the supplied parent's status and description intact.
5. Record a short progress comment with a stable operation key. Repeat the
   identical call and verify one remote comment exists. Repeat the subtask
   creation with its original key and verify one child exists.
6. If a GitHub PR is needed, use a draft documentation/setup-only change, with
   no R/package behavior changes, and verify the intended public content before
   publishing it. Link the PR and pilot child in both directions. Preserve the
   PR body and verify repeated linkage does not duplicate a block/comment.
7. Confirm that a draft/open PR or pending/failed CI cannot mark the pilot
   child done. Do not merge a PR, delete tasks, or deploy as part of this pilot.
8. Record actual results and remaining gaps. Test CLI execution and other
   clients separately when their authentication/executables are available.

If the only available connection is the official host MCP, use host tools and
the skills' manual scope/recovery checks. This validates the host MCP workflow,
not the local `cup` adapter or helper journal. Label those results separately.

## Agent handoff prompt

Use the ClickUp skills from randrescastaneda/clickup-skills at
feat/clickup-project-workflows for a bounded integration pilot. Target
PIP-Technical-Team/wbpip, base PROD, and task
https://app.clickup.com/t/37469623/868mjzgzh. Start with an authenticated task
read, verify the true workspace/list/objective, and follow the sequence in
docs/pilots/wbpip.md. Keep test writes on a clearly labeled pilot child, use
stable operation keys, and verify duplicate prevention and PR linkage. Do not
implement the business task, change R/package behavior, alter the parent task's
status, merge, deploy, or claim a live check passed without observed evidence.
Report blockers and the minimal user action needed for authentication.
