---
name: clickup-handoff
description: Resume a bound ClickUp project, review operation receipts, reconcile uncertain updates, and prepare a concise task handoff. Use at session start/end, after a failed update, or when handing work to a teammate or another coding agent.
license: MIT
compatibility: Requires the official ClickUp MCP authorized in the agent, or the optional cu-work local helper; GitHub through gh or an approved hosted connection.
---

# Resume or hand off work

<!-- selection-check:start -->
## First: which backends were selected?

The user selects the ClickUp mode and the GitHub backend at setup, independently of each other. Do not infer the selection from the tools that happen to be listed.

1. If the user, the project instructions or the setup report state the selection, use it. With a shell and the plugin source, `python3 scripts/setup.py status --client CLIENT` prints the recorded selection and changes nothing.
2. If nothing states it, assume the default, **hosted** ClickUp (official OAuth MCP, `https://mcp.clickup.com/mcp`) with **`gh`** for GitHub, and confirm it with the user before the first write.
3. The **hosted** GitHub backend (an approved hosted GitHub connection instead of `gh`) applies only when the user selected it.
4. **remote-only** permits hosted connections only: never `gh`, never a local ClickUp tool.
5. **local-helper** applies only when the user selected it and `get_bound_task` succeeds for a bound root task. A `clickup_work` server that merely starts is not enough. The local-helper steps in this skill apply only in this mode.

A selected backend that is missing, banned or unauthenticated means STOP and report; never switch backends on your own. One `gh` sign-in serves all authorized repositories: verify each project's exact repository and create no per-repository token. Never use `cup`, `cu-work` or a bridge for hosted ClickUp. Before any hosted write, follow the guarded protocol in the sibling skill `clickup-github`, file `references/official-mcp-issue-first.md`. Those are agent checks, outside helper receipts, locks and completion gates.
<!-- selection-check:end -->

Write multi-line text to a temporary file outside the repository (`$TMPDIR` on macOS and Linux, `%TEMP%` on Windows); `TEMP_DIR` in the examples stands for that folder.

## Hosted ClickUp (default and remote-only)

1. Read `.clickup/project.json` in the target worktree. Do not assume a helper journal exists.
2. Preserve your host operation evidence separately: keys, markers and returned IDs.
3. Read the task, comments and GitHub state as the rules below require, through the selected backends.
4. Reconcile issue and PR discussions with host tools when authorized, following the pagination and echo rules in `clickup-github`.
5. For an uncertain host call, reconcile the preserved host evidence and the remote markers directly. `cu-work reconcile` cannot clear or verify a host call it never recorded.

## Local-helper mode

Prefer the `clickup_work` MCP tools; each `cu-work …` line is the shell equivalent. If `cu-work` is not on PATH, use the managed launcher `CLICKUP_SKILLS_HOME/bin/cu-work` (`cu-work.cmd` on Windows; default folder `~/.local/share/clickup-skills/bin`) when it exists, otherwise the MCP tools only. Do not use an `npx` proxy as the normal way to run the helper.

1. Read the binding and `project_context` / `cu-work context` in the target worktree.
2. Run `sync_task_comments` / `cu-work sync-comments --task ID` for issue and PR discussions when authorized, observing the pagination and echo rules in `clickup-github`.
3. Inspect pending operations in the reported `local_state` file.
4. For a pending operation, inspect its remote marker or ID and the relevant task or PR.
5. Repeat the same helper call with identical arguments to allow marker-based reconciliation.
6. If the remote state cannot prove the outcome, stop that write.
7. Only after a complete inspection establishes the result, an operator may record it:

   ```bash
   cu-work --project-dir /absolute/worktree reconcile --key 'operation-key' --result-file TEMP_DIR/verified-result.json
   # Only after establishing the original write did NOT apply:
   cu-work --project-dir /absolute/worktree reconcile --key 'operation-key' --not-applied
   ```

8. For a partially linked PR, inspect and recover the `:github` and `:clickup` receipts independently.
9. Post an authorized update with `record_progress` / `cu-work progress --message-file ... --key ...`.

Reconciliation records an inspection decision; it does not inspect ClickUp itself.

## Rules for every selection

- Confirm the project, objective, active task, branch and repository before resuming.
- Read the actual task, its relevant comments, and the current GitHub issue, PR and check state. Verify the remote GitHub association markers.
- When agents work in parallel, pass an explicit task (`--task`) instead of changing shared focus.
- Local focus and receipts are not authoritative remote state.
- Do not print task bodies, credentials or the whole state file into unrelated logs.
- Never use `--not-applied` just to clear an inconvenient error.
- Never change backends to replay an uncertain write.
- Save the handoff as a task comment only when the user's work authorizes that update; otherwise return it in chat.
- Leave review and complete statuses unchanged unless the completion workflow establishes their evidence.
- Never claim a test, sync, deployment or merge occurred without evidence.

## Report

A short handoff: task URL, objective, current branch, PR and head SHA, completed work, checks actually run, blockers, pending operations, and the next action. End with any specific input needed from the user, or say that nothing is needed.
