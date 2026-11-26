"""Generate consistent client manifests and optional MCP profiles. Contains no credentials."""

import hashlib
import json
from pathlib import Path
import re
import sys

# SOURCE is read; ROOT is written. check.py points ROOT at a temporary folder.
SOURCE = ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.2.0"
# Files copied into installed skills so each skill is self-contained.
BUNDLED = {"skills/clickup-bind-project/assets/project.example.json": "examples/project.json",
           "skills/clickup-setup/references/manual-install.md": "INSTALL.md"}
CLICKUP_URL = "https://mcp.clickup.com/mcp"
# Per-client facts for INSTALL.md. Skill folders come from clients.py SKILL_PATHS and the
# snippets from render_config; check.py compares the settings paths with setup.py.
INSTALL_CLIENTS = (
    # client, label, skills key, user settings file, project settings file, native command
    ("kilo", "Kilo Code", "kilo", "~/.config/kilo/kilo.jsonc", ".kilo/kilo.jsonc", None),
    ("codex", "Codex", "codex", "~/.codex/config.toml", ".codex/config.toml",
     "codex mcp add clickup_official --url " + CLICKUP_URL + "\ncodex mcp login clickup_official"),
    ("claude", "Claude Code", "claude", "~/.claude.json", ".mcp.json",
     "claude mcp add --transport http clickup_official --scope user " + CLICKUP_URL),
    ("copilot", "Copilot CLI", "copilot", "~/.copilot/mcp-config.json", ".mcp.json", None),
    ("vscode", "VS Code Copilot Chat", "copilot", None, ".vscode/mcp.json", None),
)


def put(path, value):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes((json.dumps(value, indent=2) + "\n").encode("utf-8"))  # LF on every platform


def write(path, text, source=None):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(text.encode("utf-8") if text is not None else (SOURCE / source).read_bytes())


def client_section():
    sys.path.insert(0, str(SOURCE / "src"))
    from clickup_skills.clients import SKILL_PATHS, render_config
    profile = json.loads((SOURCE / "profiles/remote-only.json").read_text(encoding="utf-8"))
    lines = ["| Client | User skills folder | Project skills folder | User settings file | Project settings file |",
             "| --- | --- | --- | --- | --- |"]
    for client, label, skills, user, project, _ in INSTALL_CLIENTS:
        user_skills = "none" if client == "vscode" else "`~/" + SKILL_PATHS[skills][0] + "/`"
        lines.append(f"| {label} | {user_skills} | `{SKILL_PATHS[skills][1]}/` | "
                     + (f"`{user}`" if user else "none") + f" | `{project}` |")
    lines += ["", "Kilo respects `XDG_CONFIG_HOME` and Codex respects `CODEX_HOME`. Kilo uses an existing "
              "project-root `kilo.jsonc` instead of `.kilo/kilo.jsonc` when there is one."]
    for client, label, _, _, _, command in INSTALL_CLIENTS:
        language = "toml" if client == "codex" else "json"
        lines += ["", f"**{label}**", ""]
        if command:
            lines += ["Native command (from vendor documentation, untested here):", "", "```bash", command, "```", "",
                      "Or add this to the settings file:", ""]
        else:
            lines += ["Add this to the settings file:", ""]
        lines += ["```" + language, render_config(client, profile).rstrip("\n"), "```"]
    return "\n".join(lines) + "\n"


def render_install():
    text = (SOURCE / "INSTALL.md").read_text(encoding="utf-8")
    start, end = "<!-- clients:start -->\n", "<!-- clients:end -->"
    return re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: start + client_section() + end, text, flags=re.S)


def manifest():
    """SHA-256 of every file in each skill, for verifying manual copies."""
    skills = {}
    for folder in sorted(p for p in (SOURCE / "skills").iterdir() if (p / "SKILL.md").is_file()):
        files = sorted(f for f in folder.rglob("*") if f.is_file() and not f.name.startswith(".")
                       and "__pycache__" not in f.parts)
        skills[folder.name] = {f.relative_to(folder).as_posix(): hashlib.sha256(
            (ROOT / f.relative_to(SOURCE)).read_bytes() if (ROOT / f.relative_to(SOURCE)).is_file() else f.read_bytes()
        ).hexdigest() for f in files}
    license_hash = hashlib.sha256((SOURCE / "LICENSE").read_bytes()).hexdigest()
    return {"package": "clickup-skills", "version": VERSION,
            "note": "Each installed skill folder also receives LICENSE; installers may add their own receipt files.",
            "license": {"file": "LICENSE", "sha256": license_hash}, "skills": skills}


def main():
    identity = {"name": "clickup-skills", "version": VERSION,
                "description": "Project-bound ClickUp workflows with CLI/MCP routing and GitHub PR linkage.",
                "author": {"name": "Andres Castaneda"},
                "repository": "https://github.com/randrescastaneda/clickup-skills", "license": "MIT"}
    put("plugin.json", {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json", **identity})
    put(".claude-plugin/plugin.json", identity)
    put(".codex-plugin/plugin.json", {**identity, "skills": "./skills/", "mcpServers": "./.mcp.json"})
    put(".claude-plugin/marketplace.json", {
        "name": "clickup-skills-marketplace", "owner": {"name": "Andres Castaneda"},
        "plugins": [{"name": "clickup-skills", "source": "./", "version": VERSION,
                     "description": identity["description"]}]})
    basic = {"clickup_work": {"type": "stdio", "command": "cu-work", "args": ["mcp"]},
             "github": {"type": "http", "url": "https://api.githubcopilot.com/mcp/"}}
    remote = {"clickup_official": {"type": "http", "url": "https://mcp.clickup.com/mcp"}}
    put(".mcp.json", {"mcpServers": remote})
    portable = json.loads(json.dumps(remote))
    portable["clickup_official"]["type"] = "streamable-http"
    put("mcp.json", {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": portable})
    env = {"CLICKUP_API_KEY": "${CLICKUP_API_KEY}", "CLICKUP_TEAM_ID": "${CLICKUP_TEAM_ID}"}
    variants = {
        "default": {},
        "context": {"clickup_context": {"type": "stdio", "command": "npx",
                   "args": ["-y", "@hauptsache.net/clickup-mcp@1.9.0"],
                   "env": {**env, "CLICKUP_MCP_MODE": "read-minimal"}}},
        "rest": {"clickup_rest": {"type": "stdio", "command": "clickup-rest-mcp", "env": env}},
    }
    for name in ("official", "remote-only"):
        put("profiles/" + name + ".json", {"mcpServers": remote})
    put("profiles/local-helper.json", {"mcpServers": basic})
    for name, extra in variants.items():
        put("profiles/" + name + ".json", {"mcpServers": {**basic, **extra}})
    # INSTALL.md is regenerated in place (client section only), then bundled like the others.
    write("INSTALL.md", render_install())
    for path, source in BUNDLED.items():
        write(path, (ROOT / source).read_text(encoding="utf-8") if source == "INSTALL.md" else None, source)
    put("skills/MANIFEST.json", manifest())


if __name__ == "__main__":
    main()
