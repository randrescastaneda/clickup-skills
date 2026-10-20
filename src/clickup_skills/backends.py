"""Reuse the upstream CLI or its free REST MCP alternative, with no shell evaluation."""

from __future__ import annotations

import json
import os
import queue
import subprocess
import tempfile
import threading

from .context import WorkError


def execute(argv, cwd=None):
    try:
        result = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, encoding="utf-8", timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WorkError("Tool unavailable or timed out; verify remote state before retrying a write.") from exc
    if result.returncode:
        # Do not echo subprocess output: a third-party failure may contain credentials.
        raise WorkError(f"{argv[0]} failed (exit {result.returncode}). Inspect authentication and remote state; no automatic retry.")
    try:
        return json.loads(result.stdout) if result.stdout.strip() else {}
    except json.JSONDecodeError as exc:
        raise WorkError("Tool returned invalid JSON; a write may already have succeeded. Reconcile before retrying.") from exc


class StdioMCP:
    """Small newline JSON-RPC client for the pinned ClickUp REST MCP; one session per workflow."""
    def __init__(self):
        self.process = None
        self.serial = 0

    def open(self):
        if self.process:
            return
        try:
            # Installed explicitly by the teammate; no network/package install on a task write.
            self.process = subprocess.Popen(["clickup-rest-mcp"], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                            text=True, encoding="utf-8", bufsize=1)
        except OSError as exc:
            raise WorkError("Install clickup-rest-mcp==2026.10.15.1 or choose the cup runtime.") from exc
        self.messages = queue.Queue()
        def read():
            try:
                for line in self.process.stdout:
                    self.messages.put(line)
            finally:
                self.messages.put(None)
        threading.Thread(target=read, daemon=True).start()
        self.request("initialize", {"protocolVersion": "2024-11-05", "capabilities": {},
                                    "clientInfo": {"name": "clickup-skills", "version": "0.1.0"}})
        self.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.tools = {tool["name"] for tool in self.request("tools/list", {}).get("tools", [])}

    def send(self, message):
        try:
            self.process.stdin.write(json.dumps(message) + "\n")
            self.process.stdin.flush()
        except (OSError, BrokenPipeError) as exc:
            raise WorkError("MCP disconnected; reconcile any outstanding write.") from exc

    def request(self, method, params):
        self.serial += 1
        request_id = self.serial
        self.send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        while True:
            try:
                line = self.messages.get(timeout=60)
            except queue.Empty as exc:
                raise WorkError("MCP timed out; reconcile any outstanding write.") from exc
            if line is None:
                raise WorkError("MCP exited; reconcile any outstanding write.")
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as exc:
                raise WorkError("Invalid MCP stdout; reconcile any outstanding write.") from exc
            if msg.get("id") != request_id:
                continue
            if "error" in msg:
                raise WorkError("MCP rejected the request. No automatic replay.")
            return msg.get("result", {})

    def call(self, name, arguments):
        self.open()
        if name not in self.tools:
            raise WorkError("Installed REST MCP does not expose " + name)
        result = self.request("tools/call", {"name": name, "arguments": arguments})
        if result.get("isError"):
            raise WorkError("MCP tool reported an error. Verify remote state before another write.")
        if "structuredContent" in result:
            return result["structuredContent"]
        for item in result.get("content", []):
            if item.get("type") == "text":
                try:
                    return json.loads(item["text"])
                except json.JSONDecodeError:
                    pass
        raise WorkError("MCP returned no JSON data; reconcile before retrying a write.")

    def close(self):
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process.stdin.close()
            self.process.stdout.close()
            self.process = None


class ClickUp:
    def __init__(self, context):
        self.context = context
        self.runtime = context.config["routing"].get("runtime", "cup")
        self.mcp = StdioMCP()

    def close(self):
        self.mcp.close()

    def cup(self, args):
        prefix = ["cup", "--json"]
        profile = self.context.config["routing"].get("cup_profile")
        if profile:
            prefix += ["--profile", profile]
        # --team is not a global cup option. Scope is checked from the actual returned task.
        return execute(prefix + args, self.context.root)

    def get(self, task_id):
        if self.runtime == "rest-mcp":
            result = self.mcp.call("get_task", {"task_id": task_id, "include_subtasks": False})
        else:
            result = self.cup(["task", task_id])
        if not isinstance(result, dict):
            raise WorkError("Task backend did not return an object. Scope cannot be verified.")
        return result

    def comments(self, task_id):
        if self.runtime == "rest-mcp":
            data = self.mcp.call("list_comments", {"task_id": task_id})
            result = data.get("comments") if isinstance(data, dict) else data
        else:
            result = self.cup(["comments", task_id])
        if not isinstance(result, list) or not all(isinstance(c, dict) for c in result):
            raise WorkError("Invalid comment response; absence of a marker cannot be established.")
        if len(result) >= 25:
            raise WorkError("Comment history may be truncated at 25. Use a host MCP with complete pagination; do not infer a missing marker.")
        return result

    def children(self, task_id):
        if self.runtime == "rest-mcp":
            data = self.mcp.call("get_task", {"task_id": task_id, "include_subtasks": True})
            return data.get("subtasks", [])
        return self.cup(["subtasks", task_id, "--include-closed"])


    def write_text(self, command, text):
        # Files carry multiline text without exposing it to shell quoting or argv limits.
        fd, path = tempfile.mkstemp(prefix="cu-work-", suffix=".md")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(text)
            return self.cup(command + [path])
        finally:
            os.unlink(path)

    def subtask(self, parent, title, description):
        if self.runtime == "rest-mcp":
            return self.mcp.call("create_task", {"list_id": self.context.config["clickup"]["list_id"],
                                                 "parent": parent, "name": title, "description": description})
        return self.write_text(["create", "--parent", parent, "--list", self.context.config["clickup"]["list_id"], "--name", title,
                                "--description-file"], description)

    def comment(self, task_id, text):
        if self.runtime == "rest-mcp":
            return self.mcp.call("add_comment", {"task_id": task_id, "text": text, "notify_all": False})
        return self.write_text(["comment", task_id, "--message-file"], text)

    def status(self, task_id, status):
        if self.runtime == "rest-mcp":
            return self.mcp.call("update_task", {"task_id": task_id, "status": status})
        return self.cup(["update", task_id, "--status", status])
