"""Generate consistent client manifests and optional MCP profiles. Contains no credentials."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def put(path, value):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    identity = {"name": "clickup-skills", "version": "0.1.0",
                "description": "Project-bound ClickUp workflows with CLI/MCP routing and GitHub PR linkage.",
                "author": {"name": "Andres Castaneda"},
                "repository": "https://github.com/randrescastaneda/clickup-skills", "license": "MIT"}
    put("plugin.json", {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **identity})
    put(".claude-plugin/plugin.json", identity)
    put(".codex-plugin/plugin.json", {**identity, "skills": "./skills/", "mcpServers": "./.mcp.json"})
    put(".claude-plugin/marketplace.json", {
        "name": "clickup-skills-marketplace", "owner": {"name": "Andres Castaneda"},
        "plugins": [{"name": "clickup-skills", "source": "./", "version": "0.1.0",
                     "description": identity["description"]}]})
    basic = {"clickup_work": {"type": "stdio", "command": "cu-work", "args": ["mcp"]},
             "github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/"}}
    put(".mcp.json", {"mcpServers": basic})
    portable = json.loads(json.dumps(basic))
    portable["github"]["type"] = "streamable-http"
    put("mcp.json", {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": portable})
    env = {"CLICKUP_API_KEY": "${CLICKUP_API_KEY}", "CLICKUP_TEAM_ID": "${CLICKUP_TEAM_ID}"}
    variants = {
        "default": {},
        "official": {"clickup_official": {"type": "http", "url": "https://mcp.clickup.com/mcp"}},
        "context": {"clickup_context": {"type": "stdio", "command": "npx",
                   "args": ["-y", "@hauptsache.net/clickup-mcp@1.9.0"],
                   "env": {**env, "CLICKUP_MCP_MODE": "read-minimal"}}},
        "rest": {"clickup_rest": {"type": "stdio", "command": "clickup-rest-mcp", "env": env}},
    }
    for name, extra in variants.items():
        put("profiles/" + name + ".json", {"mcpServers": {**basic, **extra}})


if __name__ == "__main__":
    main()
