"""Client-specific packaging around the same workflow skills and MCP servers."""

import copy
import json
from pathlib import Path
import re

from .context import WorkError


SKILL_PATHS = {
    "codex": (".agents/skills", ".agents/skills"),
    "claude": (".claude/skills", ".claude/skills"),
    "copilot": (".copilot/skills", ".github/skills"),
    "kilo": (".kilo/skills", ".kilo/skills"),
    "opencode": (".config/opencode/skills", ".agents/skills"),
}
CONFIG_CLIENTS = ("claude", "codex", "vscode", "copilot", "kilo", "posit", "portable")


def skill_directory(client, *, home=None, project_dir=None):
    if client not in SKILL_PATHS:
        raise WorkError("Unknown skills client: " + client)
    user, project = SKILL_PATHS[client]
    return Path(project_dir).resolve() / project if project_dir is not None else Path(home or Path.home()) / user


def _references(env, style):
    def convert(value):
        match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", value)
        if not match:
            return value
        if style == "vscode":
            return "${env:" + match.group(1) + "}"
        return "{env:" + match.group(1) + "}"
    return {key: convert(value) for key, value in env.items()}


def render_config(client, config):
    """Return text only. Never inspect secret values or modify client settings."""
    if client not in CONFIG_CLIENTS:
        raise WorkError("Unknown configuration client: " + client)
    servers = copy.deepcopy(config["mcpServers"])
    if client == "codex":
        lines = []
        for name, server in servers.items():
            lines.append("[mcp_servers." + name + "]")
            for key in ("command", "args", "url"):
                if key in server:
                    lines.append(key + " = " + json.dumps(server[key]))
            env = server.get("env", {})
            names = [key for key, value in env.items() if re.fullmatch(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", value)]
            fixed = {key: value for key, value in env.items() if key not in names}
            if names:
                lines.append("env_vars = " + json.dumps(names))
            if fixed:
                lines.append("env = { " + ", ".join(json.dumps(k) + " = " + json.dumps(v) for k, v in fixed.items()) + " }")
            lines.append("")
        return "\n".join(lines) + "\n"
    key = "servers" if client == "vscode" else "mcp" if client == "kilo" else "mcpServers"
    for server in servers.values():
        local = server.get("type") == "stdio"
        if client == "portable":
            server["type"] = "stdio" if local else "streamable-http"
        elif client == "vscode":
            key = "servers"
            if "env" in server:
                server["env"] = _references(server["env"], "vscode")
        elif client == "copilot":
            server["type"] = "local" if local else "http"
            server["tools"] = ["*"]
        elif client in ("kilo", "posit"):
            key = "mcp" if client == "kilo" else "mcpServers"
            server["type"] = "local" if local else "remote"
            if local:
                server["command"] = [server["command"], *server.pop("args", [])]
            if "env" in server:
                server["environment"] = _references(server.pop("env"), client)
            if not local and client == "posit":
                server["auth"] = "oauth"
    result = {key: servers}
    if client == "portable":
        result["$schema"] = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    return json.dumps(result, indent=2) + "\n"
