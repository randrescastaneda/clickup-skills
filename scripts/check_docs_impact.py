"""Require a documentation decision when a PR/push changes plugin behavior."""

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BEHAVIOR = ("src/", "skills/", "profiles/", "bin/", "package.json", "scripts/setup.py", "scripts/run_work.py", "scripts/configure.py", "scripts/install_skills.py", "scripts/build_metadata.py", "plugin.json", "mcp.json", ".claude-plugin/", "pyproject.toml", "upstreams.lock.json")
GUIDES = {"site/content/installation.md", "site/content/project-setup.md", "site/content/using-the-plugin.md", "site/content/examples.md", "site/content/synchronization.md", "site/content/troubleshooting.md", "docs/clients.md", "docs/contract.md", "docs/wiki/github-clickup.md"}


def check(changed, old, new):
    behavior = {p for p in changed if any(p.startswith(prefix) for prefix in BEHAVIOR)}
    if not behavior or GUIDES.intersection(changed):
        return
    previous = [json.dumps(entry, sort_keys=True) for entry in old.get("changes", [])]
    covered = set()
    for entry in new.get("changes", []):
        if json.dumps(entry, sort_keys=True) in previous:
            continue
        reason = entry.get("reason", "").strip()
        paths = entry.get("paths", [])
        if len(reason) < 50 or not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
            raise ValueError("New docs-impact entries need exact paths and a concrete reason (at least 50 characters).")
        covered.update(paths)
    missing = behavior - covered
    if missing:
        raise ValueError("Plugin behavior changed without a guide/example update or new reviewed docs-impact rationale for: " + ", ".join(sorted(missing)))


def main(base):
    # A first push has no meaningful predecessor to compare.
    if not base or set(base) == {"0"}:
        print("No comparison base; documentation build checks still apply.")
        return
    changed = subprocess.check_output(["git", "diff", "--name-only", base, "HEAD"], cwd=ROOT, text=True).splitlines()
    prior = subprocess.run(["git", "show", base + ":site/docs-impact.json"], cwd=ROOT, text=True, capture_output=True)
    old = json.loads(prior.stdout) if prior.returncode == 0 else {"changes": []}
    new = json.loads((ROOT / "site/docs-impact.json").read_text(encoding="utf-8"))
    check(changed, old, new)
    print("Documentation impact decision verified.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    main(args.base)
