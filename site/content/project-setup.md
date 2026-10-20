---
title: Bind your first project
description: Give the agent an objective and verified ClickUp scope in the repository it will work on.
section: Start here
---
# Start with a bounded project.

A binding tells the agent which work belongs together: one GitHub repository, one objective, one ClickUp Workspace and home List, and one or more root tasks. The agent verifies the task’s actual identity and ancestry before it writes.

## What you provide

| Input | Example / meaning |
| --- | --- |
| Working repository | The repository to implement, not the plugin’s install directory |
| Project objective | Deliver the approved poverty dashboard with verified data |
| ClickUp scope | Workspace, home List, and root task URLs or native IDs |
| GitHub repository and base | Your actual `owner/repository` and its default/approved base branch |
| Acceptance criteria | Observable conditions that make the task complete |

## Ask your agent to set it up

```prompt
Bind this working repository to ClickUp Skills.
Objective: deliver the approved poverty dashboard with verified data.
GitHub repository: <owner/repository>; base branch: <approved-base>.
ClickUp Workspace: <workspace>; home List: <list>; root task: <task-URL>.
Read any existing binding before changing anything. Resolve native task IDs,
verify the Workspace, home List and root scope, and inspect the repository
origin. Discover the List's exact statuses before mapping progress/review/done.
Create only the local binding; do not create remote tasks during setup.
```

Replace every placeholder. The agent should ask only for missing essentials and stop if scope or account access cannot be verified. A local configuration file is not proof of remote permission.

## What the agent records

The tracked `.clickup/project.json` holds objective, IDs, repository/base, routing policy, and the exact status mapping. The helper’s `init` creates it locally with no remote task writes and refuses to overwrite an existing binding. Review an existing binding before making any scope change.

Commit it only if its identifiers and objective are suitable for the repository’s audience. Keep credentials in each teammate’s private authentication or environment. Local focus and operation receipts live in Git worktree state, outside tracked project files.

[View the example binding](binding-reference.html) for the full schema and defaults. The example IDs are illustrative and must never be used as real scope.

## Enable skill discovery

Installation does not force every agent to load the workflow. Ask the agent to add this instruction to the working project’s existing `AGENTS.md`, `CLAUDE.md`, or the client’s supported instruction file, preserving other guidance:

```text
When this project has .clickup/project.json, load the ClickUp project/task
skills before task work. Verify the bound task and route CLI/MCP operations
before writing.
```

## Check that the setup is ready

Ask the agent to read the actual root task, verify its Workspace/List and ancestry, discover its status definitions, and summarize the repository, objective, active task and available tools. `doctor` alone does not verify remote task identity.

Multiple roots may share the same home List. Roots in different Lists require separate bindings/worktrees in this version. Moving a task across Lists stops further scoped writes until the binding is reviewed.

## Parallel work and ownership

Use separate Git worktrees for concurrent implementation and explicit task IDs for each agent. Agents in one worktree share focus and receipts. Receipts serialize local helper writes; they do not provide a cross-machine lock. Assign one owner to each task’s writes to avoid races.

Next: [use the plugin in everyday work](using-the-plugin.html).
