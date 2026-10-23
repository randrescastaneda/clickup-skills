"""Explicit, per-user setup. Uses only Python's standard library; never handles tokens."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import uuid
import venv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from clickup_skills.clients import render_config, skill_directory
from install_skills import install

CLIENTS = ("kilo", "codex", "claude", "copilot", "vscode")
SOURCE_ITEMS = ("src", "scripts/run_work.py", "skills", "profiles", "LICENSE", "THIRD_PARTY_NOTICES.md", "third_party")
START, END = "# BEGIN clickup-skills managed MCP", "# END clickup-skills managed MCP"
NPX = "npx --yes github:randrescastaneda/clickup-skills"


def read_json(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def save_json(path, data):
    atomic_write(path, json.dumps(data, indent=2) + "\n")


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".clickup-skills-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def jsonc_text(text):
    """Mask comments and trailing commas, retaining every source offset."""
    pattern = r'"(?:[^"\\]|\\.)*"|//[^\r\n]*|/\*[\s\S]*?\*/'
    masked = re.sub(pattern, lambda m: m[0] if m[0].startswith('"') else re.sub(r'[^\r\n]', ' ', m[0]), text)
    # Only comma tokens outside strings count. Offsets stay the same.
    return re.sub(r'"(?:[^"\\]|\\.)*"|,(?=\s*[}\]])',
                  lambda m: " " if m[0] == "," else m[0], masked)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate configuration key; resolve it before setup: " + key)
        result[key] = value
    return result


def object_fields(text, start=0):
    clean = jsonc_text(text)
    decoder = json.JSONDecoder()
    pos = start + len(clean[start:]) - len(clean[start:].lstrip())
    if clean[pos:pos + 1] != "{":
        raise ValueError("Expected a configuration object.")
    pos += 1
    fields = {}
    while True:
        while clean[pos].isspace() or clean[pos] == ",":
            pos += 1
        if clean[pos] == "}":
            return fields, pos
        key, pos = decoder.raw_decode(clean, pos)
        while clean[pos].isspace():
            pos += 1
        if clean[pos] != ":":
            raise ValueError("Invalid configuration property.")
        pos += 1
        while clean[pos].isspace():
            pos += 1
        value_start = pos
        _, pos = decoder.raw_decode(clean, pos)
        fields[key] = (value_start, pos)


def edit_object(text, start, changes):
    fields, closing = object_fields(text, start)
    replacements, additions = [], {}
    for name, value in changes.items():
        if name in fields:
            begin, end = fields[name]
            replacements.append((begin, end, json.dumps(value, indent=2)))
        else:
            additions[name] = value
    if additions:
        # Add the separator after any preceding comment, and preserve trailing commas.
        before = text[start:closing]
        without_comments = re.sub(r'"(?:[^"\\]|\\.)*"|//[^\r\n]*|/\*[\s\S]*?\*/',
                                  lambda m: m[0] if m[0].startswith('"') else " ", before).rstrip()
        separator = "," if fields and not without_comments.endswith(",") else ""
        body = json.dumps(additions, indent=2)[1:-1].strip("\n")
        replacements.append((closing, closing, separator + "\n" + body + "\n"))
    for begin, end, value in sorted(replacements, reverse=True):
        text = text[:begin] + value + text[end:]
    return text


def config_destination(client, project=None):
    home = Path.home()
    if project:
        paths = {"kilo": ".kilo/kilo.jsonc", "codex": ".codex/config.toml", "claude": ".mcp.json",
                 "copilot": ".mcp.json", "vscode": ".vscode/mcp.json"}
        if client == "kilo" and (project / "kilo.jsonc").exists():
            return project / "kilo.jsonc"
        return project / paths[client]
    paths = {"kilo": Path(os.environ.get("XDG_CONFIG_HOME", home / ".config")) / "kilo/kilo.jsonc",
             "codex": Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml",
             "claude": home / ".claude.json", "copilot": home / ".copilot/mcp-config.json"}
    if client not in paths:
        raise ValueError("VS Code setup needs --project-dir /absolute/path/to/project.")
    return paths[client]


def desired_config(client, profile, runtime):
    config = read_json(ROOT / "profiles" / (profile + ".json"))
    config["mcpServers"]["clickup_work"].update(command=str(runtime / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")),
                                              args=["-I", str(runtime / "scripts/run_work.py"), "mcp"])
    text = render_config(client, config)
    return tomllib.loads(text) if client == "codex" else json.loads(text)


def desired_host_config(client):
    """Agent-hosted OAuth MCP only. Do not install or authenticate cup in this mode."""
    config = read_json(ROOT / "profiles/official.json")
    config["mcpServers"].pop("clickup_work")
    text = render_config(client, config)
    return tomllib.loads(text) if client == "codex" else json.loads(text)


def merge_config(text, client, desired, previous):
    key = {"kilo": "mcp", "codex": "mcp_servers", "vscode": "servers"}.get(client, "mcpServers")
    data = tomllib.loads(text) if client == "codex" else json.loads(jsonc_text(text), object_pairs_hook=unique_object)
    if not isinstance(data, dict) or not isinstance(data.get(key, {}), dict):
        raise ValueError("MCP settings must be an object; existing settings were preserved.")
    current = data.get(key, {})
    owned, changes = dict(previous), {}
    for name, server in desired[key].items():
        if name in current:
            if current[name] == server:
                continue
            if name in previous and current[name] == previous[name]:
                changes[name] = server
            elif name == "clickup_work" and name not in previous:
                legacy = {"mcpServers": {name: {"type": "stdio", "command": "cu-work", "args": ["mcp"]}}}
                baseline = render_config(client, legacy)
                baseline = tomllib.loads(baseline) if client == "codex" else json.loads(baseline)
                if current[name] != baseline[key][name]:
                    raise ValueError("Refusing to replace an existing or locally modified MCP server: " + name)
                changes[name] = server
            elif name != "clickup_work" and name not in previous:
                continue  # Reuse the teammate's existing GitHub/optional server.
            else:
                raise ValueError("Refusing to replace an existing or locally modified MCP server: " + name)
        else:
            if name != "clickup_work" and any(s.get("url") == server.get("url") for s in current.values()
                                                 if isinstance(s, dict) and server.get("url")):
                continue
            changes[name] = server
        owned[name] = server
    if not changes:
        return text, owned
    if client == "codex":
        if "clickup_work" in current and "clickup_work" not in previous and "clickup_work" in changes:
            legacy = render_config("codex", {"mcpServers": {"clickup_work": {"type": "stdio", "command": "cu-work", "args": ["mcp"]}}})
            if text.count(legacy) != 1:
                raise ValueError("Move the old clickup_work TOML entry aside, then rerun setup. Settings were preserved.")
            text = text.replace(legacy, "", 1)
        # Only the dedicated generated block is rewritten; all other TOML is untouched.
        if START in text or END in text:
            if text.count(START) != 1 or text.count(END) != 1:
                raise ValueError("Ambiguous managed TOML block; settings preserved.")
            begin, end = text.index(START), text.index(END) + len(END)
            block = tomllib.loads(text[begin:end]).get(key, {})
            if block != previous:
                raise ValueError("Managed TOML block was locally modified; settings preserved.")
        else:
            if previous:
                raise ValueError("Managed TOML block is missing; settings preserved.")
            begin = end = len(text)
        canonical = {"mcpServers": owned}
        block = START + "\n" + render_config("codex", canonical) + END
        result = text[:begin] + ("\n" if begin and text[begin - 1] != "\n" else "") + block + "\n" + text[end:]
        tomllib.loads(result)
        return result, owned
    fields, _ = object_fields(text)
    result = edit_object(text, fields[key][0], changes) if key in fields else edit_object(text, 0, {key: changes})
    json.loads(jsonc_text(result), object_pairs_hook=unique_object)
    return result, owned


def source_digest(node):
    digest = hashlib.sha256((str(Path(sys.executable).resolve()) + node).encode())
    for item in (*SOURCE_ITEMS, "package.json"):
        path = ROOT / item
        for file in sorted(path.rglob("*")) if path.is_dir() else [path]:
            if file.is_file() and "__pycache__" not in file.parts and file.suffix not in (".pyc", ".pyo"):
                digest.update(file.relative_to(ROOT).as_posix().encode() + b"\0" + file.read_bytes())
    return digest.hexdigest()


def runtime_python(runtime):
    return runtime / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def build_runtime(home, node, npm, digest):
    releases = home / "releases"
    releases.mkdir(parents=True, exist_ok=True)
    runtime = Path(tempfile.mkdtemp(prefix=digest[:12] + "-", dir=releases))
    try:
        for item in SOURCE_ITEMS:
            source, target = ROOT / item, runtime / item
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
            else:
                shutil.copyfile(source, target)
        venv.EnvBuilder(with_pip=False).create(runtime / ".venv")
        print("Installing Krodak's ClickUp CLI (latest) in your personal tools directory...", flush=True)
        subprocess.run([node, npm, "install", "--prefix", str(runtime / "tools"), "--no-audit", "--no-fund",
                        "--ignore-scripts", "@krodak/clickup-cli@latest"], check=True)
        package = runtime / "tools/node_modules/@krodak/clickup-cli"
        metadata = read_json(package / "package.json")
        entry = (package / metadata["bin"]["cup"]).resolve()
        if not entry.is_relative_to(package.resolve()) or not entry.is_file():
            raise ValueError("The installed ClickUp CLI has an invalid entry point.")
        command = [node, str(entry)]
        subprocess.run(command + ["--version"], check=True)
        save_json(runtime / "runtime.json", {"source_digest": digest, "cup_version": metadata["version"], "cup_command": command})
        return runtime
    except BaseException:
        shutil.rmtree(runtime, ignore_errors=True)
        raise


def setup(args, home):
    node, npm = os.environ.get("CLICKUP_SKILLS_NODE"), os.environ.get("CLICKUP_SKILLS_NPM_CLI")
    if not node or not npm:
        raise ValueError("Run setup through npx so Node and npm can be located automatically.")
    project = args.project_dir.resolve() if args.project_dir else None
    if project and not project.is_dir():
        raise ValueError("The project directory must already exist.")
    destination = config_destination(args.client, project).resolve()
    receipt_path = home / "clients" / (hashlib.sha256(str(destination).encode()).hexdigest() + ".json")
    receipt = read_json(receipt_path, {})
    # Read exact bytes once; reject a concurrent settings edit before saving anything over it.
    original = destination.read_bytes() if destination.exists() else None
    text = original.decode("utf-8") if original is not None else ("" if args.client == "codex" else "{}\n")
    skills = skill_directory("copilot" if args.client == "vscode" else args.client, project_dir=project)
    if not args.skip_skills:
        install(skills, update=True, dry_run=True)
    active = read_json(home / "installation.json", {})
    digest = source_digest(node)
    runtime = Path(active.get("runtime", home / "pending-runtime"))
    # Detect collisions before installing packages or changing skills/settings.
    merge_config(text, args.client, desired_config(args.client, args.profile, runtime), receipt.get("servers", {}))
    metadata = read_json(runtime / "runtime.json", {})
    fresh = (args.command == "update" or metadata.get("source_digest") != digest or not runtime_python(runtime).is_file())
    if fresh:
        runtime = build_runtime(home, node, npm, digest)
    else:
        subprocess.run(metadata["cup_command"] + ["--version"], check=True)
    merged, owned = merge_config(text, args.client, desired_config(args.client, args.profile, runtime), receipt.get("servers", {}))
    if (destination.read_bytes() if destination.exists() else None) != original:
        raise ValueError("Client settings changed during setup. Rerun; your settings were preserved.")
    if not args.skip_skills:
        install(skills, update=True)
    if merged != text:
        if original is not None:
            backup = destination.with_name(destination.name + ".clickup-skills-backup-" + uuid.uuid4().hex[:12])
            atomic_write(backup, text)
            print("Settings backup: " + str(backup))
        atomic_write(destination, merged)
    save_json(receipt_path, {"config": str(destination), "servers": owned})
    save_json(home / "installation.json", {"runtime": str(runtime)})
    print("\nSetup complete: Python environment, Krodak CLI, " + ("external skills unchanged" if args.skip_skills else "managed skills") + ", and MCP configuration.")
    print("Client settings: " + str(destination))
    if args.command != "onboard":
        print("Reload your agent. Each teammate signs in with their own accounts:")
        print("  " + NPX + " cup init")
        print("  " + NPX + " cup auth")
        print("  gh auth login")
        if not shutil.which("gh"):
            print("GitHub CLI is missing. Install it from https://cli.github.com/ before using the local GitHub workflow.")
        print("Ask your agent to verify account access and bind the working project before task writes.")


def setup_host(args, home):
    """Install the agent skills and hosted OAuth MCP. Never read local CLI credentials."""
    if args.profile not in ("default", "official"):
        raise ValueError("OAuth onboarding supports only the official ClickUp MCP; omit --profile context.")
    project = args.project_dir.resolve() if args.project_dir else None
    if project and not project.is_dir():
        raise ValueError("The project directory must already exist.")
    destination = config_destination(args.client, project).resolve()
    receipt_path = home / "clients" / (hashlib.sha256(str(destination).encode()).hexdigest() + ".json")
    receipt = read_json(receipt_path, {})
    original = destination.read_bytes() if destination.exists() else None
    source = original.decode("utf-8") if original is not None else ("" if args.client == "codex" else "{}\n")
    skills = skill_directory("copilot" if args.client == "vscode" else args.client, project_dir=project)
    if not args.skip_skills:
        install(skills, update=True, dry_run=True)
    merged, owned = merge_config(source, args.client, desired_host_config(args.client),
                                 receipt.get("servers", {}))
    if (destination.read_bytes() if destination.exists() else None) != original:
        raise ValueError("Client settings changed during OAuth setup. Rerun; settings were preserved.")
    if not args.skip_skills:
        install(skills, update=True)
    if merged != source:
        if original is not None:
            backup = destination.with_name(destination.name + ".clickup-skills-backup-" + uuid.uuid4().hex[:12])
            atomic_write(backup, source)
            print("Settings backup: " + str(backup))
        atomic_write(destination, merged)
    save_json(receipt_path, {"config": str(destination), "servers": owned, "mode": "oauth"})
    print("\nOAuth setup complete: " + ("external skills unchanged" if args.skip_skills else "six managed skills") +
          ", official ClickUp MCP and GitHub MCP configuration.")
    print("Client settings: " + str(destination))
    print("No ClickUp API token, local workflow runtime, or Krodak CLI is required by this mode.")
    if "clickup_work" in owned:
        print("An existing local clickup_work server was preserved. It does NOT share the hosted OAuth session.")
    print("Reload your agent and authorize clickup_official in its browser OAuth flow if prompted.")
    print("Only the running agent can verify its hosted OAuth, tools, account, workspace and task scope.")


def main():
    home = Path(os.environ.get("CLICKUP_SKILLS_HOME", Path.home() / ".local/share/clickup-skills")).expanduser().resolve()
    args = sys.argv[1:]
    if args[:1] in (["cup"], ["work"]):
        installed = read_json(home / "installation.json", {})
        if not installed.get("runtime"):
            raise ValueError("Run setup --client CLIENT first.")
        runtime = Path(installed["runtime"])
        command = [str(runtime_python(runtime)), "-I", str(runtime / "scripts/run_work.py")]
        raise SystemExit(subprocess.call(command + (["--cup"] if args[0] == "cup" else []) + args[1:]))
    parser = argparse.ArgumentParser(description=__doc__, epilog="Also: cup <arguments> or work <cu-work arguments> after setup.")
    parser.add_argument("command", choices=["setup", "update", "onboard"])
    parser.add_argument("--client", choices=CLIENTS)
    parser.add_argument("--mode", choices=["oauth", "cli"],
                        help="Onboarding mode: oauth (default, hosted official MCP) or cli (personal API token/full helper).")
    parser.add_argument("--skip-skills", action="store_true", help="Leave externally installed skills untouched (e.g. npx skills add)")
    parser.add_argument("--profile", choices=["default", "official", "context"], default="default")
    parser.add_argument("--project-dir", type=Path, help="Install project skills and config instead of personal settings")
    options = parser.parse_args(args)
    if options.command != "onboard" and options.mode is not None:
        parser.error("--mode is supported only for onboard; setup/update retain their existing CLI behavior.")
    if options.client is None:
        if options.command == "onboard":
            from onboard import choose_client
            options.client = choose_client()
        else:
            parser.error("--client is required for setup and update.")
    if options.command == "onboard":
        from onboard import run_onboarding
        mode = options.mode or "oauth"
        if mode == "oauth":
            setup_host(options, home)
            run_onboarding(None, mode="oauth")
        else:
            setup(options, home)
            active = read_json(home / "installation.json", {})
            run_onboarding(Path(active["runtime"]), mode="cli")
    else:
        setup(options, home)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        # Never print third-party command output or configuration contents.
        message = "A required installation/verification command failed; resolve it and rerun setup." if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        print("Setup stopped: " + message, file=sys.stderr)
        raise SystemExit(1)
