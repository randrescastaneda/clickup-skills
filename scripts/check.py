"""Run repository validation offline; no third-party Python packages required."""

import compileall
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / "src"))
env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
for file in ROOT.rglob("*.json"):
    if any(part in {".git", "node_modules", ".venv"} for part in file.parts):
        continue
    json.loads(file.read_text(encoding="utf-8"))
for file in (ROOT / "skills").glob("*/SKILL.md"):
    text = file.read_text(encoding="utf-8")
    front = text.split("---", 2)[1]
    assert re.search(r"^name: " + re.escape(file.parent.name) + r"$", front, re.M), file
    assert re.search(r"^description: .+", front, re.M), file
    assert "[TODO" not in text, file
    assert (file.parent / "agents/openai.yaml").is_file(), file
    assert re.search(r"^license: MIT$", front, re.M), file
    name = re.search(r"^name: (.+)$", front, re.M)[1]
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64, file
    assert len(re.search(r"^description: (.+)$", front, re.M)[1]) <= 1024, file
    compatibility = re.search(r"^compatibility: (.+)$", front, re.M)
    assert compatibility and len(compatibility[1]) <= 500, file
    assert len(text.splitlines()) <= 200, file
# The five workflow skills open with the same selection check, byte for byte.
WORKFLOW = ("clickup-bind-project", "clickup-route", "clickup-work-task", "clickup-github", "clickup-handoff")
blocks = {re.search(r"<!-- selection-check:start -->.*?<!-- selection-check:end -->",
                    (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8"), re.S)[0] for name in WORKFLOW}
assert len(blocks) == 1, "The selection-check block differs between workflow skills"
RETIRED = re.compile(r"full[- ]helper|oauth host-agent|oauth mode|oauth-only", re.I)
for file in (ROOT / "skills").rglob("*.md"):
    assert not RETIRED.search(file.read_text(encoding="utf-8")), ("Retired mode term", file)
# Installed skills are copied without the rest of the repository: relative links
# must stay inside skills/, and every other link must be absolute HTTPS.
for file in (ROOT / "skills").rglob("*.md"):
    for target in re.findall(r"\]\(([^)\s]+)\)", file.read_text(encoding="utf-8")):
        if re.match(r"[a-z]+:", target):
            assert target.startswith("https:"), (file, target)
            continue
        resolved = (file.parent / target.split("#")[0]).resolve()
        assert resolved.is_file() and resolved.is_relative_to(ROOT / "skills"), (file, target)
for project in json.loads((ROOT / "upstreams.lock.json").read_text(encoding="utf-8"))["projects"]:
    assert re.fullmatch(r"[a-f0-9]{40}", project["commit"]), project
    notice = (ROOT / project["notice"]).read_text(encoding="utf-8")
    assert project["license"] == "MIT" and "Permission is hereby granted" in notice, project

versions = {json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"],
            tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]}
# Check that generated client configurations are reproducible without rewriting source.
spec = importlib.util.spec_from_file_location("metadata", ROOT / "scripts/build_metadata.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
for path, source in module.BUNDLED.items():
    assert (ROOT / path).read_bytes() == (ROOT / source).read_bytes(), path + " differs from " + source
assert versions == {module.VERSION}, "Version differs between package.json, pyproject.toml and build_metadata.py"
with tempfile.TemporaryDirectory() as temporary:
    module.ROOT = Path(temporary)
    module.main()
    for generated in (p for p in Path(temporary).rglob("*") if p.is_file()):
        actual = ROOT / generated.relative_to(temporary)
        assert actual.is_file() and actual.read_bytes() == generated.read_bytes(), str(actual) + " is stale"
for profile in ("remote-only", "local-helper", "default", "official", "context", "rest"):
    rendered = subprocess.run([sys.executable, "scripts/configure.py", "--client", "codex", "--profile", profile],
                              capture_output=True, text=True, encoding="utf-8", check=True)
    config = tomllib.loads(rendered.stdout)
    servers = config["mcp_servers"]
    if profile in ("official", "remote-only"):
        assert servers == {"clickup_official": {"url": "https://mcp.clickup.com/mcp"}}
    else:
        assert "clickup_work" in servers and "github" in servers
assert compileall.compile_dir("src", quiet=1)
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], env=env, check=True)
print("All offline checks passed: skills, manifests, profiles, licenses, Python, and workflows.")
