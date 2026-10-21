"""Worker scope, preflight, crash recovery and repeat polling without service writes."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from clickup_skills.context import Context, WorkError, git, process_lock, write_json
from clickup_skills.github import GitHub
from clickup_skills.worker import run_worker
from clickup_skills.workflow import Workflow, marker, sync_event
import test_workflows as fixtures


class WorkerTests(unittest.TestCase):
    def setUp(self):
        fixtures.BoundTest.setUp(self)
        self.url = self.github.url + "/pull/42"
        self.work.link_github(self.url, "link", "child")
        self.github.notes[self.url] = [{"id": "review-comment:9", "text": "Test the missing value case",
                                       "author": "reviewer", "url": self.url + "#discussion_r9"}]
        self.backend.writes.clear()
        self.github.writes.clear()

    def tearDown(self):
        fixtures.BoundTest.tearDown(self)

    def run_worker(self, tasks=None, **kwargs):
        return run_worker(self.root, tasks or ["child"],
                          workflow_factory=lambda ctx: Workflow(ctx, self.backend, self.github), **kwargs)

    def test_preview_reads_without_remote_writes_receipts_or_body_output(self):
        before = self.ctx.state()
        report = self.run_worker()
        self.assertEqual(report["status"], "preview")
        self.assertEqual(report["planned_writes"], 1)
        self.assertEqual(before, self.ctx.state())
        self.assertFalse(self.backend.writes or self.github.writes)
        self.assertNotIn("missing value", json.dumps(report))
        self.assertFalse((self.ctx.local / "worker-status.json").exists())

    def test_apply_restart_and_source_edit_keep_one_mirror_per_revision(self):
        self.run_worker(apply=True)
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)
        (self.ctx.local / "state.json").unlink()
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)
        self.github.notes[self.url][0]["text"] = "Updated: test NA and NaN"
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 2)
        self.assertNotIn("Updated:", (self.ctx.local / "worker-status.json").read_text())
        self.assertTrue(all(write[0] == "comment" for write in self.backend.writes))

    def test_shared_pr_imports_to_each_scoped_task_without_receipt_collision(self):
        self.backend.tasks["second"] = fixtures.task("second", "root")
        self.work.link_github(self.url, "link-second", "second")
        self.backend.writes.clear()
        self.run_worker(["child", "second"], apply=True)
        self.assertEqual({write[1] for write in self.backend.writes}, {"child", "second"})
        self.run_worker(["child", "second"], apply=True)
        self.assertEqual(len(self.backend.writes), 2)

    def test_legacy_pending_receipt_recovers_from_remote_marker(self):
        plan = self.work.plan_comments("child")
        op = plan["operations"][0]
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.work._comment(op["text"], op["event"], "child", op["event"])
        self.backend.lose_comment_response = False
        self.run_worker(apply=True)
        self.assertEqual(self.ctx.state()["operations"][op["event"]]["state"], "done")
        self.assertEqual(len(self.backend.writes), 1)

    def test_lost_clickup_response_is_recovered_without_duplicate(self):
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.run_worker(apply=True)
        self.assertEqual(json.loads((self.ctx.local / "worker-status.json").read_text())["status"], "blocked")
        self.backend.lose_comment_response = False
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)

    def test_missing_remote_evidence_blocks_replay_before_any_other_task_writes(self):
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.run_worker(apply=True)
        self.backend.lose_comment_response = False
        self.backend.notes = [c for c in self.backend.notes if "[cu-work-sync:" not in c.get("text", "")]
        before = len(self.backend.writes)
        with self.assertRaisesRegex(WorkError, "uncertain"):
            self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), before)

    def test_lost_github_response_is_recovered_without_duplicate(self):
        self.backend.notes.append({"id": "human", "task_id": "child", "text": "Acceptance note"})
        self.github.lose_note_response = True
        with self.assertRaises(WorkError):
            self.run_worker(direction="to-github", apply=True)
        self.github.lose_note_response = False
        self.run_worker(direction="to-github", apply=True)
        self.assertEqual(len(self.github.writes), 1)

    def test_budget_and_second_task_scope_are_checked_before_first_write(self):
        self.backend.notes.append({"id": "human", "task_id": "child", "text": "Acceptance note"})
        with self.assertRaisesRegex(WorkError, "max-writes"):
            self.run_worker(apply=True, max_writes=1)
        with self.assertRaisesRegex(WorkError, "outside"):
            self.run_worker(["child", "other"], apply=True)
        self.assertFalse(self.backend.writes or self.github.writes)

    def test_long_history_boundary_is_checked_before_write(self):
        self.backend.notes.extend({"id": str(i), "task_id": "child", "text": "[cu-work:fixture]"} for i in range(23))
        with self.assertRaisesRegex(WorkError, "25-comment"):
            self.run_worker(apply=True)
        self.assertFalse(self.backend.writes or self.github.writes)

    def test_complete_reader_supports_long_histories_without_bypassing_scope(self):
        self.backend.complete_comment_history = True
        self.backend.notes.extend({"id": str(i), "task_id": "child", "text": "[cu-work:fixture]"} for i in range(40))
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)
        with self.assertRaisesRegex(WorkError, "outside"):
            self.run_worker(["other"], apply=True)

    def test_enabling_complete_reader_reuses_remote_provenance_after_binding_change(self):
        self.run_worker(apply=True)
        config = self.ctx.config
        config["routing"]["comment_reader"] = "clickup-api"
        write_json(self.root / ".clickup/project.json", config)
        self.backend.complete_comment_history = True
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)

    def test_binding_change_cannot_bypass_uncertain_old_sync_receipt(self):
        self.backend.lose_comment_response = True
        with self.assertRaises(WorkError):
            self.run_worker(apply=True)
        self.backend.lose_comment_response = False
        self.backend.notes = [n for n in self.backend.notes if "[cu-work-sync:" not in n.get("text", "")]
        config = self.ctx.config
        config["routing"]["comment_reader"] = "clickup-api"
        write_json(self.root / ".clickup/project.json", config)
        self.backend.complete_comment_history = True
        with self.assertRaisesRegex(WorkError, "uncertain"):
            self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)

    def test_last_target_read_failure_cannot_partially_mirror_earlier_target(self):
        self.work.link_github(self.github.url + "/issues/7", "issue-link", "child")
        self.backend.writes.clear()
        self.github.writes.clear()
        original = self.github.comments
        def comments(target):
            if target["kind"] == "pull":
                raise WorkError("Read failed")
            return original(target)
        self.github.notes[self.github.url + "/issues/7"] = [{"id": "comment:1", "text": "First source",
                                                              "url": self.github.url + "/issues/7#issuecomment-1"}]
        with patch.object(self.github, "comments", side_effect=comments):
            with self.assertRaisesRegex(WorkError, "Read failed"):
                self.run_worker(apply=True)
        self.assertFalse(self.backend.writes or self.github.writes)

    def test_malformed_or_duplicate_destination_identity_stops_before_writes(self):
        self.github.notes[self.url][0]["url"] = "https://github.com/other/repo/pull/1"
        with self.assertRaisesRegex(WorkError, "malformed"):
            self.run_worker(apply=True)
        self.assertFalse(self.backend.writes or self.github.writes)

    def test_duplicate_source_events_do_not_duplicate_new_writes(self):
        self.github.notes[self.url].append(copy.deepcopy(self.github.notes[self.url][0]))
        self.run_worker(apply=True)
        self.assertEqual(len(self.backend.writes), 1)

    def test_watch_reloads_binding_and_stops_if_scope_changes(self):
        def change_binding(_seconds):
            config = self.ctx.config
            config["objective"] = "Different scope"
            write_json(self.root / ".clickup/project.json", config)
        with self.assertRaisesRegex(WorkError, "binding changed"):
            self.run_worker(apply=True, watch=True, wait=change_binding)
        self.assertEqual(len(self.backend.writes), 1)

    def test_watch_releases_write_lock_between_passes_and_stops_cleanly(self):
        def stop(_seconds):
            with self.ctx.locked():
                pass
            raise KeyboardInterrupt
        report = self.run_worker(apply=True, watch=True, wait=stop)
        self.assertEqual(report["status"], "stopped")
        self.assertEqual(report["passes"], 1)
        # Worker ownership is released too.
        with process_lock(self.ctx.shared / "worker.lock.guard"):
            pass

    def test_worker_options_require_explicit_tasks_and_bounded_interval(self):
        for kwargs in ({"tasks": []}, {"interval": 0}, {"interval": True}, {"max_writes": 101}, {"watch": True}):
            with self.assertRaises(WorkError):
                run_worker(self.root, **({"tasks": ["child"]} | kwargs))

    def test_single_worker_owner_prevents_competing_pass(self):
        with process_lock(self.ctx.shared / "worker.lock.guard"):
            with self.assertRaisesRegex(WorkError, "worker.lock"):
                self.run_worker(apply=True)
        self.assertFalse(self.backend.writes or self.github.writes)

    def test_process_exit_releases_lock_and_linked_worktrees_share_lock(self):
        git(self.root, "add", ".")
        git(self.root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.test", "commit", "-qm", "Fixture")
        linked = self.root / "linked"
        git(self.root, "worktree", "add", "-q", "--detach", str(linked))
        other = Context(linked)
        self.assertEqual(self.ctx.shared.resolve(), other.shared.resolve())
        with self.ctx.locked():
            with self.assertRaisesRegex(WorkError, "write.lock"):
                with other.locked():
                    self.fail("Competing writer")
        script = "from clickup_skills.context import Context; import sys; c=Context(sys.argv[1]);\nwith c.locked():\n print('ready',flush=True); sys.stdin.read()"
        child = subprocess.Popen([sys.executable, "-c", script, str(self.root)], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "ready")
            with self.assertRaises(WorkError):
                with self.ctx.locked():
                    self.fail("Competing process")
            child.kill()
            child.communicate(timeout=10)
            with self.ctx.locked():
                pass
        finally:
            if child.poll() is None:
                child.kill()
            child.communicate()

    def test_plain_issue_comment_uses_exact_bound_endpoint_and_file_input(self):
        github = GitHub(self.ctx)
        target = {"kind": "issue", "number": 7}
        def execute(argv, cwd):
            self.assertEqual(argv[:5], ["gh", "api", "--hostname", "github.com", "repos/acme/analysis/issues/7/comments"])
            self.assertEqual(json.loads(Path(argv[-1]).read_text())["body"], "Literal `text`\n$(never execute)")
            return {"id": 99, "html_url": self.github.url + "/issues/7#issuecomment-99"}
        with patch("clickup_skills.github.execute", side_effect=execute):
            self.assertEqual(github.comment(target, "Literal `text`\n$(never execute)")["id"], 99)

    def test_pagination_cannot_treat_malformed_records_as_absence(self):
        with patch("clickup_skills.github.execute", return_value=[[None]]):
            with self.assertRaisesRegex(WorkError, "pagination"):
                GitHub(self.ctx).pages("repos/acme/analysis/issues/7/comments")
        with patch.object(GitHub, "pages", return_value=[{"body": "Missing identity"}]):
            with self.assertRaisesRegex(WorkError, "identity"):
                GitHub(self.ctx).comments({"kind": "issue", "number": 7, "url": self.github.url + "/issues/7"})

    def test_inline_reply_is_imported_and_unsubmitted_review_is_ignored(self):
        inline = {"id": 10, "body": "Reply in the review thread", "in_reply_to_id": 9,
                  "html_url": self.url + "#discussion_r10"}
        pending = {"id": 11, "body": "Private draft review", "state": "PENDING",
                   "html_url": self.url + "#pullrequestreview-11"}
        with patch.object(GitHub, "pages", side_effect=[[], [inline], [pending]]):
            notes = GitHub(self.ctx).comments({"kind": "pull", "number": 42, "url": self.url})
        self.assertEqual([n["id"] for n in notes], ["review-comment:10"])
        self.assertEqual(notes[0]["url"], inline["html_url"])


if __name__ == "__main__":
    unittest.main()
