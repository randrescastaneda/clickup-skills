"""Versioned project bindings, scope validation, and per-worktree operation state."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


class WorkError(Exception):
    """An actionable failure safe to display to an agent."""


@contextlib.contextmanager
def process_lock(path):
    """An OS-held lock releases on process exit; never unlink its lock file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        try:
            if os.name == "nt":
                import msvcrt
                if os.fstat(fd).st_size == 0:
                    os.write(fd, b" ")
                os.lseek(fd, 0, os.SEEK_SET)
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise WorkError("Another workflow holds " + path.name + "; wait for its owner to exit.") from exc
        yield
    finally:
        os.close(fd)


def identifier(value):
    value = str(value)
    if not re.fullmatch(r"[A-Za-z0-9_-]+", value):
        raise WorkError("Use a native ClickUp ID, not a URL or custom task alias.")
    return value


def repository(value):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise WorkError("GitHub repository must be owner/name.")
    return value


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                            text=True, encoding="utf-8", timeout=10, check=False)
    if result.returncode:
        raise WorkError("Cannot inspect Git repository: " + " ".join(args[:2]))
    return result.stdout.strip()


def remote_repository(value):
    match = re.fullmatch(r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?/?", value)
    if not match:
        raise WorkError("Origin must be a github.com repository without embedded credentials.")
    return repository(match.group(1))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".tmp-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate(config):
    try:
        if config["version"] != 1:
            raise WorkError("Unsupported project binding version.")
        if not config["name"].strip() or not config["objective"].strip():
            raise WorkError("Project name and objective are required.")
        cu = config["clickup"]
        identifier(cu["workspace_id"])
        identifier(cu["list_id"])
        if not isinstance(cu["root_task_ids"], list) or not cu["root_task_ids"]:
            raise WorkError("Bind at least one root task.")
        for task in cu["root_task_ids"]:
            identifier(task)
        repository(config["github"]["repository"])
        if not isinstance(config["github"]["base_branch"], str) or not config["github"]["base_branch"].strip():
            raise WorkError("A GitHub base branch is required.")
        if type(config["github"].get("require_checks", True)) is not bool:
            raise WorkError("require_checks must be a boolean.")
        if not isinstance(config["routing"].get("prefer", []), list):
            raise WorkError("routing.prefer must be a list.")
        if config["routing"].get("runtime", "cup") not in ("cup", "rest-mcp"):
            raise WorkError("Local runtime must be cup or rest-mcp; other MCPs run in the host.")
        if config["routing"].get("comment_reader", "upstream") not in ("upstream", "clickup-api"):
            raise WorkError("Comment reader must be upstream or clickup-api; it never changes the write runtime.")
        for status in config["github"].get("status_map", {}).values():
            if not isinstance(status, str) or not status.strip():
                raise WorkError("Status mappings must be non-empty strings.")
    except (KeyError, TypeError, AttributeError) as exc:
        raise WorkError("Invalid project binding; see examples/project.json.") from exc
    return config


class Context:
    def __init__(self, directory):
        self.root = Path(git(Path(directory).resolve(), "rev-parse", "--show-toplevel"))
        path = self.root / ".clickup/project.json"
        if not path.is_file():
            raise WorkError("No binding. Run cu-work init in this repository first.")
        self.config = validate(json.loads(path.read_text(encoding="utf-8")))
        actual = remote_repository(git(self.root, "remote", "get-url", "origin"))
        if actual.lower() != self.config["github"]["repository"].lower():
            raise WorkError("Origin differs from the project binding; refusing cross-repository work.")
        # git-path resolves separately for each worktree, including linked worktrees.
        state_dir = Path(git(self.root, "rev-parse", "--git-path", "clickup-skills"))
        self.local = state_dir if state_dir.is_absolute() else self.root / state_dir
        self.local.mkdir(parents=True, exist_ok=True)
        common = Path(git(self.root, "rev-parse", "--git-common-dir"))
        self.shared = (common if common.is_absolute() else self.root / common) / "clickup-skills"
        self.fingerprint = hashlib.sha256(json.dumps(self.config, sort_keys=True).encode()).hexdigest()

    @contextlib.contextmanager
    def locked(self):
        # Do not bypass a running/crashed pre-worker version's exclusive lock.
        if (self.local / "write.lock").exists():
            raise WorkError("Legacy write.lock exists. Inspect its PID/process before removing it.")
        with process_lock(self.shared / "write.lock.guard"):
            yield

    def state(self):
        path = self.local / "state.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        return data

    def save(self, data):
        write_json(self.local / "state.json", data)

    def task_id(self, explicit=None):
        state = self.state()
        focus = state.get("focus") if state.get("binding") == self.fingerprint else None
        return identifier(explicit or focus or self.config["clickup"]["root_task_ids"][0])

    def scoped(self, task_id, fetch):
        """Verify identity, workspace, home list, and ancestry with fresh remote reads."""
        current = identifier(task_id)
        roots = set(self.config["clickup"]["root_task_ids"])
        visited = set()
        original = None
        for _ in range(64):
            if current in visited:
                raise WorkError("Task ancestry contains a cycle.")
            visited.add(current)
            task = fetch(current)
            if str(task.get("id")) != current:
                raise WorkError("Backend returned a different task ID.")
            if str(task.get("team_id")) != self.config["clickup"]["workspace_id"]:
                raise WorkError("Task workspace is missing or does not match the binding.")
            if str(task.get("list", {}).get("id")) != self.config["clickup"]["list_id"]:
                raise WorkError("Task home list does not match the binding.")
            original = original or task
            if current in roots:
                return original
            parent = task.get("parent")
            if not parent:
                break
            current = identifier(parent)
        raise WorkError("Task is outside the bound roots and their descendants.")
