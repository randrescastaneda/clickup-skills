"""Minimal stdio MCP facade around the same scoped workflow implementation."""

import json
from pathlib import Path
import sys

from .context import Context, WorkError
from .routing import CAPABILITIES, route
from .workflow import Workflow


def tool(name, description, properties=None, required=None, write=False):
    props = {"project_dir": {"type": "string", "description": "Absolute path to the target Git worktree"}}
    props.update(properties or {})
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": props,
                            "required": ["project_dir"] + (required or []), "additionalProperties": False},
            "annotations": {"readOnlyHint": not write, "destructiveHint": False,
                            "idempotentHint": not write, "openWorldHint": True}}


STRING = {"type": "string"}
TASK = {"task_id": STRING}
WRITE = {**TASK, "key": STRING}
TOOLS = [
    tool("project_context", "Read the binding and active task; does not verify remote scope."),
    tool("route_operation", "Choose among backends actually available to the host; does not execute a tool.",
         {"operation": {"type": "string", "enum": list(CAPABILITIES)},
          "available": {"type": "array", "items": STRING}}, ["operation", "available"]),
    tool("get_bound_task", "Fetch and verify a task belongs to the bound workspace, list, and roots.", TASK),
    tool("create_bound_subtask", "Create a GitHub-associated subtask. Default creates/reuses an issue first. Requires gh.",
         {**WRITE, "title": STRING, "description": STRING, "github_target": STRING}, ["key", "title", "description"], True),
    tool("record_progress", "Post linked progress and mirror to associated issues/PRs with resumable receipts.",
         {**WRITE, "text": STRING}, ["key", "text"], True),
    tool("link_pull_request", "Preserve PR content and link both systems. Requires gh; no status changes.",
         {**WRITE, "pr_number": {"type": "integer", "minimum": 1}}, ["key", "pr_number"], True),
    tool("link_github_target", "Link a bound repo/issue/PR or create/reuse new-issue. Requires gh; preserves body text.",
         {**WRITE, "target": STRING, "title": STRING, "description": STRING}, ["key", "target"], True),
    tool("sync_task_comments", "Reconcile top-level ClickUp comments and GitHub issue/PR discussions; no background worker.",
         {**TASK, "direction": {"type": "string", "enum": ["both", "to-clickup", "to-github"]}}, [], True),
    tool("set_task_phase", "Set a mapped status. Done requires a merged PR, successful CI, and verification text.",
         {**WRITE, "phase": {"type": "string", "enum": ["in_progress", "review", "done"]},
          "pr_number": {"type": "integer", "minimum": 1}, "verification": STRING}, ["key", "phase"], True),
]


def call(name, args):
    definition = next((t for t in TOOLS if t["name"] == name), None)
    if not definition:
        raise WorkError("Unknown tool.")
    if not isinstance(args, dict):
        raise WorkError("Tool arguments must be an object.")
    schema = definition["inputSchema"]
    if any(k not in args for k in schema["required"]) or set(args) - set(schema["properties"]):
        raise WorkError("Invalid tool arguments.")
    for key, value in args.items():
        if "enum" in schema["properties"][key] and value not in schema["properties"][key]["enum"]:
            raise WorkError("Unsupported value for " + key)
        expected = schema["properties"][key]["type"]
        if expected == "string" and not isinstance(value, str):
            raise WorkError("Expected a string for " + key)
        if expected == "integer" and (type(value) is not int or value < 1):
            raise WorkError("Expected a positive integer for " + key)
        if expected == "array" and (not isinstance(value, list) or not all(isinstance(v, str) for v in value)):
            raise WorkError("Expected an array of strings for " + key)
    if not Path(args["project_dir"]).is_absolute():
        raise WorkError("project_dir must be absolute; do not infer it from the plugin directory.")
    ctx = Context(args["project_dir"])
    if name == "project_context":
        return {"project": ctx.config, "active_task_id": ctx.task_id()}
    if name == "route_operation":
        return route(args["operation"], args["available"], ctx.config)
    work = Workflow(ctx)
    try:
        task = args.get("task_id")
        if name == "get_bound_task":
            return work.task(task)
        with ctx.locked():
            if name == "create_bound_subtask":
                return work.subtask(args["title"], args["description"], args["key"], task, args.get("github_target"))
            if name == "record_progress":
                return work.progress(args["text"], args["key"], task)
            if name == "link_pull_request":
                return work.link_pr(args["pr_number"], args["key"], task)
            if name == "link_github_target":
                return work.link_github(args["target"], args["key"], task, args.get("title"), args.get("description", ""))
            if name == "sync_task_comments":
                return work.sync_comments(task, args.get("direction", "both"))
            if name == "set_task_phase":
                return work.phase(args["phase"], args["key"], task, args.get("pr_number"), args.get("verification"))
        raise WorkError("Unsupported tool.")
    finally:
        work.close()


def response(message):
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "Invalid request"}}
    request_id = message.get("id")
    method = message.get("method")
    if request_id is None:
        return None
    if method == "initialize":
        result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "clickup-skills", "version": "0.1.0"}}
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        try:
            params = message.get("params", {})
            if not isinstance(params, dict):
                raise WorkError("Tool parameters must be an object.")
            data = call(params.get("name"), params.get("arguments", {}))
            result = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}
        except (WorkError, OSError, ValueError, KeyError, TypeError) as exc:
            result = {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
    else:
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def serve():
    for line in sys.stdin:
        try:
            result = response(json.loads(line))
        except json.JSONDecodeError:
            result = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
        if result is not None:
            print(json.dumps(result, ensure_ascii=False), flush=True)
