"""Print (never overwrite) MCP configuration for a chosen client and profile."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--client", choices=["claude", "codex", "portable"], required=True)
p.add_argument("--profile", choices=["default", "official", "context", "rest"], default="default")
a = p.parse_args()
config = json.loads((ROOT / "profiles" / (a.profile + ".json")).read_text())
if a.client == "codex":
    for name, server in config["mcpServers"].items():
        print("[mcp_servers." + name + "]")
        for key in ("command", "args", "url"):
            if key in server:
                print(key + " = " + json.dumps(server[key]))
        if "env" in server:
            # Forward secret variable names, never interpolate values into a file.
            names = [k for k, v in server["env"].items() if v.startswith("${")]
            fixed = {k: v for k, v in server["env"].items() if not v.startswith("${")}
            if names:
                print("env_vars = " + json.dumps(names))
            if fixed:
                print("env = { " + ", ".join(json.dumps(k) + " = " + json.dumps(v) for k, v in fixed.items()) + " }")
        print()
else:
    if a.client == "portable":
        config["$schema"] = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
        for server in config["mcpServers"].values():
            if server["type"] == "http":
                server["type"] = "streamable-http"
    print(json.dumps(config, indent=2))
