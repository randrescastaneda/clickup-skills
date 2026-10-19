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
from clickup_skills.workflow import Workflow


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
        config = json.loads((self.root / ".clickup/project.json").read_text())
        config["github"]["status_map"] = {"in_progress": "in progress", "review": "in review", "done": "complete"}
        write_json(self.root / ".clickup/project.json", config)
        self.ctx = Context(self.root)
        self.backend = FakeClickUp()
        self.work = Workflow(self.ctx, self.backend)

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
        self.assertEqual(len(self.backend.writes), 1)

    def pr_data(self):
        return {"url": "https://github.com/acme/analysis/pull/42", "body": "Reviewer notes: preserve me",
                "state": "OPEN", "headRefOid": "abc", "baseRefName": "main", "isDraft": False,
                "statusCheckRollup": [{"status": "COMPLETED", "conclusion": "SUCCESS"}]}

    def test_pr_link_preserves_body_and_does_not_change_status(self):
        pr = self.pr_data()
        def gh(argv, cwd=None):
            if "PATCH" in argv:
                payload = json.loads(Path(argv[argv.index("--input") + 1]).read_text())
                pr["body"] = payload["body"]
                return pr
            return copy.deepcopy(pr)
        with patch("clickup_skills.workflow.execute", gh):
            self.work.link_pr(42, "link", "child")
            self.work.link_pr(42, "link", "child")
        self.assertIn("Reviewer notes: preserve me", pr["body"])
        self.assertEqual(pr["body"].count("<!-- clickup-skills:child -->"), 1)
        self.assertEqual(sum(w[0] == "comment" for w in self.backend.writes), 1)
        self.assertFalse(any(w[0] == "status" for w in self.backend.writes))

    def test_partial_link_resumes_only_missing_side(self):
        pr = self.pr_data()
        patches = []
        def gh(argv, cwd=None):
            if "PATCH" in argv:
                patches.append(argv)
                pr["body"] = json.loads(Path(argv[-1]).read_text())["body"]
            return copy.deepcopy(pr)
        self.backend.lose_comment_response = True
        with patch("clickup_skills.workflow.execute", gh):
            with self.assertRaises(WorkError):
                self.work.link_pr(42, "link", "child")
            self.backend.lose_comment_response = False
            self.work.link_pr(42, "link", "child")
        self.assertEqual(len(patches), 1)
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
            self.assertEqual(Path(argv[-1]).read_text(), "Text `code`\nteam's $value")
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
        self.assertEqual(len(tools["result"]["tools"]), 7)
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
                                 input=wire, text=True, capture_output=True, check=True)
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
