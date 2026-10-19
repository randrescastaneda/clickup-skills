---
name: clickup-handoff
description: Resume a bound ClickUp project, review operation receipts, reconcile uncertain updates, and prepare a concise task handoff. Use at session start/end, after a failed update, or when handing work to a teammate or another coding agent.
---

# Resume or hand off work

Read `.clickup/project.json` and, when available, `cu-work context` in the target worktree. With host MCPs only, read the binding and preserve separate host operation evidence; do not assume a helper journal exists. Confirm the project, objective, active task, branch, and repository before resuming. Explicit `--task` is safer than changing shared focus when agents work in parallel.

Read the actual task and relevant comments plus current GitHub issue/PR/check state. Verify its remote GitHub association markers. Run `sync-comments --task ID` / `sync_task_comments` for issue/PR discussions when authorized, observing the pagination/echo rules in `clickup-github`. Local focus and receipts are not authoritative remote state. Inspect pending operations in the reported `local_state` file. Do not print task bodies, credentials, or the entire state file into unrelated logs.

If an operation is pending, inspect its remote marker/ID and relevant task or PR. Repeat the same helper call with identical arguments to allow marker-based reconciliation. If the remote state cannot prove the outcome, stop that write. After a complete inspection establishes the result, an operator may run:

```bash
cu-work --project-dir /absolute/worktree reconcile --key 'operation-key' --result-file /tmp/verified-result.json
# Only after establishing the original write did NOT apply:
cu-work --project-dir /absolute/worktree reconcile --key 'operation-key' --not-applied
```

Reconciliation records an inspection decision; it does not itself inspect ClickUp. Never use `--not-applied` just to clear an inconvenient error, and never change backends to replay an uncertain write. For a partially linked PR, inspect and recover the `:github` and `:clickup` receipts independently. For host-only calls, reconcile the preserved host evidence and remote markers directly; `cu-work reconcile` cannot clear or verify a host call it never recorded.

Produce a short handoff with task URL, objective, current branch/PR and head SHA, completed work, checks actually run, blockers, pending operations, and next action. Save it as a task comment only when the user's work authorizes that update; otherwise return it in chat. Use `record_progress` or `cu-work progress --message-file ... --key ...` for an authorized update. Leave review/complete statuses unchanged unless the completion workflow establishes their evidence.

Never claim a test, sync, deployment, or merge occurred without evidence. End with the next action and any specific input needed from the user; say nothing is needed when that is the case.
