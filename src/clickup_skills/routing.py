"""Capability-first routing; priorities are policy defaults, not benchmark claims."""

from .context import WorkError

# Host MCP names are hints. Inspect tools/list and inputSchema before calling them.
CAPABILITIES = {
    "task.get": {"cup": "cup task", "rest-mcp": "get_task", "context-mcp": "getTaskById", "official": "clickup_get_task"},
    "task.context": {"context-mcp": "getTaskById", "cup": "cup activity", "rest-mcp": "get_task + list_comments", "official": "clickup_get_task + clickup_get_task_comments"},
    "task.subtask": {"cup": "cup create --parent", "rest-mcp": "create_task", "context-mcp": "createTask", "official": "clickup_create_task"},
    "task.comment": {"cup": "cup comment --message-file", "rest-mcp": "add_comment", "context-mcp": "addComment", "official": "clickup_create_task_comment"},
    "task.status": {"cup": "cup update --status", "rest-mcp": "update_task", "context-mcp": "updateTask", "official": "clickup_update_task"},
    "task.search": {"cup": "cup tasks --all --list", "rest-mcp": "search_tasks", "context-mcp": "searchTasks", "official": "clickup_search"},
    "task.custom-field": {"cup": "cup field", "rest-mcp": "set_custom_field_value"},
    "task.dependency": {"cup": "cup depend", "rest-mcp": "add_dependency"},
    "docs.search": {"official": "clickup_search", "cup": "cup docs", "context-mcp": "searchDocuments"},
    "chat.send": {"official": "discover chat send tool", "cup": "cup chat send"},
    "github.pr": {"github-cli": "gh pr view/create/edit", "github-mcp": "discover pull request tools"},
    "github.checks": {"github-cli": "gh pr view --json statusCheckRollup", "github-mcp": "discover pull request/status/check tools"},
}


def route(operation, available, config=None):
    if operation not in CAPABILITIES:
        raise WorkError("Unknown operation: " + operation)
    cfg = (config or {}).get("routing", {})
    overrides = cfg.get("overrides", {})
    default = ["context-mcp", "cup", "rest-mcp", "official"] if operation == "task.context" else ["cup", "rest-mcp", "context-mcp", "official", "github-cli", "github-mcp"]
    if operation == "docs.search":
        default = ["official", "cup", "context-mcp"]
    preferred = overrides.get(operation, []) or cfg.get("prefer", []) or default
    if not isinstance(preferred, list):
        raise WorkError("Routing overrides must be ordered lists.")
    order = list(dict.fromkeys(preferred + default))
    choices = [name for name in order if name in available and name in CAPABILITIES[operation]]
    if not choices:
        raise WorkError("No available backend supports " + operation + ". Configure a profile or install cup/gh.")
    return {"operation": operation, "backend": choices[0], "tool_hint": CAPABILITIES[operation][choices[0]],
            "alternatives": choices[1:], "schema_discovery_required": choices[0] not in ("cup", "github-cli"),
            "reason": "First available capable backend under project policy; no measured speed claim.",
            "on_uncertain_write": "Read remote state and reconcile; do not fail over or replay."}
