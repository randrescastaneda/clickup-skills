"""Scoped writes, resumable operation receipts, and ClickUp/GitHub linkage."""

import hashlib
import json
import re

from .backends import ClickUp, execute
from .context import WorkError, identifier
from .github import GitHub


def marker(key):
    return "cu-work:" + hashlib.sha256(key.encode()).hexdigest()[:24]


def sync_event(parts):
    encoded = json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "sync:" + hashlib.sha256(encoded).hexdigest()[:32]


class Workflow:
    def __init__(self, context, backend=None, github=None):
        self.context = context
        self.backend = backend or ClickUp(context)
        self.github = github or GitHub(context)

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

    def associations(self, task, comments=None):
        """Remote association markers survive a new teammate checkout or lost receipts."""
        comments = self.backend.comments(str(task["id"])) if comments is None else comments
        texts = [task.get("text_content") or task.get("description") or task.get("markdown_description") or ""]
        texts += [c.get("comment_text", c.get("text", "")) for c in comments]
        urls = set(re.findall(r"\[cu-work-github:(https://github\.com/[^\s\]]+)\]", "\n".join(texts)))
        # A repository-only task is valid, but has no issue/PR discussion to mirror.
        if not urls:
            return [{"kind": "repository", "url": self.github.url, "number": None}]
        return [self.github.target(url) for url in sorted(urls)]

    def linked_text(self, text, task_id, targets):
        return (text.rstrip() + "\n\nClickUp: https://app.clickup.com/t/" + task_id +
                "\nRepository: " + self.github.url + "\n" +
                "\n".join("[cu-work-github:" + t["url"] + "]" for t in targets))

    def _comment(self, text, key, task_id, provenance=None):
        """One ClickUp write; callers supply links and choose whether to mirror."""
        token = marker(self.context.fingerprint + task_id + key)
        body = text.rstrip() + "\n\n[" + token + "]"
        def recover():
            comments = self.backend.comments(task_id)
            hits = [c for c in comments if token in str(c.get("comment_text", c.get("text", ""))) or
                    (provenance and "[cu-work-sync:" + provenance + "]" in str(c.get("comment_text", c.get("text", ""))))]
            if len(hits) > 1:
                raise WorkError("Multiple remote comments match this operation; inspect them.")
            return {"id": hits[0].get("id"), "task_id": task_id} if hits else None
        return self.once(key, {"operation": "comment", "task_id": task_id, "body": body},
                         lambda: self.backend.comment(task_id, body), recover)

    def _github_comment(self, target, text, key, task_id, comments=None, provenance=None):
        token = marker(self.context.fingerprint + task_id + key)
        body = text.rstrip() + "\n\n[" + token + "]"
        def recover():
            notes = self.github.comments(target) if comments is None else comments
            hits = [c for c in notes if token in c.get("text", "") or
                    (provenance and "[cu-work-sync:" + provenance + "]" in c.get("text", ""))]
            if len(hits) > 1:
                raise WorkError("Multiple GitHub comments match this operation; inspect them.")
            return {"id": hits[0].get("id"), "url": hits[0].get("url")} if hits else None
        return self.once(key, {"operation": "github-comment", "task_id": task_id,
                               "target": target["url"], "body": body},
                         lambda: self.github.comment(target, body), recover)

    def progress(self, text, key, task_id=None):
        if not text.strip():
            raise WorkError("Progress text must not be empty.")
        task = self.task(task_id)
        task_id = str(task["id"])
        targets = self.associations(task)
        body = self.linked_text(text, task_id, targets)
        clickup = self._comment(body, key, task_id)
        mirrored = []
        for target in targets:
            if target["kind"] != "repository":
                mirror_key = marker(key + target["url"]) + ":github"
                mirrored.append(self._github_comment(target, body, mirror_key, task_id))
        return {**clickup, "github": mirrored}

    def subtask(self, title, description, key, task_id=None, github_target=None):
        if not title.strip():
            raise WorkError("Subtask title must not be empty.")
        parent = self.task(task_id)
        parent_id = str(parent["id"])
        self.once(key + ":intent", {"operation": "subtask-intent", "task_id": parent_id,
                                    "title": title, "description": description, "target": github_target},
                  lambda: {"accepted": True})
        token = marker(self.context.fingerprint + parent_id + key)
        # Create the GitHub target first: a ClickUp subtask can never be born unlinked.
        target = self.resolve_target(github_target or "new-issue", title, description,
                                     key + ":issue", parent_id)
        body = self.linked_text(description, parent_id, [target]) + "\n\n[" + token + "]"
        def recover():
            children = self.backend.children(parent_id)
            hits = []
            for child in children:
                full = self.context.scoped(str(child["id"]), self.backend.get)
                if token in str(full.get("description", "")) + str(full.get("text_content", "")) + str(full.get("markdown_description", "")):
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
        created = self.once(key, {"operation": "subtask", "task_id": parent_id, "title": title, "body": body},
                            create, recover)
        child_id = str(created["result"]["id"])
        backlink = self.link_github(target["url"], marker(key) + ":backlink", child_id)
        return {**created, "github": target["url"], "backlink": backlink}

    def resolve_target(self, url, title, description, key, task_id):
        if url != "new-issue":
            return self.github.target(url)
        if not title or not title.strip():
            raise WorkError("Creating a GitHub issue requires a non-empty title.")
        token = marker(self.context.fingerprint + task_id + key)
        body = (description.rstrip() + "\n\nClickUp parent: https://app.clickup.com/t/" + task_id +
                "\nRepository: " + self.github.url + "\n\n[" + token + "]")
        result = self.once(key, {"operation": "issue-create", "task_id": task_id, "title": title, "body": body},
                           lambda: self.github.create_issue(title, body), lambda: self.github.find_issue(token))
        return self.github.target(result["result"]["url"])

    def link_github(self, url, key, task_id=None, title=None, description=""):
        task = self.task(task_id)
        task_id = str(task["id"])
        self.once(key + ":intent", {"operation": "link-intent", "task_id": task_id,
                                    "target": url, "title": title, "description": description},
                  lambda: {"accepted": True})
        target = self.resolve_target(url, title, description, key + ":issue", task_id)
        if target["kind"] != "repository":
            self._artifact_backlink(target, task_id, key + ":github")
        text = self.linked_text("GitHub association recorded. CU-" + task_id, task_id, [target])
        comment = self._comment(text, key + ":clickup", task_id)
        return {"target": target["url"], "clickup": comment, "note": "No status was changed."}

    def _artifact_backlink(self, target, task_id, key):
        start, end = "<!-- clickup-skills:" + task_id + " -->", "<!-- /clickup-skills:" + task_id + " -->"
        block = (start + "\nClickUp: https://app.clickup.com/t/" + task_id + "\nCU-" + task_id +
                 "\n\nObjective: " + self.context.config["objective"] + "\n" + end)
        body = target.get("body") or ""
        if (body.count(start) != body.count(end) or body.count(start) > 1 or
                (start in body and body.index(start) > body.index(end))):
            raise WorkError("Artifact contains malformed or duplicate managed blocks; resolve before linking.")
        updated = re.sub(re.escape(start) + r".*?" + re.escape(end), lambda _: block, body, flags=re.S) if start in body else body.rstrip() + "\n\n" + block + "\n"
        def recover():
            return {"url": target["url"]} if block in self.github.target(target["url"])["body"] else None
        def apply():
            if self.github.target(target["url"])["body"] != body:
                raise WorkError("Artifact body changed concurrently. Re-read and reconcile before retrying.")
            self.github.set_body(target, updated)
            result = recover()
            if result is None:
                raise WorkError("GitHub backlink was not verified. Reconcile before another write.")
            return result
        return self.once(key, {"operation": "artifact-body", "task_id": task_id,
                               "target": target["url"], "block": block}, apply, recover)

    def sync_comments(self, task_id=None, direction="both"):
        """Reconcile discussions during a session; never infer status or execute comment text."""
        if direction not in ("both", "to-clickup", "to-github"):
            raise WorkError("Choose both, to-clickup, or to-github.")
        task = self.task(task_id)
        task_id = str(task["id"])
        comments = self.backend.comments(task_id)
        targets = [t for t in self.associations(task, comments) if t["kind"] != "repository"]
        if not targets:
            raise WorkError("Link an issue or PR before synchronizing comments; repositories have no task discussion.")
        results = []
        for target in targets:
            notes = self.github.comments(target)
            if direction in ("both", "to-clickup"):
                for note in notes:
                    if "[cu-work:" in note["text"] or "[cu-work-sync:" in note["text"]:
                        continue
                    # Hash the content too: edited comments become explicit revisions, never overwrites.
                    event = sync_event(["github", target["url"], note["id"], note["text"]])
                    text = ("GitHub comment by " + note.get("author", "unknown") + "\nSource: " + note["url"] +
                            "\n\n" + note["text"] + "\n\n[cu-work-sync:" + event + "]")
                    results.append(self._comment(self.linked_text(text, task_id, [target]), event, task_id, event))
            if direction in ("both", "to-github"):
                for note in comments:
                    text = note.get("comment_text", note.get("text", ""))
                    if not text.strip() or "[cu-work:" in text or "[cu-work-sync:" in text:
                        continue
                    if not note.get("id"):
                        raise WorkError("ClickUp comment is missing its identity; cannot deduplicate safely.")
                    event = sync_event(["clickup", task_id, str(note["id"]), text, target["url"]])
                    source = ("ClickUp comment " + str(note["id"]) + " by " +
                              (note.get("user", {}).get("username", "unknown") if isinstance(note.get("user"), dict)
                               else str(note.get("user") or "unknown")) + "\n\n" + text +
                              "\n\n[cu-work-sync:" + event + "]")
                    results.append(self._github_comment(target, self.linked_text(source, task_id, [target]),
                                                        event, task_id, notes, event))
        return {"task_id": task_id, "direction": direction, "operations": results,
                "note": "Discussion snapshots reconciled. No status changes; no background worker installed."}

    def pr(self, number):
        if not str(number).isdigit() or int(number) < 1:
            raise WorkError("Use a positive pull request number in the bound repository.")
        repo = self.context.config["github"]["repository"]
        data = execute(["gh", "pr", "view", str(number), "--repo", "github.com/" + repo, "--json",
                        "url,body,state,headRefOid,statusCheckRollup,isDraft,baseRefName"], self.context.root)
        expected = f"https://github.com/{repo}/pull/{int(number)}"
        if data.get("url", "").lower() != expected.lower():
            raise WorkError("GitHub returned a PR from a different repository.")
        if data.get("baseRefName") != self.context.config["github"]["base_branch"]:
            raise WorkError("PR targets a different base branch from the binding.")
        return data

    def link_pr(self, number, key, task_id=None):
        if not str(number).isdigit() or int(number) < 1:
            raise WorkError("Use a positive pull request number in the bound repository.")
        return self.link_github(self.github.url + "/pull/" + str(int(number)), key, task_id)

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
