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
for project in json.loads((ROOT / "upstreams.lock.json").read_text(encoding="utf-8"))["projects"]:
    assert re.fullmatch(r"[a-f0-9]{40}", project["commit"]), project
    notice = (ROOT / project["notice"]).read_text(encoding="utf-8")
    assert project["license"] == "MIT" and "Permission is hereby granted" in notice, project

# Check that generated client configurations are reproducible without rewriting source.
spec = importlib.util.spec_from_file_location("metadata", ROOT / "scripts/build_metadata.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as temporary:
    module.ROOT = Path(temporary)
    module.main()
    for generated in Path(temporary).rglob("*.json"):
        actual = ROOT / generated.relative_to(temporary)
        assert actual.read_text(encoding="utf-8") == generated.read_text(encoding="utf-8"), str(actual) + " is stale"
for profile in ("default", "official", "context", "rest"):
    rendered = subprocess.run([sys.executable, "scripts/configure.py", "--client", "codex", "--profile", profile],
                              capture_output=True, text=True, encoding="utf-8", check=True)
    config = tomllib.loads(rendered.stdout)
    assert "clickup_work" in config["mcp_servers"] and "github" in config["mcp_servers"]
assert compileall.compile_dir("src", quiet=1)
subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], env=env, check=True)
print("All offline checks passed: skills, manifests, profiles, licenses, Python, and workflows.")
