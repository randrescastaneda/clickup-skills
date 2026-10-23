---
title: Talk to your agent
description: Delegate in plain language while your agent handles task scope, tools, progress, and evidence.
section: Work with your agent
---
# Say what you need. Keep the objective visible.

You do not need to remember `cu-work` commands, MCP tool names, or synchronization markers. Describe the outcome, identify the task when needed, and tell the agent what evidence you expect. The agent selects tools and follows the workflow skills.

## Which installation mode?

- **Default browser OAuth:** Your agent uses the official ClickUp MCP and
  authenticated `gh` (or an independently configured working GitHub MCP) directly. It loads the
  [guarded issue-first workflow](clickup-github.html) before any mutation.
  The agent re-reads scope, searches complete history for duplicates, verifies
  a GitHub target before creating a subtask, and stops on uncertain writes.
  These checks are agent-enforced; there is no local `clickup_work` journal.
- **Optional full local helper:** If you deliberately installed
  `onboard --mode cli`, authenticated Krodak's `cup`, and bound this project,
  your agent may use `clickup_work` for helper-enforced scope and durable
  receipts. The two authentication methods are separate.

## A good first request

```prompt
Use this project's ClickUp binding. Work on <task-URL> toward the recorded
objective. Read the task, existing subtasks and linked GitHub discussion first.
Create subtasks only when they are useful, associate a GitHub target before
each one, and keep meaningful progress current. Link the implementation PR.
Put ready work in review. Mark done only after acceptance, merge and the latest
PR-head checks are verified, with evidence recorded.
```

Task URLs in these examples are placeholders. Use a real task inside the bound scope.

## The everyday loop

| Stage | You ask | The agent does |
| --- | --- | --- |
| Resume | “Where are we on this task?” | Reads binding, task, branch/PR and current discussions; checks local receipts **only in full-helper mode** |
| Plan | “Break this into useful deliverables.” | Reuses existing children; resolves a GitHub target before every new child |
| Implement | “Build the agreed change and verify it.” | Works on the branch, runs appropriate checks, records meaningful progress |
| Review | “Prepare this for review.” | Links the PR both ways, preserves its body and sets the mapped review status |
| Complete | “Check whether this is ready to close.” | Verifies acceptance, merged non-draft PR, correct base and latest-head CI |
| Hand off | “Prepare the next agent to continue.” | Gives task/PR links, head SHA, evidence, blockers, pending writes and next action |

Review and done are separate states. The plugin does not merge PRs or deploy software on your behalf. Those operations require the agent’s other tools and your authorized task scope.

## Progress that helps the team

Ask for milestone updates instead of a stream of small actions. A useful update says what changed, which evidence supports it, what is blocked, and what happens next. In the **full helper mode**, the helper includes ClickUp/GitHub links and mirrors progress to associated issue/PR discussions. In **OAuth mode**, the agent must follow the guarded workflow and explicitly perform approved mirroring; installing MCP does not start automatic synchronization.

## When the agent should stop

- The task is outside the bound Workspace, List or task tree.
- A write times out and the actual result is uncertain.
- The agent cannot fully read the history needed for safe reconciliation.
- The PR is unmerged, draft, targets the wrong base, or has failed/pending/missing required checks.
- Acceptance evidence is absent, even if a PR has merged.

A stop should identify the missing evidence or setup. It should preserve successful writes and avoid retrying the same uncertain mutation through another backend.

## What to expect at handoff

Ask for a short report with the task URL, objective, branch/PR and latest head, completed work, checks actually run, blockers, pending operations, and the next action. A tool can record the agent’s verification summary; it cannot determine whether that summary is truthful.

Browse [copyable examples](examples.html) for research, dashboards, bugs, review, recovery and team handoff.
