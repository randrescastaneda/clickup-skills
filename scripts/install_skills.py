"""Install the shared skills for an agent; refuse conflicts before writing anything."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from clickup_skills.clients import SKILL_PATHS, skill_directory


def digest(directory):
    result = hashlib.sha256()
    for file in sorted(directory.rglob("*")):
        if file.is_file() and file.name not in (".clickup-skills.json", "LICENSE"):
            result.update(file.relative_to(directory).as_posix().encode())
            result.update(b"\0" + file.read_bytes())
    return result.hexdigest()


def install(destination, method="copy", update=False):
    destination = Path(destination)
    actions = []
    for source in sorted((ROOT / "skills").iterdir()):
        if not (source / "SKILL.md").is_file():
            continue
        target = destination / source.name
        same_link = target.is_symlink() and target.resolve() == source
        same_copy = target.is_dir() and not target.is_symlink() and digest(target) == digest(source)
        action = method
        if target.exists() or target.is_symlink():
            receipt = target / ".clickup-skills.json"
            metadata = json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else {}
            managed = metadata.get("package") == "clickup-skills"
            unmodified = managed and digest(target) == metadata.get("digest")
            if same_link or same_copy:
                action = "unchanged"
            elif update and unmodified and not target.is_symlink() and method == "copy":
                action = "update"
            else:
                raise ValueError("Refusing to replace existing or locally modified skill: " + str(target))
        actions.append((source, target, action))
    destination.mkdir(parents=True, exist_ok=True)
    for source, target, action in actions:
        if action in ("copy", "update"):
            if action == "update":
                shutil.rmtree(target)
            shutil.copytree(source, target)
            shutil.copyfile(ROOT / "LICENSE", target / "LICENSE")
            (target / ".clickup-skills.json").write_text(json.dumps({"package": "clickup-skills", "digest": digest(source)}), encoding="utf-8")
        elif action == "link":
            try:
                target.symlink_to(source, target_is_directory=True)
            except OSError as exc:
                raise ValueError("Cannot create a symlink; retry with --method copy.") from exc
        print(action.capitalize() + ": " + str(target))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--client", choices=list(SKILL_PATHS), required=True)
    p.add_argument("--scope", choices=["user", "project"], default="user")
    p.add_argument("--project-dir", type=Path)
    p.add_argument("--destination", type=Path, help="Explicit skill directory for isolated testing")
    p.add_argument("--method", choices=["copy", "link"], default="copy", help="Copy works without Windows symlink privileges")
    p.add_argument("--update", action="store_true", help="Update managed copies only when their content is unmodified")
    a = p.parse_args()
    if a.scope == "project" and a.project_dir is None:
        p.error("--scope project requires --project-dir")
    if a.scope == "user" and a.project_dir is not None:
        p.error("--project-dir requires --scope project")
    dest = a.destination or skill_directory(a.client, project_dir=a.project_dir if a.scope == "project" else None)
    try:
        install(dest, a.method, a.update)
    except ValueError as exc:
        p.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
