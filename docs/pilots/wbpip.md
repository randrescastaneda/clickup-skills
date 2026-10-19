# wbpip pilot handoff

## Selected target and current status

- Repository: `PIP-Technical-Team/wbpip`.
- ClickUp task supplied by the user: `https://app.clickup.com/t/37469623/868mjzgzh`.
- GitHub access: confirmed through the connected GitHub integration.
- GitHub default branch: `PROD`, confirmed from repository metadata.
- Package: R package `wbpip` (DESCRIPTION version 0.1.4 at inspection).
- Repository agent/binding files: none found in the inspected PROD tree.
- ClickUp task title, workspace, home list, objective, and statuses: **not read or verified**.
- Live ClickUp writes / wbpip changes: **none** during this preparation.

Do not infer `team_id` or list membership from the URL's path. No usable
`.clickup/project.json` is created until an authenticated task read supplies
the actual scope fields. The `PROD` branch is a target base, not a place for
the pilot agent to push changes directly.

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

## First pilot sequence

1. Read the task with an authenticated ClickUp tool. Verify native `id`,
   `team_id`, home `list.id`, actual objective/acceptance criteria, and available
   statuses. Read existing children so the pilot does not create a duplicate.
2. Read GitHub state and project instructions, confirm `PROD` is still the
   intended base, and use an isolated branch/worktree. Never push to PROD.
3. Bind the verified scope and objective. Include `--base-branch PROD` in
   `cu-work init`. Keep real task metadata local until its intended repository
   visibility is reviewed; wbpip is public.
4. Create or reuse one clearly labeled integration-pilot child task under the
   selected task. Use that child explicitly for test comments/status changes.
   Leave the supplied parent task's status and description intact.
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
