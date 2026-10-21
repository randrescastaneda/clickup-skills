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
- Initial 2026-10-19 attempt: no wbpip issue/PR/code changes. Issue creation returned HTTP 403,
  `Resource not accessible by integration`; the successful repository read/admin
  flag did not establish integration write permission.

These initial results validate the official **host MCP** path, including authenticated
scope reads, repository-associated child creation, linked progress, and a scoped
status update. The 2026-10-20 follow-up below also verifies issue/PR backlinks
and controlled PR conversation transfers. Local CLI/helper journal behavior is
covered separately by offline tests; native hooks and continuous sync are unverified.

The official compact task response omitted `team_id`. Workspace hierarchy
verified the actual Workspace/Space, and list metadata matched the task's
Space/List. The task's plain markers were returned intact under `text_content`;
`markdown_description` escaped their brackets and wrapped URLs.

No binding file or agent instructions were published to wbpip. The `PROD` branch
is a target base, not a place for the pilot agent to push changes directly.

## Live GitHub follow-up: 2026-10-20

The accessible GitHub App installations initially included the user's personal
account but not `PIP-Technical-Team`. After the user installed the app for the
organization, that installation became visible and the same issue-creation
operation succeeded. Reading the public repository and seeing user-level admin
permission had not established the app's ability to write to it.

| Check | Observed result |
| --- | --- |
| Issue creation | [wbpip #269](https://github.com/PIP-Technical-Team/wbpip/issues/269), with a managed backlink to the existing child |
| Child reuse | `868mjzvmu`, same verified parent/List; no additional child |
| PR creation | [wbpip #270](https://github.com/PIP-Technical-Team/wbpip/pull/270), draft, base `PROD` |
| PR scope | One new file, `docs/clickup-agent-pilot.md`, 32 lines; existing `^docs$` R-build exclusion |
| PR head | `be4baf54610f5291071d3d52185a7235f4a30890` |
| Body preservation | Original PR description/review notes retained; one task-specific managed block |
| Reciprocal links | Issue/PR bodies link the child; scoped ClickUp association comments link issue/PR |
| ClickUp → GitHub fixture | Source `90110280918641`; destination PR comment `6291826233` |
| GitHub → ClickUp fixture | Source PR comment `6291808000`; destination `90110280919036` |
| Second reconciliation pass | Exactly one copy for each canonical provenance key; generated mirrors skipped |
| Completion | Withheld because PR is draft/open and unmerged; child remains `backlog` |
| Parent preservation | Parent remains `backlog`, description empty, one pilot child |

The conversation transfers used explicitly labeled, controlled test comments.
They validate the host MCP/skill procedure and shared source-event format, not
live helper execution, native webhook delivery, inline review/reply transfers,
or exact-once behavior across simultaneous machines. The GitHub connector's
comment-write tool is documented for PR conversation comments; plain issue
comment writes were not exercised through it. The helper's `gh` issue-comment
path and review-type parsing remain offline-tested.

The pilot branch is `chore/CU-868mjzvmu-agent-integration-pilot`. Only that branch
received the documentation commit; nothing was pushed directly to `PROD`,
merged, or deployed. A draft PR with successful linkage is not completion evidence.

## Remaining pilot steps

The permission repair, issue creation, draft PR linkage, and controlled two-way
PR discussion checks passed. No further user input is needed for that bounded
host-MCP pilot. Keep #269/#270 available for review; no merge is part of the test.

Independently verify native repository-to-Space mapping/automation behavior,
live local `cup`/REST runtime credentials, long histories/threaded replies, and
actual installed Codex, Claude Code, Copilot, and Kilo clients. Rendered config
tests do not establish installed-client behavior. These are rollout acceptance
steps rather than unresolved results of the completed conversation test.

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
main for a bounded integration pilot. Target
PIP-Technical-Team/wbpip, base PROD, and task
https://app.clickup.com/t/37469623/868mjzgzh. Start with an authenticated task
read, verify the true workspace/list/objective, and follow the sequence in
docs/pilots/wbpip.md. Keep test writes on a clearly labeled pilot child, use
stable operation keys, and verify duplicate prevention and PR linkage. Do not
implement the business task, change R/package behavior, alter the parent task's
status, merge, deploy, or claim a live check passed without observed evidence.
Report blockers and the minimal user action needed for authentication.
