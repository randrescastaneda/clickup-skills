---
name: clickup-route
description: Choose an efficient available CLI or free MCP for a ClickUp/GitHub operation. Use whenever a bound project needs ClickUp tools, a backend lacks a capability, a rate limit occurs, or a choice among cup, community MCP, official ClickUp MCP, gh, and GitHub MCP is needed.
license: MIT
compatibility: Requires the official ClickUp MCP authorized in the agent, or the optional cu-work local helper; GitHub through gh or an approved hosted connection.
---

# Route each operation

<!-- selection-check:start -->
## First: which backends were selected?

The user selects the ClickUp mode and the GitHub backend at setup, independently of each other. Do not infer the selection from the tools that happen to be listed.

1. If the user, the project instructions or the setup report state the selection, use it.
2. If nothing states it, assume the default, **hosted** ClickUp (official OAuth MCP, `https://mcp.clickup.com/mcp`) with **`gh`** for GitHub, and confirm it with the user before the first write.
3. The **hosted** GitHub backend (an approved hosted GitHub connection instead of `gh`) applies only when the user selected it.
4. **remote-only** permits hosted connections only: never `gh`, never a local ClickUp tool.
5. **local-helper** applies only when the user selected it and `get_bound_task` succeeds for a bound root task. A `clickup_work` server that merely starts is not enough. The local-helper steps in this skill apply only in this mode.

A selected backend that is missing, banned or unauthenticated means STOP and report; never switch backends on your own. One `gh` sign-in serves all authorized repositories: verify each project's exact repository and create no per-repository token. Never use `cup`, `cu-work` or a bridge for hosted ClickUp. Before any hosted write, follow the guarded protocol in the sibling skill `clickup-github`, file `references/official-mcp-issue-first.md`. Those are agent checks, outside helper receipts, locks and completion gates.
<!-- selection-check:end -->

## Hosted ClickUp (default and remote-only)

1. Read the binding and inventory only the tools actually present in this session.
2. Use the connected official ClickUp MCP for ClickUp operations.
3. Use the selected GitHub backend for GitHub operations: `gh`, or the approved hosted GitHub tools. In remote-only mode, hosted tools only.
4. Never choose `cup`, `rest-mcp` or an unbound `clickup_work` merely because it appears in the client's tool list. Those are separate authentication and receipt domains.
5. Before any hosted write, load the guarded protocol in the sibling skill `clickup-github`, file [`references/official-mcp-issue-first.md`](../clickup-github/references/official-mcp-issue-first.md).
6. Before each direct host call, recheck the Workspace, List and ancestry. Preserve operation markers and receipts yourself: the helper's journal does not capture host calls.
7. Use paginated host MCP reads for complete comment histories and threaded replies.
8. If a hosted write fails, do not fall back to the CLI.

## Local-helper mode

Prefer the `clickup_work` MCP tools; each `cu-work …` line is the shell equivalent. If `cu-work` is not on PATH, use the managed launcher `CLICKUP_SKILLS_HOME/bin/cu-work` (`cu-work.cmd` on Windows; default folder `~/.local/share/clickup-skills/bin`) when it exists, otherwise the MCP tools only. Do not use an `npx` proxy as the normal way to run the helper.

The routing table below applies to a local-helper installation with a working `cup` token. The backends are `cup`, `rest-mcp` (Joel Thornton), `context-mcp` (hauptsacheNet), `official` (ClickUp), `github-cli` and `github-mcp`.

| Need | First candidate | Reason |
| --- | --- | --- |
| Exact task, subtask, status, comment, custom field, dependency | `cup` | Small JSON commands and file-based text input |
| Task plus comments/images/context | `context-mcp` | May consolidate several reads; discover the exposed mode |
| Broad REST API operation without cup | `rest-mcp` | Free local MCP with individual operation tools |
| Broad workspace search / official-specific functionality | `official` | Official search and service coverage; inspect limits |
| Branch, PR, checks, issue | `gh` or GitHub MCP | Use the available tool with complete fields and least extra work |

1. Ask for a route with `route_operation` (absolute `project_dir`, operation, available backend names) or the shell equivalent:

   ```bash
   cu-work --project-dir /absolute/worktree route task.context --available cup,context-mcp,official
   ```

2. Treat the route as advice. It neither executes nor probes availability, per-project overrides can reorder it, and its defaults are not latency or token benchmarks. In a hosted session `route_operation` may lack a project binding.
3. `cu-work` and its MCP execute scoped writes directly through `cup` or the configured `rest-mcp` runtime. Host `context-mcp`, official ClickUp MCP and GitHub MCP are called by the agent, not proxied by the helper.
4. For `cup tasks` or `cup search`, use `--all` for team-wide work and scope to the bound List.
5. The pinned `cup comments` and REST MCP `list_comments` return one page, so the helper stops at 25 comments. For longer local histories, explicitly select `routing.comment_reader=clickup-api` with private environment credentials for GET-only cursor reads. Writes stay on the selected upstream runtime, with no automatic fallback.
6. Use `cu-work reconcile` only for local-helper receipts, and only after establishing what applied.

## Rules for every selection

- For any MCP, inspect the selected tool's current input schema and returned fields. Tool names in a route are hints, not guarantees.
- A read-minimal context MCP cannot write just because its full version has create tools.
- Do not register every server to perform one task.
- Prefer native IDs, filtered and paginated reads, and compact responses. Retrieve comments and images only when needed.
- A limited search that returns no match does not prove absence.
- Use a complete-read backend for reconciliation.
- Link GitHub before any subtask creation, whatever the backend. Routing a create call directly does not exempt it from `clickup-github`'s association rules.
- If the selected backend is unavailable, stop and report it.
- The user may explicitly choose another allowed backend before a new operation, after its authentication and scope are verified. That is not automatic fallback.
- After a timeout, malformed response, rate-limit error during a write, or other uncertain outcome, inspect remote state first. Never replay the write through another backend.
- Stop when authorization, scope or required evidence cannot be established.
- Keep tokens in each teammate's own account.
- Free MCP software still uses services with API and plan limits.
- Do not install paid or proprietary servers, and do not claim one backend is faster without evidence.

## Report

State the operation, the backend chosen and why, and any backend that was unavailable or stopped the operation.
