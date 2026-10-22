"""Documented ClickUp pagination, strict completeness and credential isolation."""

import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from clickup_skills.backends import ClickUp
from clickup_skills.comments import CommentReader, NoRedirect
from clickup_skills.context import WorkError, validate


def comment(number):
    return {"id": str(number), "date": str(100000 + number), "comment_text": "Note " + str(number)}


class Response(io.BytesIO):
    def getcode(self):
        return 200


class CommentReaderTests(unittest.TestCase):
    def test_multiple_pages_overlap_and_exact_full_page_termination(self):
        reader = CommentReader()
        pages = [[comment(i) for i in range(50, 25, -1)],
                 [comment(i) for i in range(26, 1, -1)], [comment(2), comment(1)]]
        with patch.object(reader, "page", side_effect=pages) as request:
            result = reader.comments("task")
        self.assertEqual([note["id"] for note in result], [str(i) for i in range(50, 0, -1)])
        self.assertEqual(request.call_args_list[1].args, ("task", ("100026", "26")))
        self.assertEqual(request.call_args_list[2].args, ("task", ("100002", "2")))
        with patch.object(reader, "page", side_effect=[pages[0], []]):
            self.assertEqual(len(reader.comments("task")), 25)

    def test_same_timestamp_comments_retain_both_cursor_fields(self):
        reader = CommentReader()
        page = [{**comment(i), "date": "100000"} for i in range(25, 0, -1)]
        with patch.object(reader, "page", side_effect=[page, [page[-1]]]) as request:
            self.assertEqual(len(reader.comments("task")), 25)
        self.assertEqual(request.call_args.args, ("task", ("100000", "1")))

    def test_stalled_full_pages_and_changed_duplicate_cannot_establish_absence(self):
        reader = CommentReader()
        page = [comment(i) for i in range(25, 0, -1)]
        with patch.object(reader, "page", side_effect=[page, page]):
            with self.assertRaisesRegex(WorkError, "advance|order"):
                reader.comments("task")
        changed = {**page[-1], "comment_text": "Edited during read"}
        with patch.object(reader, "page", side_effect=[page, [changed]]):
            with self.assertRaisesRegex(WorkError, "changed"):
                reader.comments("task")

    def test_malformed_identity_timestamp_text_or_order_blocks_history(self):
        reader = CommentReader()
        for page in ([None], [{"comment_text": "Missing id"}], [{**comment(1), "date": None}],
                     [{**comment(1), "comment_text": None}], [comment(1), comment(2)],
                     [{**comment(1), "id": True}]):
            with self.subTest(page=page), patch.object(reader, "page", return_value=page):
                with self.assertRaises(WorkError):
                    reader.comments("task")

    def test_page_is_get_only_fixed_host_and_errors_do_not_expose_credentials(self):
        reader = CommentReader()
        def open_page(request, timeout):
            self.assertEqual(request.get_method(), "GET")
            self.assertEqual(request.full_url, "https://api.clickup.com/api/v2/task/task/comment?start=100001&start_id=1")
            self.assertEqual(request.get_header("Authorization"), "private-fixture")
            self.assertIsNone(request.data)
            self.assertEqual(timeout, 30)
            return Response(json.dumps({"comments": [comment(1)]}).encode())
        with patch.dict(os.environ, {"CLICKUP_API_KEY": "private-fixture", "CLICKUP_API_KEY_FILE": ""}), \
                patch.object(reader.opener, "open", side_effect=open_page):
            self.assertEqual(reader.page("task", ("100001", "1")), [comment(1)])
        error = HTTPError("https://api.clickup.com/private-fixture", 401, "private-fixture", {}, None)
        with patch.dict(os.environ, {"CLICKUP_API_KEY": "private-fixture", "CLICKUP_API_KEY_FILE": ""}), \
                patch.object(reader.opener, "open", side_effect=error):
            with self.assertRaises(WorkError) as raised:
                reader.page("task")
        self.assertNotIn("private-fixture", str(raised.exception))

    def test_redirects_are_not_followed_with_authorization(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, "redirect", {}, "https://other.test"))

    def test_invalid_json_missing_collection_and_oversized_pages_fail_closed(self):
        reader = CommentReader()
        with patch.dict(os.environ, {"CLICKUP_API_KEY": "fixture", "CLICKUP_API_KEY_FILE": ""}):
            for payload in (b"not JSON", b'{}', b'{"comments": {}}', b" " * (8 * 1024 * 1024 + 1)):
                with patch.object(reader.opener, "open", return_value=Response(payload)):
                    with self.assertRaises(WorkError):
                        reader.page("task")

    def test_credential_file_is_explicit_and_ambiguity_is_not_silently_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "credential"
            file.write_text("file-fixture\n")
            with patch.dict(os.environ, {"CLICKUP_API_KEY": "", "CLICKUP_API_KEY_FILE": str(file)}):
                self.assertEqual(CommentReader.token(), "file-fixture")
            with patch.dict(os.environ, {"CLICKUP_API_KEY": "other", "CLICKUP_API_KEY_FILE": str(file)}):
                with self.assertRaisesRegex(WorkError, "not both"):
                    CommentReader.token()
        with patch.dict(os.environ, {"CLICKUP_API_KEY": "", "CLICKUP_API_KEY_FILE": ""}):
            with self.assertRaisesRegex(WorkError, "private"):
                CommentReader.token()

    def test_explicit_reader_is_used_for_reads_and_never_falls_back_on_error(self):
        context = SimpleNamespace(config={"routing": {"runtime": "cup", "comment_reader": "clickup-api"}})
        backend = ClickUp(context)
        with patch.object(CommentReader, "comments", return_value=[comment(1)]) as read, patch.object(backend, "cup") as cup:
            self.assertTrue(backend.complete_comment_history)
            self.assertEqual(backend.comments("task"), [comment(1)])
            read.assert_called_once_with("task")
            cup.assert_not_called()
        with patch.object(CommentReader, "comments", side_effect=WorkError("Auth failed")), patch.object(backend, "cup") as cup:
            with self.assertRaises(WorkError):
                backend.comments("task")
            cup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
