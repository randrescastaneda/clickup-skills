---
name: clickup-github
description: Link bound ClickUp tasks with GitHub branches, pull requests, checks, and completion evidence through gh or GitHub MCP. Use to create/link a PR, reflect review or merge state in ClickUp, or coordinate task implementation across both systems.
---

# Connect the task and the pull request

Load the binding and verify the active task's native ID, workspace, list, and ancestry. Check the exact GitHub owner/repo and base branch. Include the ClickUp task URL and objective in PRs. Never run GitHub `Closes #N` syntax for a ClickUp task number.

1. Inspect the working branch, changes, tests, and any existing PR. Create a branch/PR only when appropriate to the user's work; preserve existing branches and descriptions. Prefer the project's own branch convention, with the task ID where useful. Avoid duplicate PRs by looking up the branch first.
2. Use `gh` for complete ordinary GitHub operations, or discover the installed GitHub MCP's repository, pull-request, file, status, and check tools. Do not assume tool namespace prefixes. Pin explicit owner/repo arguments; do not rely on a tool's current repository default.
3. Link both directions. When `gh` and the local ClickUp runtime are available:

   ```bash
   cu-work --project-dir /absolute/worktree link-pr --task 86native --pr 42 --key '86native:pr42:link:v1'
   ```

   Or call `link_pull_request`. The helper adds/updates a task-specific managed block without replacing other PR content and posts the PR URL to the task. Separate operation receipts permit reconciliation after one service succeeds. It does not create the PR or change task status.
4. With GitHub MCP instead of `gh`, first fetch PR metadata and body. Verify its URL is exactly `https://github.com/OWNER/REPO/pull/NUMBER` and its base is the configured branch. Preserve the body, append/update a `<!-- clickup-skills:TASK_ID -->` block containing the task URL and objective, then verify the saved body. Record the PR URL on the verified ClickUp task with a stable marker. Preserve successful work if the second service fails; reconcile only that side before retrying. Re-read before updating to reduce concurrent-edit risk.
5. Set the configured review status only when work is ready for review; keep draft/incomplete work in progress. `cu-work phase --phase review` uses the exact configured status name; it does not assess readiness for you.
6. Mark done only after the linked PR is merged into the configured base, the task's acceptance criteria are met, the latest PR-head checks succeed, and the verification summary is recorded. Read the latest PR head and checks; stale cached CI, checks for another SHA, an empty check list, or a closed unmerged PR is insufficient. No checks is allowed only if `require_checks=false` was explicitly configured. Do not infer completion from a commit message or a PR existing.

   ```bash
   cu-work --project-dir /absolute/worktree phase --task 86native --phase done --pr 42 --verification-file /tmp/verification.md --key '86native:pr42:done:v1'
   ```

For host MCP completion, enforce the same evidence gate manually before calling the ClickUp status tool. Preserve the exact PR URL, head SHA, test results, and acceptance evidence in the task update. If any check is unavailable, report the gap and leave the task open.

This is an agent-driven workflow. It does not provision ClickUp's native GitHub integration, install webhooks, run a background sync daemon, merge PRs automatically, or deploy the project. Those actions require their own explicit task.
