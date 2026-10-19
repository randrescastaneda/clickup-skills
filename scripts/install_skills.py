"""Link this checkout's skills into a local client, without replacing existing skills."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--client", choices=["codex", "claude", "opencode"], required=True)
p.add_argument("--destination", type=Path, help="Override the normal user skill directory")
a = p.parse_args()
defaults = {"codex": ".agents/skills", "claude": ".claude/skills", "opencode": ".config/opencode/skills"}
dest = a.destination or Path.home() / defaults[a.client]
dest.mkdir(parents=True, exist_ok=True)
for source in sorted((ROOT / "skills").iterdir()):
    if not (source / "SKILL.md").exists():
        continue
    target = dest / source.name
    if target.is_symlink() and target.resolve() == source:
        print("Already linked: " + str(target))
    elif target.exists() or target.is_symlink():
        raise SystemExit("Refusing to replace existing skill: " + str(target))
    else:
        target.symlink_to(source, target_is_directory=True)
        print("Linked: " + str(target))
