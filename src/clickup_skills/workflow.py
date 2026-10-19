"""Scoped writes, resumable operation receipts, and ClickUp/GitHub linkage."""

import hashlib
import json
import os
import re
import tempfile

from .backends import ClickUp, execute
from .context import WorkError, identifier


def marker(key):
    return "cu-work:" + hashlib.sha256(key.encode()).hexdigest()[:24]


class Workflow:
    def __init__(self, context, backend=None):
        self.context = context
        self.backend = backend or ClickUp(context)

    def close(self):
        self.backend.close()

    def task(self, explicit=None):
        return self.context.scoped(self.context.task_id(explicit), self.backend.get)

    def once(self, key, payload, action, recover=None):
        if not key or len(key) > 200:
            raise WorkError("A stable operation key of 1–200 characters is required.")
        digest = hashlib.sha256(json.dumps([self.context.fingerprint, payload], sort_keys=True).encode()).hexdigest()
        state = self.context.state()
        journal = state.setdefault("operations", {})
        previous = journal.get(key)
        if previous:
            if previous["digest"] != digest:
                raise WorkError("Operation key already belongs to different inputs or a different binding.")
            if previous["state"] == "done":
                return {"reused": True, "result": previous["result"]}
            recovered = recover() if recover else None
            if recovered is not None:
                journal[key].update(state="done", result=recovered)
                self.context.save(state)
                return {"reconciled": True, "result": recovered}
            raise WorkError("Operation outcome is uncertain. Inspect the remote marker and reconcile this key; do not switch backends.")
        # Attempt remote marker recovery even when another teammate made the operation.
        recovered = recover() if recover else None
        journal[key] = {"digest": digest, "state": "pending", "operation": payload["operation"],
                        "task_id": payload.get("task_id")}
        self.context.save(state)
        result = recovered if recovered is not None else action()
        journal[key].update(state="done", result=result)
        self.context.save(state)
        return {"reused": recovered is not None, "result": result}

    def progress(self, text, key, task_id=None):
        if not text.strip():
            raise WorkError("Progress text must not be empty.")
        task = self.task(task_id)
        task_id = str(task["id"])
        token = marker(self.context.fingerprint + task_id + key)
        body = text.rstrip() + "\n\n[" + token + "]"
        def recover():
            comments = self.backend.comments(task_id)
            hits = [c for c in comments if token in str(c.get("comment_text", c.get("text", "")))]
            if len(hits) > 1:
                raise WorkError("Multiple remote comments match this operation; inspect them.")
            return {"id": hits[0].get("id"), "task_id": task_id} if hits else None
        return self.once(key, {"operation": "comment", "task_id": task_id, "body": body},
                         lambda: self.backend.comment(task_id, body), recover)

    def subtask(self, title, description, key, task_id=None):
        if not title.strip():
            raise WorkError("Subtask title must not be empty.")
        parent = self.task(task_id)
        parent_id = str(parent["id"])
        token = marker(self.context.fingerprint + parent_id + key)
        body = description.rstrip() + "\n\n[" + token + "]"
        def recover():
            children = self.backend.children(parent_id)
            hits = []
            for child in children:
                if child.get("name") != title:
                    continue
                full = self.context.scoped(str(child["id"]), self.backend.get)
                if token in str(full.get("description", "")) + str(full.get("markdown_description", "")):
                    hits.append(full)
            if len(hits) > 1:
                raise WorkError("Multiple subtasks match this operation; inspect them.")
            return {"id": hits[0]["id"], "name": title, "url": hits[0].get("url")} if hits else None
        def create():
            result = self.backend.subtask(parent_id, title, body)
            child = self.context.scoped(identifier(result.get("id", "")), self.backend.get)
            if str(child.get("parent")) != parent_id:
                raise WorkError("Created task does not have the expected parent. Reconcile before another write.")
            return {"id": child["id"], "name": child["name"], "url": child.get("url")}
        return self.once(key, {"operation": "subtask", "task_id": parent_id, "title": title, "body": body},
                         create, recover)

    def pr(self, number):
        if not str(number).isdigit() or int(number) < 1:
            raise WorkError("Use a positive pull request number in the bound repository.")
        repo = self.context.config["github"]["repository"]
        data = execute(["gh", "pr", "view", str(number), "--repo", repo, "--json",
                        "url,body,state,headRefOid,statusCheckRollup,isDraft,baseRefName"], self.context.root)
        expected = f"https://github.com/{repo}/pull/{int(number)}"
        if data.get("url", "").lower() != expected.lower():
            raise WorkError("GitHub returned a PR from a different repository.")
        if data.get("baseRefName") != self.context.config["github"]["base_branch"]:
            raise WorkError("PR targets a different base branch from the binding.")
        return data

    def link_pr(self, number, key, task_id=None):
        task = self.task(task_id)
        task_id = str(task["id"])
        pr = self.pr(number)
        repo = self.context.config["github"]["repository"]
        tag = "clickup-skills:" + task_id
        start, end = "<!-- " + tag + " -->", "<!-- /" + tag + " -->"
        block = (start + "\nClickUp: https://app.clickup.com/t/" + task_id +
                 "\n\nObjective: " + self.context.config["objective"] + "\n" + end)
        body = pr.get("body") or ""
        if body.count(start) != body.count(end) or body.count(start) > 1:
            raise WorkError("PR contains malformed or duplicate managed blocks; resolve before linking.")
        if start in body:
            updated = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, body, flags=re.S)
        else:
            updated = body.rstrip() + "\n\n" + block + "\n"
        def apply():
            # Refresh before modifying: do not overwrite edits made since the first read.
            fresh = self.pr(number)
            if (fresh.get("body") or "") != body:
                raise WorkError("PR body changed concurrently. Re-read and reconcile before retrying.")
            fd, path = tempfile.mkstemp(prefix="cu-work-pr-", suffix=".json")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump({"body": updated}, handle)
                execute(["gh", "api", "--method", "PATCH", f"repos/{repo}/pulls/{int(number)}",
                         "--input", path], self.context.root)
            finally:
                os.unlink(path)
            if block not in (self.pr(number).get("body") or ""):
                raise WorkError("PR update not verified. Reconcile before another write.")
            return {"url": pr["url"]}
        def recover():
            return {"url": pr["url"]} if block in (self.pr(number).get("body") or "") else None
        # Separate receipts permit resuming if GitHub succeeds and ClickUp fails.
        github = self.once(key + ":github", {"operation": "pr-body", "task_id": task_id,
                                             "pr": pr["url"], "block": block}, apply, recover)
        clickup = self.progress("Pull request: " + pr["url"] + "\nObjective: " + self.context.config["objective"],
                                key + ":clickup", task_id)
        return {"github": github, "clickup": clickup, "note": "Links recorded; no status was changed."}

    def phase(self, phase, key, task_id=None, pr_number=None, verification=None):
        task = self.task(task_id)
        mapped = self.context.config["github"].get("status_map", {}).get(phase)
        if not mapped:
            raise WorkError("Configure an exact ClickUp status_map for phase " + phase + ".")
        evidence = None
        if phase == "done":
            if not pr_number or not verification or not verification.strip():
                raise WorkError("Done requires a PR number and a non-empty verification summary.")
            pr = self.pr(pr_number)
            if pr.get("state") != "MERGED" or pr.get("isDraft"):
                raise WorkError("Done requires a merged, non-draft PR.")
            if ("<!-- clickup-skills:" + str(task["id"]) + " -->") not in (pr.get("body") or ""):
                raise WorkError("PR is not linked to this task. Link and verify it before completion.")
            checks = pr.get("statusCheckRollup") or []
            if not checks and self.context.config["github"].get("require_checks", True):
                raise WorkError("No CI checks found; keep the task open or explicitly configure require_checks=false.")
            for check in checks:
                if check.get("__typename") == "StatusContext" or "state" in check:
                    passed = check.get("state") == "SUCCESS"
                else:
                    passed = check.get("status") == "COMPLETED" and check.get("conclusion") == "SUCCESS"
                if not passed:
                    raise WorkError("CI is pending, missing, or not successful; keep the task open.")
            evidence = {"pr": pr["url"], "head": pr["headRefOid"], "verification": verification}
            self.progress("Completion verification\nPR: " + pr["url"] + "\nHead: " + pr["headRefOid"] +
                          "\n\n" + verification, key + ":verification", str(task["id"]))
        def recover():
            fresh = self.task(str(task["id"]))
            status = fresh.get("status", {})
            status = status.get("status") if isinstance(status, dict) else status
            return {"id": task["id"], "status": mapped} if status == mapped else None
        return self.once(key, {"operation": "status", "task_id": str(task["id"]), "status": mapped,
                               "evidence": evidence}, lambda: self.backend.status(str(task["id"]), mapped), recover)

    def reconcile(self, key, result=None, not_applied=False):
        """Explicit operator reconciliation after examining remote state; never a retry."""
        state = self.context.state()
        entry = state.get("operations", {}).get(key)
        if not entry or entry["state"] != "pending":
            raise WorkError("Only a pending operation can be reconciled.")
        if not_applied:
            del state["operations"][key]
        else:
            if not isinstance(result, dict) or not result:
                raise WorkError("Supply a remote result object or --not-applied after inspection.")
            entry.update(state="done", result=result)
        self.context.save(state)
        return {"key": key, "reconciled": True, "retry_enabled": not_applied}
