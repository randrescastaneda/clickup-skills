"""cu-work: local project context plus deterministic, scoped workflow operations."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from .context import Context, WorkError, git, validate, write_json
from .routing import CAPABILITIES, route
from .workflow import Workflow


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project-dir", default=".", help="Target Git worktree, never the plugin install directory")
    sub = p.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create the shared binding; performs no remote writes")
    for name in ("name", "objective", "workspace", "list", "repository"):
        init.add_argument("--" + name, required=True)
    init.add_argument("--task", action="append", required=True)
    init.add_argument("--base-branch", default="main")
    init.add_argument("--runtime", choices=["cup", "rest-mcp"], default="cup")
    init.add_argument("--cup-profile")
    init.add_argument("--comment-reader", choices=["upstream", "clickup-api"], default="upstream")
    sub.add_parser("context")
    sub.add_parser("doctor")
    r = sub.add_parser("route")
    r.add_argument("operation", choices=list(CAPABILITIES))
    r.add_argument("--available", required=True, help="Comma-separated backends actually available in this session")
    for name in ("task", "focus", "subtask", "progress", "link-pr", "link-github", "sync-comments", "phase"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--task")
        if name in ("subtask", "progress", "link-pr", "link-github", "phase"):
            cmd.add_argument("--key", required=True, help="Stable key, reused only for identical inputs")
        if name == "subtask":
            cmd.add_argument("--title", required=True)
            cmd.add_argument("--description-file", type=Path, required=True)
            cmd.add_argument("--github-target", help="Bound repo/issue/PR URL; default creates/reuses an issue")
        if name == "link-github":
            cmd.add_argument("--target", required=True, help="Bound repo/issue/PR URL or new-issue")
            cmd.add_argument("--title", help="Required for new-issue")
            cmd.add_argument("--description-file", type=Path)
        if name == "sync-comments":
            cmd.add_argument("--direction", choices=["both", "to-clickup", "to-github"], default="both")
        if name == "progress":
            cmd.add_argument("--message-file", type=Path, required=True)
        if name in ("link-pr", "phase"):
            cmd.add_argument("--pr", type=int, required=name == "link-pr")
        if name == "phase":
            cmd.add_argument("--phase", choices=["in_progress", "review", "done"], required=True)
            cmd.add_argument("--verification-file", type=Path)
    reconcile = sub.add_parser("reconcile")
    reconcile.add_argument("--key", required=True)
    group = reconcile.add_mutually_exclusive_group(required=True)
    group.add_argument("--result-file", type=Path)
    group.add_argument("--not-applied", action="store_true")
    worker = sub.add_parser("sync-worker", help="Preview or poll comment sync for explicit tasks; never starts during setup")
    worker.add_argument("--task", action="append", required=True, help="Native task ID; repeat for each allowed task")
    worker.add_argument("--direction", choices=["both", "to-clickup", "to-github"], default="both")
    worker.add_argument("--apply", action="store_true", help="Allow the existing scoped comment writes; default only previews")
    worker.add_argument("--watch", action="store_true", help="Continue polling until stopped; requires --apply")
    worker.add_argument("--interval", type=int, default=300, help="Seconds after each pass, minimum 60")
    worker.add_argument("--max-writes", type=int, default=20, help="Total new mirrors allowed per pass, maximum 100")
    sub.add_parser("mcp", help="Serve task-scoped workflow tools over stdio")
    return p


def dispatch(args):
    if args.command == "sync-worker":
        from .worker import run_worker
        return run_worker(args.project_dir, args.task, args.direction, apply=args.apply,
                          watch=args.watch, interval=args.interval, max_writes=args.max_writes,
                          emit=(lambda report: print(json.dumps(report), flush=True)) if args.watch else None)
    if args.command == "mcp":
        from .mcp import serve
        serve()
        return None
    if args.command == "init":
        root = Path(git(args.project_dir, "rev-parse", "--show-toplevel"))
        path = root / ".clickup/project.json"
        if path.exists():
            raise WorkError("Binding already exists. Review and edit it instead of silently rebinding.")
        config = validate({"version": 1, "name": args.name, "objective": args.objective,
                           "clickup": {"workspace_id": args.workspace, "list_id": args.list,
                                       "root_task_ids": args.task},
                           "github": {"repository": args.repository, "base_branch": args.base_branch,
                                      "status_map": {}, "require_checks": True},
                           "routing": {"runtime": args.runtime, "cup_profile": args.cup_profile,
                                       "comment_reader": args.comment_reader,
                                       "prefer": [], "overrides": {}}})
        from .context import remote_repository
        if remote_repository(git(root, "remote", "get-url", "origin")).lower() != args.repository.lower():
            raise WorkError("Origin and requested repository differ.")
        write_json(path, config)
        return {"binding": str(path), "remote_verified": False,
                "next": "Read each bound task and confirm scope before any remote write."}
    if args.command == "route":
        try:
            ctx = Context(args.project_dir)
        except WorkError as exc:
            if "No binding." not in str(exc):
                raise
            ctx = None
        return route(args.operation, args.available.split(","), ctx.config if ctx else None)
    ctx = Context(args.project_dir)
    if args.command == "context":
        return {"project": ctx.config, "active_task_id": ctx.task_id(), "binding_digest": ctx.fingerprint,
                "local_state": str(ctx.local / "state.json")}
    if args.command == "doctor":
        executables = {name: bool(shutil.which(name)) for name in ("cup", "gh", "clickup-rest-mcp")}
        if os.environ.get("CU_WORK_CUP_COMMAND"):
            command = json.loads(os.environ["CU_WORK_CUP_COMMAND"])
            executables["cup"] = bool(isinstance(command, list) and command and all(isinstance(v, str) for v in command)
                                      and shutil.which(command[0]) and (len(command) < 2 or Path(command[1]).is_file()))
        return {"binding_valid": True, "runtime": ctx.config["routing"]["runtime"],
                "comment_reader": ctx.config["routing"].get("comment_reader", "upstream"),
                "executables": executables,
                "credentials": "Not inspected or printed. Run cup auth / gh auth status separately.",
                "remote_verified": False}
    work = Workflow(ctx)
    try:
        if args.command == "task":
            return work.task(args.task)
        with ctx.locked():
            if args.command == "focus":
                task = work.task(args.task)
                state = ctx.state()
                state.update(focus=str(task["id"]), binding=ctx.fingerprint)
                ctx.save(state)
                return {"active_task_id": task["id"], "objective": ctx.config["objective"]}
            if args.command == "subtask":
                return work.subtask(args.title, args.description_file.read_text(encoding="utf-8"), args.key,
                                    args.task, args.github_target)
            if args.command == "progress":
                return work.progress(args.message_file.read_text(encoding="utf-8"), args.key, args.task)
            if args.command == "link-pr":
                return work.link_pr(args.pr, args.key, args.task)
            if args.command == "link-github":
                text = args.description_file.read_text(encoding="utf-8") if args.description_file else ""
                return work.link_github(args.target, args.key, args.task, args.title, text)
            if args.command == "sync-comments":
                return work.sync_comments(args.task, args.direction)
            if args.command == "phase":
                text = args.verification_file.read_text(encoding="utf-8") if args.verification_file else None
                return work.phase(args.phase, args.key, args.task, args.pr, text)
            if args.command == "reconcile":
                result = json.loads(args.result_file.read_text(encoding="utf-8")) if args.result_file else None
                return work.reconcile(args.key, result, args.not_applied)
    finally:
        work.close()


def main():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    try:
        result = dispatch(parser().parse_args())
        if result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (WorkError, OSError, ValueError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
