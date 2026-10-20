"""Bound GitHub artifacts and paginated discussions through gh, without a shell."""

import json
import os
import re
import tempfile

from .backends import execute
from .context import WorkError


class GitHub:
    def __init__(self, context):
        self.context = context
        self.repository = context.config["github"]["repository"]
        self.url = "https://github.com/" + self.repository
        self.api = "repos/" + self.repository

    def request(self, endpoint, payload=None, method="POST"):
        argv = ["gh", "api", "--hostname", "github.com", endpoint]
        if payload is None:
            return execute(argv, self.context.root)
        fd, path = tempfile.mkstemp(prefix="cu-work-github-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle)
            return execute(argv + ["--method", method, "--input", path], self.context.root)
        finally:
            os.unlink(path)

    def pages(self, endpoint):
        pages = execute(["gh", "api", "--hostname", "github.com", endpoint, "--paginate", "--slurp"], self.context.root)
        if not isinstance(pages, list) or any(not isinstance(p, list) for p in pages):
            raise WorkError("GitHub pagination did not return complete lists; refusing reconciliation.")
        return [item for page in pages for item in page]

    def target(self, url):
        match = re.fullmatch(r"https://github\.com/([^/]+/[^/]+)(?:/(issues|pull)/([1-9][0-9]*))?/?", url)
        if not match or match[1].lower() != self.repository.lower():
            raise WorkError("GitHub target must be the bound repository or one of its issue/PR URLs.")
        kind = {None: "repository", "issues": "issue", "pull": "pull"}[match[2]]
        number = int(match[3]) if match[3] else None
        suffix = "" if number is None else f"/{'issues' if kind == 'issue' else 'pulls'}/{number}"
        data = self.request(self.api + suffix)
        expected = self.url + ("" if number is None else f"/{match[2]}/{number}")
        if not isinstance(data, dict) or data.get("html_url", "").lower() != expected.lower():
            raise WorkError("GitHub returned a different artifact; no writes performed.")
        if kind == "issue" and data.get("pull_request"):
            raise WorkError("This issue number is a PR. Use its /pull/ URL.")
        if kind == "pull" and data.get("base", {}).get("ref") != self.context.config["github"]["base_branch"]:
            raise WorkError("PR targets a different base branch from the binding.")
        return {"kind": kind, "number": number, "url": expected, "body": data.get("body") or ""}

    def find_issue(self, token):
        hits = [x for x in self.pages(self.api + "/issues?state=all&per_page=100")
                if not x.get("pull_request") and token in (x.get("body") or "")]
        if len(hits) > 1:
            raise WorkError("Multiple issues match the operation marker; inspect before continuing.")
        return {"url": hits[0]["html_url"]} if hits else None

    def create_issue(self, title, body):
        result = self.request(self.api + "/issues", {"title": title, "body": body})
        target = self.target(result.get("html_url", ""))
        if target["kind"] != "issue":
            raise WorkError("Issue creation did not return a verified issue.")
        return {"url": target["url"]}

    def set_body(self, target, body):
        # Issues API accepts PR bodies too, but use the explicit artifact endpoint.
        segment = "pulls" if target["kind"] == "pull" else "issues"
        self.request(f"{self.api}/{segment}/{target['number']}", {"body": body}, "PATCH")

    def comments(self, target):
        if target["kind"] == "repository":
            return []
        number = target["number"]
        endpoints = [("comment", f"{self.api}/issues/{number}/comments?per_page=100")]
        if target["kind"] == "pull":
            endpoints += [("review-comment", f"{self.api}/pulls/{number}/comments?per_page=100"),
                          ("review", f"{self.api}/pulls/{number}/reviews?per_page=100")]
        result = []
        for kind, endpoint in endpoints:
            for comment in self.pages(endpoint):
                if comment.get("body") and comment.get("id"):
                    result.append({"id": f"{kind}:{comment['id']}", "text": comment["body"],
                                   "revision": comment.get("updated_at", comment.get("submitted_at", "")),
                                   "author": (comment.get("user") or {}).get("login", "unknown"),
                                   "url": comment.get("html_url", target["url"])})
        return result

    def comment(self, target, text):
        result = self.request(f"{self.api}/issues/{target['number']}/comments", {"body": text})
        if not result.get("id") or not result.get("html_url", "").startswith(self.url + "/"):
            raise WorkError("GitHub comment result is incomplete. Reconcile before another write.")
        return {"id": result.get("id"), "url": result.get("html_url"), "text": text}
