"""Opt-in polling of explicit tasks using the existing scoped reconciliation."""

from datetime import datetime, timezone
import time

from .context import Context, WorkError, identifier, process_lock, write_json
from .workflow import Workflow


def summary(plan):
    pending = [op for op in plan["operations"] if op["write_needed"]]
    return {"task_id": plan["task_id"], "direction": plan["direction"],
            "new_to_clickup": sum(op["destination"] == "clickup" for op in pending),
            "new_to_github": sum(op["destination"] == "github" for op in pending),
            "already_recorded": len(plan["operations"]) - len(pending)}


def run_worker(project_dir, tasks, direction="both", *, apply=False, watch=False,
               interval=300, max_writes=20, emit=None, context_factory=Context,
               workflow_factory=Workflow, wait=time.sleep):
    """A failure exits; only verified remote markers recover uncertain writes."""
    if not tasks or not isinstance(tasks, list):
        raise WorkError("Worker requires an explicit list of native task IDs; focus is never used.")
    tasks = list(dict.fromkeys(identifier(task) for task in tasks))
    if type(interval) is not int or interval < 60:
        raise WorkError("Worker interval must be at least 60 seconds.")
    if type(max_writes) is not int or not 1 <= max_writes <= 100:
        raise WorkError("Worker max-writes must be between 1 and 100 per pass.")
    if watch and not apply:
        raise WorkError("Watch requires --apply. Omit both flags for a read-only preview.")
    original = context_factory(project_dir)
    fingerprint = original.fingerprint
    report = {"status": "starting", "binding_digest": fingerprint, "task_ids": tasks,
              "direction": direction, "apply": apply, "passes": 0}

    def record(status, **fields):
        report.update(status=status, updated_at=datetime.now(timezone.utc).isoformat(), **fields)
        # No source bodies, credentials, subprocess output or arbitrary errors in health data.
        if apply:
            write_json(original.local / "worker-status.json", report)

    with process_lock(original.shared / "worker.lock.guard"):
        try:
            while True:
                ctx = context_factory(project_dir)
                if ctx.fingerprint != fingerprint:
                    raise WorkError("Project binding changed. Restart with the intended scope before resuming.")
                work = workflow_factory(ctx)
                try:
                    # Preflight every allowed task before writing to any of them. CLI/MCP
                    # writers in other linked worktrees share this same repository lock.
                    with ctx.locked():
                        plans = [work.plan_comments(task, direction) for task in tasks]
                        reports = [summary(plan) for plan in plans]
                        writes = sum(r["new_to_clickup"] + r["new_to_github"] for r in reports)
                        if apply and writes > max_writes:
                            raise WorkError("Sync exceeds max-writes for this pass. Preview the backlog and raise the explicit limit if intended.")
                        # The current local readers cannot recover markers once a task
                        # reaches 25 comments. Do not begin a batch that crosses that limit.
                        if apply and any(not plan["complete_history"] and
                                         plan["comment_count"] + r["new_to_clickup"] >= 25
                                         for plan, r in zip(plans, reports)):
                            raise WorkError("Sync would reach the 25-comment read limit. Use complete paginated host reads before continuing.")
                        if apply:
                            for plan in plans:
                                work.apply_comment_plan(plan)
                        record("healthy" if apply else "preview", passes=report["passes"] + 1,
                               tasks=reports, planned_writes=writes)
                finally:
                    work.close()
                if emit:
                    emit(dict(report))
                if not watch:
                    return dict(report)
                # The write lock is released while waiting, so foreground work can proceed.
                wait(interval)
        except KeyboardInterrupt:
            record("stopped")
            return dict(report)
        except Exception:
            record("blocked")
            raise
