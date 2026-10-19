---
name: clickup-route
description: Choose an efficient available CLI or free MCP for a ClickUp/GitHub operation. Use whenever a bound project needs ClickUp tools, a backend lacks a capability, a rate limit occurs, or a choice among cup, community MCP, official ClickUp MCP, gh, and GitHub MCP is needed.
---

# Route each operation

Read the binding and inventory only tools actually present in this session. The backends are `cup`, `rest-mcp` (Joel Thornton), `context-mcp` (hauptsacheNet), `official` (ClickUp), `github-cli`, and `github-mcp`.

| Need | First candidate | Reason |
| --- | --- | --- |
| Exact task, subtask, status, comment, custom field, dependency | `cup` | Small JSON commands and file-based text input |
| Task plus comments/images/context | `context-mcp` | May consolidate several reads; discover the exposed mode |
| Broad REST API operation without cup | `rest-mcp` | Free local MCP with individual operation tools |
| Broad workspace search / official-specific functionality | `official` | Official search and service coverage; inspect limits |
| Branch, PR, checks, issue | `gh` or GitHub MCP | Use the available tool with complete fields and least extra work |

Run, for example:

```bash
cu-work --project-dir /absolute/worktree route task.context --available cup,context-mcp,official
```

Or call `route_operation` with the absolute `project_dir`, operation, and available backend names. A route is advice, not execution or an availability probe. Per-project overrides can reorder it. These defaults are not measured latency/token benchmarks.

For MCP, inspect the selected tool's current input schema and returned fields. Names in the route output are hints, not guarantees. A read-minimal context MCP cannot write just because its full version has create tools. Do not register all servers to perform one task. Prefer native IDs, filtered/paginated reads, and compact responses; retrieve comments/images only when needed. A limited search returning no match does not prove absence. For `cup tasks` or `cup search`, use `--all` for team-wide work and scope to the bound list.

The `cu-work` executable and its own MCP can directly execute scoped writes through `cup` or the configured `rest-mcp` runtime. Host `context-mcp`, official ClickUp MCP, and GitHub MCP are invoked by the agent, not proxied by this helper. When using host tools directly, perform fresh workspace/list/ancestry checks and preserve operation markers/receipts yourself. The helper's journal does not capture host calls.

Switch an unavailable backend before dispatch or after a definite capability rejection. After a timeout, malformed response, rate-limit error during a write, or other uncertain outcome, inspect remote state first. Never replay a mutation through another backend. Use `cu-work reconcile` only after establishing whether it applied. Stop if authorization, scope, or required evidence cannot be established.

Keep tokens in each teammate's account. Free MCP software still uses services with API/plan limits. Do not install paid/proprietary servers or claim one backend is faster without evidence.
