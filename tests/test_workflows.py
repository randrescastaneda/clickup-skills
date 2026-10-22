"""Offline behavioral tests; never call ClickUp or GitHub."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from clickup_skills.backends import ClickUp, StdioMCP
from clickup_skills.cli import dispatch, parser
from clickup_skills.context import Context, WorkError, git, remote_repository, write_json
from clickup_skills.mcp import response
from clickup_skills.routing import route
from clickup_skills.workflow import Workflow, sync_event
from clickup_skills.github import GitHub


def task(task_id="root", parent=None, team="100", list_id="200"):
    return {"id": task_id, "name": "Task " + task_id, "parent": parent, "team_id": team,
            "list": {"id": list_id}, "description": "", "status": {"status": "in progress"},
            "url": "https://app.clickup.com/t/" + task_id}


class FakeClickUp:
    def __init__(self):
        self.tasks = {"root": task(), "child": task("child", "root"), "other": task("other")}
        self.notes = []
        self.writes = []
        self.lose_comment_response = False

    def get(self, task_id):
        return copy.deepcopy(self.tasks[task_id])

    def comments(self, task_id):
        return [c for c in self.notes if c["task_id"] == task_id]

    def children(self, task_id):
        return [copy.deepcopy(t) for t in self.tasks.values() if t.get("parent") == task_id]

    def comment(self, task_id, text):
        self.writes.append(("comment", task_id, text))
        result = {"id": "c" + str(len(self.notes)), "text": text, "task_id": task_id}
        self.notes.append(result)
        if self.lose_comment_response:
            raise WorkError("Response lost after remote commit")
        return result

    def subtask(self, parent, title, description):
        self.writes.append(("subtask", parent, title))
        result = task("new" + str(len(self.tasks)), parent)
        result.update(name=title, description=description)
        self.tasks[result["id"]] = result
        return result

    def status(self, task_id, status):
        self.writes.append(("status", task_id, status))
        self.tasks[task_id]["status"] = {"status": status}
        return self.get(task_id)

    def close(self):
        pass


class FakeGitHub(GitHub):
    def __init__(self, context):
        super().__init__(context)
        self.artifacts = {self.url + "/pull/42": {"html_url": self.url + "/pull/42",
                          "body": "Reviewer notes: preserve me", "base": {"ref": "main"}},
                          self.url + "/issues/7": {"html_url": self.url + "/issues/7", "body": "Original issue"}}
        self.notes = {}
        self.writes = []
        self.lose_issue_response = False
        self.lose_note_response = False

    def request(self, endpoint, payload=None, method="POST"):
        if endpoint == self.api:
            return {"html_url": self.url}
        if endpoint == self.api + "/issues" and payload is not None:
            url = self.url + "/issues/" + str(100 + len(self.artifacts))
            self.artifacts[url] = {"html_url": url, "body": payload["body"]}
            self.writes.append(("create", url))
            if self.lose_issue_response:
                raise WorkError("Issue response lost")
            return {"html_url": url}
        suffix = endpoint.removeprefix(self.api).replace("/pulls/", "/pull/")
        url = self.url + suffix
        if payload is not None:
            self.artifacts[url]["body"] = payload["body"]
            self.writes.append(("body", url))
        return copy.deepcopy(self.artifacts[url])

    def pages(self, endpoint):
        return [dict(copy.deepcopy(x), number=int(url.rsplit("/", 1)[1]))
                for url, x in self.artifacts.items() if "/issues/" in url]

    def comments(self, target):
        return copy.deepcopy(self.notes.get(target["url"], []))

    def comment(self, target, text):
        notes = self.notes.setdefault(target["url"], [])
        note = {"id": "comment:" + str(len(notes)), "url": target["url"] + "#issuecomment-" + str(len(notes)),
                "text": text, "author": "agent"}
        notes.append(note)
        self.writes.append(("comment", target["url"]))
        if self.lose_note_response:
            raise WorkError("GitHub comment response lost")
        return copy.deepcopy(note)


class BoundTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)], check=True)
        git(self.root, "remote", "add", "origin", "https://github.com/acme/analysis.git")
        args = parser().parse_args(["--project-dir", str(self.root), "init", "--name", "Analysis",
                                   "--objective", "Verify the data", "--workspace", "100", "--list", "200",
                                   "--task", "root", "--repository", "acme/analysis"])
        dispatch(args)
        config = json.loads((self.root / ".clickup/project.json").read_text(encoding="utf-8"))
        config["github"]["status_map"] = {"in_progress": "in progress", "review": "in review", "done": "complete"}
        write_json(self.root / ".clickup/project.json", config)
        self.ctx = Context(self.root)
        self.backend = FakeClickUp()
        self.github = FakeGitHub(self.ctx)
        self.work = Workflow(self.ctx, self.backend, self.github)

    def tearDown(self):
        self.tmp.cleanup()

    def test_scope_rejects_unrelated_task_without_writes(self):
        with self.assertRaisesRegex(WorkError, "outside"):
            self.work.progress("Oops", "wrong-parent", "other")
        self.assertFalse(self.backend.writes)

    def test_scope_requires_workspace_list_and_exact_identity(self):
        for mutate in (lambda x: x.update(team_id="999"),
                       lambda x: x.update(list={"id": "999"}),
                       lambda x: x.update(id="different"),
                       lambda x: x.pop("team_id")):
            self.backend.tasks["child"] = task("child", "root")
            mutate(self.backend.tasks["child"])
            with self.assertRaises(WorkError):
                self.work.progress("No", "scope", "child")
        self.assertFalse(self.backend.writes)

    def test_scope_cycle(self):
        self.backend.tasks["child"]["parent"] = "child"
        with self.assertRaisesRegex(WorkError, "cycle"):
            self.work.task("child")

    def test_origin_change_is_rejected(self):
        git(self.root, "remote", "set-url", "origin", "git@github.com:acme/other.git")
        with self.assertRaisesRegex(WorkError, "Origin differs"):
            Context(self.root)

    def test_existing_binding_is_not_overwritten(self):
        args = parser().parse_args(["--project-dir", str(self.root), "init", "--name", "X",
                                   "--objective", "X", "--workspace", "100", "--list", "200",
                                   "--task", "root", "--repository", "acme/analysis"])
        with self.assertRaisesRegex(WorkError, "already exists"):
            dispatch(args)

    def test_local_lock_prevents_concurrent_writer(self):
        with self.ctx.locked():
            with self.assertRaisesRegex(WorkError, "write.lock"):
                with self.ctx.locked():
                    self.fail("Acquired duplicate lock")

    def test_comment_is_repeatable_and_key_cannot_change_payload(self):
        self.work.progress("Verified\n`literal`", "test-v1", "child")
        second = self.work.progress("Verified\n`literal`", "test-v1", "child")
        self.assertTrue(second["reused"])
        self.assertEqual(len(self.backend.writes), 1)
        with self.assertRaisesRegex(WorkError, "different inputs"):
            self.work.progress("Changed", "test-v1", "child")

    def test_uncertain_comment_recovers_from_remote_marker(self):
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.work.progress("Done tests", "lost", "child")
        self.backend.lose_comment_response = False
        result = self.work.progress("Done tests", "lost", "child")
        self.assertTrue(result["reconciled"])
        self.assertEqual(len(self.backend.writes), 1)

    def test_uncertain_outcome_without_remote_evidence_blocks_replay(self):
        with self.assertRaises(WorkError):
            self.work.once("lost", {"operation": "example"}, lambda: (_ for _ in ()).throw(WorkError("timeout")))
        with self.assertRaisesRegex(WorkError, "uncertain"):
            self.work.once("lost", {"operation": "example"}, lambda: self.fail("Replay"))

    def test_subtask_is_deduplicated_even_after_local_state_is_lost(self):
        first = self.work.subtask("Validate", "Acceptance: valid", "child:validate", "child")
        (self.ctx.local / "state.json").unlink()
        second = self.work.subtask("Validate", "Acceptance: valid", "child:validate", "child")
        self.assertTrue(second["reused"])
        self.assertEqual(first["result"]["id"], second["result"]["id"])
        self.assertEqual(sum(w[0] == "subtask" for w in self.backend.writes), 1)
        self.assertEqual(sum(w[0] == "create" for w in self.github.writes), 1)
        child = self.backend.tasks[first["result"]["id"]]
        self.assertIn(first["github"], child["description"])
        self.assertIn("CU-" + child["id"], self.github.artifacts[first["github"]]["body"])

    def test_issue_is_created_before_subtask_and_uncertain_create_is_recovered(self):
        self.github.lose_issue_response = True
        with self.assertRaisesRegex(WorkError, "response lost"):
            self.work.subtask("Validate", "Acceptance", "create", "child")
        self.assertFalse(self.backend.writes)
        self.github.lose_issue_response = False
        result = self.work.subtask("Validate", "Acceptance", "create", "child")
        self.assertIn("/issues/", result["github"])
        self.assertEqual(sum(w[0] == "create" for w in self.github.writes), 1)

    def test_changed_subtask_inputs_cannot_create_an_extra_issue(self):
        self.work.subtask("Validate", "Acceptance", "create", "child", self.github.url)
        before = list(self.github.writes)
        with self.assertRaisesRegex(WorkError, "different inputs"):
            self.work.subtask("Validate", "Acceptance", "create", "child")
        self.assertEqual(before, self.github.writes)

    def test_subtask_with_explicit_repo_or_issue_and_wrong_repo_rejection(self):
        result = self.work.subtask("Plan", "Acceptance", "plan", "child", self.github.url)
        self.assertEqual(result["github"], self.github.url)
        self.assertFalse(self.github.writes)
        before = list(self.backend.writes)
        with self.assertRaisesRegex(WorkError, "bound repository"):
            self.work.subtask("Wrong", "Acceptance", "wrong", "child", "https://github.com/other/repo/issues/7")
        self.assertEqual(before, self.backend.writes)

    def test_issue_backlink_preserves_original_and_progress_mirrors_with_recovery(self):
        url = self.github.url + "/issues/7"
        self.work.link_github(url, "link", "child")
        self.assertIn("Original issue", self.github.artifacts[url]["body"])
        self.github.lose_note_response = True
        with self.assertRaises(WorkError):
            self.work.progress("Tests passed", "progress", "child")
        self.github.lose_note_response = False
        self.work.progress("Tests passed", "progress", "child")
        self.assertEqual(len(self.github.notes[url]), 1)
        self.assertEqual(sum("Tests passed" in c["text"] for c in self.backend.notes), 1)
        self.assertIn("https://app.clickup.com/t/child", self.github.notes[url][0]["text"])

    def test_comment_sync_is_bidirectional_deduplicated_and_skips_echoes(self):
        url = self.github.url + "/pull/42"
        self.work.link_github(url, "link", "child")
        self.github.notes[url] = [{"id": "review:1", "text": "Please test edge case", "author": "reviewer", "url": url + "#pullrequestreview-1"},
                                  {"id": "review-comment:1", "text": "Inline comment", "author": "reviewer", "url": url + "#discussion_r1"}]
        self.backend.notes.append({"id": "human", "text": "Acceptance clarified", "task_id": "child", "user": "Planner"})
        self.work.sync_comments("child")
        counts = (len(self.backend.notes), len(self.github.notes[url]))
        self.work.sync_comments("child")
        self.assertEqual(counts, (len(self.backend.notes), len(self.github.notes[url])))
        (self.ctx.local / "state.json").unlink()
        self.work.sync_comments("child")
        self.assertEqual(counts, (len(self.backend.notes), len(self.github.notes[url])))
        self.assertEqual(sum("Please test edge case" in x["text"] for x in self.backend.notes), 1)
        self.assertEqual(sum("Acceptance clarified" in x["text"] for x in self.github.notes[url]), 1)
        self.assertIn("Planner", self.github.notes[url][-1]["text"])
        self.github.notes[url][0]["text"] = "Updated review"
        self.work.sync_comments("child", "to-clickup")
        self.assertEqual(len(self.backend.notes), counts[0] + 1)
        self.assertFalse(any(w[0] == "status" for w in self.backend.writes))

    def test_repository_only_task_has_links_but_no_discussion_sync(self):
        self.work.progress("Scoped update", "update", "child")
        self.assertIn("[cu-work-github:" + self.github.url + "]", self.backend.notes[0]["text"])
        with self.assertRaisesRegex(WorkError, "Link an issue or PR"):
            self.work.sync_comments("child")

    def test_host_provenance_is_reused_without_helper_receipts(self):
        url = self.github.url + "/issues/7"
        self.work.link_github(url, "link", "child")
        event = sync_event(["github", url, "comment:123", "Análisis"])
        self.github.notes[url] = [{"id": "comment:123", "text": "Análisis", "url": url + "#issuecomment-123"}]
        self.backend.notes.append({"id": "host", "task_id": "child", "text": "Host snapshot\n[cu-work-sync:" + event + "]"})
        before = len(self.backend.notes)
        self.work.sync_comments("child", "to-clickup")
        self.assertEqual(before, len(self.backend.notes))

    def test_subtask_backlink_failure_resumes_existing_child_and_issue(self):
        with patch.object(self.work, "_artifact_backlink", side_effect=WorkError("Backlink unavailable")):
            with self.assertRaises(WorkError):
                self.work.subtask("Validate", "Acceptance", "create", "child")
        self.work.subtask("Validate", "Acceptance", "create", "child")
        self.assertEqual(sum(w[0] == "subtask" for w in self.backend.writes), 1)
        self.assertEqual(sum(w[0] == "create" for w in self.github.writes), 1)

    def test_github_discussions_read_all_pages_and_review_types(self):
        github = GitHub(self.ctx)
        with patch("clickup_skills.github.execute", return_value=[[{"id": 1}], [{"id": 2}]]) as run:
            self.assertEqual(github.pages("repos/acme/analysis/issues?per_page=100"), [{"id": 1}, {"id": 2}])
            self.assertEqual(run.call_args.args[0][-2:], ["--paginate", "--slurp"])
            self.assertEqual(run.call_args.args[0][2:4], ["--hostname", "github.com"])
        target = {"kind": "pull", "number": 42, "url": github.url + "/pull/42"}
        with patch.object(github, "pages", side_effect=[[{"id": 1, "body": "Conversation", "html_url": target["url"] + "#issuecomment-1"}],
                                                       [{"id": 1, "body": "Inline", "html_url": target["url"] + "#discussion_r1"}],
                                                       [{"id": 1, "body": "Review", "html_url": target["url"] + "#pullrequestreview-1"}]]) as pages:
            notes = github.comments(target)
            self.assertEqual({n["id"] for n in notes}, {"comment:1", "review-comment:1", "review:1"})
            self.assertEqual(pages.call_count, 3)

    def test_full_comment_page_blocks_incomplete_reconciliation(self):
        backend = ClickUp(self.ctx)
        with patch("clickup_skills.backends.execute", return_value=[{"id": str(i)} for i in range(25)]):
            with self.assertRaisesRegex(WorkError, "truncated"):
                backend.comments("child")

    def pr_data(self):
        return {"url": "https://github.com/acme/analysis/pull/42", "body": "Reviewer notes: preserve me",
                "state": "OPEN", "headRefOid": "abc", "baseRefName": "main", "isDraft": False,
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}]}

    def test_pr_link_preserves_body_and_does_not_change_status(self):
        self.work.link_pr(42, "link", "child")
        self.work.link_pr(42, "link", "child")
        pr = self.github.artifacts[self.github.url + "/pull/42"]
        self.assertIn("Reviewer notes: preserve me", pr["body"])
        self.assertEqual(pr["body"].count("<!-- clickup-skills:child -->"), 1)
        self.assertEqual(sum(w[0] == "comment" for w in self.backend.writes), 1)
        self.assertFalse(any(w[0] == "status" for w in self.backend.writes))

    def test_partial_link_resumes_only_missing_side(self):
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.work.link_pr(42, "link", "child")
        self.backend.lose_comment_response = False
        self.work.link_pr(42, "link", "child")
        self.assertEqual(sum(w[0] == "body" for w in self.github.writes), 1)
        self.assertEqual(len(self.backend.notes), 1)

    def test_completion_blocks_open_failed_missing_checks_and_unlinked_pr(self):
        base = self.pr_data()
        base.update(state="MERGED", body="<!-- clickup-skills:child -->")
        cases = [dict(base, state="OPEN"), dict(base, body="No link"),
                 dict(base, statusCheckRollup=[]),
                 dict(base, statusCheckRollup=[{"status": "IN_PROGRESS"}]),
                 dict(base, statusCheckRollup=[{"status": "COMPLETED", "conclusion": "FAILURE"}])]
        for pr in cases:
            with patch.object(self.work, "pr", return_value=pr):
                with self.assertRaises(WorkError):
                    self.work.phase("done", "done", "child", 42, "Unit tests passed")
        self.assertFalse(self.backend.writes)

    def test_completion_records_verified_head_and_then_sets_status(self):
        pr = self.pr_data()
        pr.update(state="MERGED", body="<!-- clickup-skills:child -->")
        with patch.object(self.work, "pr", return_value=pr):
            self.work.phase("done", "done", "child", 42, "Acceptance criteria checked; 10 unit tests passed")
        self.assertEqual(self.backend.writes[-1], ("status", "child", "complete"))
        self.assertIn("Head: abc", self.backend.notes[0]["text"])

    def test_wrong_repository_and_base_pr_are_rejected(self):
        for data in (dict(self.pr_data(), url="https://github.com/evil/project/pull/42"),
                     dict(self.pr_data(), baseRefName="release")):
            with patch("clickup_skills.workflow.execute", return_value=data):
                with self.assertRaises(WorkError):
                    self.work.pr(42)

    def test_cup_argv_preserves_text_and_explicit_parent(self):
        backend = ClickUp(self.ctx)
        seen = []
        def run(argv, cwd=None):
            seen.append(argv)
            self.assertEqual(Path(argv[-1]).read_text(encoding="utf-8"), "Text `code`\nteam's $value")
            return {"id": "new"}
        with patch("clickup_skills.backends.execute", run):
            backend.subtask("child", "A; $(unsafe)", "Text `code`\nteam's $value")
        self.assertEqual(seen[0][:3], ["cup", "--json", "create"])
        self.assertIn("--parent", seen[0])
        self.assertNotIn("-p", seen[0])
        self.assertIn("A; $(unsafe)", seen[0])

    def test_rest_mcp_adapter_uses_upstream_contract(self):
        backend = ClickUp(self.ctx)
        backend.runtime = "rest-mcp"
        with patch.object(backend.mcp, "call", return_value={"id": "new"}) as rpc:
            backend.subtask("child", "Title", "Description")
            rpc.assert_called_once_with("create_task", {"list_id": "200", "parent": "child",
                                                       "name": "Title", "description": "Description"})

    def test_malformed_backend_reads_do_not_pass_scope_or_reconciliation(self):
        backend = ClickUp(self.ctx)
        with patch("clickup_skills.backends.execute", return_value=[]):
            with self.assertRaisesRegex(WorkError, "Scope cannot"):
                backend.get("root")
        with patch("clickup_skills.backends.execute", return_value={"truncated": True}):
            with self.assertRaisesRegex(WorkError, "marker cannot"):
                backend.comments("root")

    def test_unicode_binding_state_and_progress_file(self):
        text = "Análisis de pobreza 数据"
        config = copy.deepcopy(self.ctx.config)
        config["objective"] = text
        (self.root / ".clickup/project.json").write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
        context = Context(self.root)
        self.assertEqual(context.config["objective"], text)
        context.save({"note": text})
        self.assertEqual(context.state()["note"], text)
        path = self.root / "progress.md"
        path.write_text(text, encoding="utf-8")
        args = parser().parse_args(["--project-dir", str(self.root), "progress", "--task", "child",
                                   "--key", "unicode", "--message-file", str(path)])
        with patch("clickup_skills.cli.Workflow", return_value=self.work):
            dispatch(args)
        self.assertIn(text, self.backend.notes[0]["text"])


class RoutingProtocolTest(unittest.TestCase):
    def test_routes_compact_cli_and_richer_mcp(self):
        self.assertEqual(route("task.subtask", ["cup", "official"])["backend"], "cup")
        self.assertEqual(route("task.context", ["cup", "context-mcp"])["backend"], "context-mcp")
        self.assertEqual(route("task.status", ["official"])["backend"], "official")
        self.assertEqual(route("github.pr", ["github-mcp"])["backend"], "github-mcp")
        with self.assertRaises(WorkError):
            route("task.custom-field", ["context-mcp"])

    def test_routing_override_is_respected(self):
        config = {"routing": {"overrides": {"task.get": ["rest-mcp", "cup"]}}}
        self.assertEqual(route("task.get", ["cup", "rest-mcp"], config)["backend"], "rest-mcp")

    def test_remote_repository_formats(self):
        for url in ("git@github.com:acme/project.git", "https://github.com/acme/project.git",
                    "ssh://git@github.com/acme/project.git"):
            self.assertEqual(remote_repository(url), "acme/project")
        with self.assertRaises(WorkError):
            remote_repository("https://token@github.com/acme/project.git")

    def test_mcp_negotiation_and_invalid_inputs(self):
        init = response({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertIn("tools", init["result"]["capabilities"])
        self.assertIsNone(response({"jsonrpc": "2.0", "method": "notifications/initialized"}))
        tools = response({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(tools["result"]["tools"]), 9)
        for args in (None, {}, {"project_dir": "."}, {"project_dir": 3}):
            result = response({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                               "params": {"name": "get_bound_task", "arguments": args}})
            self.assertTrue(result["result"]["isError"])
        result = response({"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": None})
        self.assertTrue(result["result"]["isError"])

    def test_own_mcp_as_real_stdio_process(self):
        wire = '\n'.join(json.dumps(m) for m in [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}]) + '\n'
        process = subprocess.run([sys.executable, "-m", "clickup_skills.cli", "mcp"],
                                 input=wire, text=True, encoding="utf-8", capture_output=True, check=True)
        results = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual([r["id"] for r in results], [1, 2])
        self.assertEqual(process.stderr, "")

    def test_rest_mcp_client_with_real_fake_server(self):
        fixture = Path(__file__).parent / "fixtures/fake_rest_mcp.py"
        original = subprocess.Popen
        def launch(argv, **kwargs):
            return original([sys.executable, str(fixture)], **kwargs)
        client = StdioMCP()
        try:
            with patch("clickup_skills.backends.subprocess.Popen", launch):
                result = client.call("get_task", {"task_id": "root", "include_subtasks": False})
                self.assertEqual(result["id"], "root")
                with self.assertRaises(WorkError):
                    client.call("not_exposed", {})
        finally:
            client.close()


if __name__ == "__main__":
    unittest.main()
