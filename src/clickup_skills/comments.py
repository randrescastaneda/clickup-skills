"""Narrow, opt-in GET-only reader for ClickUp's documented comment cursor API."""

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .context import WorkError, identifier


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # An Authorization header must never follow a service redirect.
        return None


class CommentReader:
    """Uses explicit environment credentials; never reads cup's private key store."""
    def __init__(self):
        self.opener = build_opener(NoRedirect())

    @staticmethod
    def token():
        direct, file = os.environ.get("CLICKUP_API_KEY"), os.environ.get("CLICKUP_API_KEY_FILE")
        if direct and file:
            raise WorkError("Choose CLICKUP_API_KEY or CLICKUP_API_KEY_FILE for the comment reader, not both.")
        try:
            token = Path(file).expanduser().read_text(encoding="utf-8").strip() if file else (direct or "").strip()
        except (OSError, UnicodeError) as exc:
            raise WorkError("Cannot read the private ClickUp comment-reader credential file.") from exc
        if not token or any(c.isspace() for c in token):
            raise WorkError("Set a valid private CLICKUP_API_KEY or CLICKUP_API_KEY_FILE for the comment reader.")
        return token

    def page(self, task_id, cursor=None):
        url = "https://api.clickup.com/api/v2/task/" + identifier(task_id) + "/comment"
        if cursor:
            url += "?" + urlencode({"start": cursor[0], "start_id": cursor[1]})
        request = Request(url, headers={"Authorization": self.token(), "Accept": "application/json"}, method="GET")
        try:
            with self.opener.open(request, timeout=30) as response:
                if response.getcode() != 200:
                    raise WorkError("ClickUp comment read did not succeed; no automatic fallback.")
                raw = response.read(8 * 1024 * 1024 + 1)
            if len(raw) > 8 * 1024 * 1024:
                raise WorkError("ClickUp comment page exceeds the read limit; refusing incomplete history.")
            data = json.loads(raw)
        except (HTTPError, URLError, OSError, ValueError, UnicodeError) as exc:
            # Service errors can contain credentials/content. Never interpolate them.
            raise WorkError("ClickUp comment read failed. Check authentication and service limits; no automatic fallback.") from exc
        page = data.get("comments") if isinstance(data, dict) else None
        if not isinstance(page, list):
            raise WorkError("ClickUp returned an invalid comment page; refusing incomplete history.")
        return page

    def comments(self, task_id):
        result, seen, cursors = [], {}, set()
        cursor = None
        for _ in range(1000):
            page = self.page(task_id, cursor)
            dates, added = [], 0
            for note in page:
                if not isinstance(note, dict) or isinstance(note.get("id"), bool) or not isinstance(note.get("id"), (str, int)) or not str(note["id"]):
                    raise WorkError("ClickUp comment is missing its identity; refusing incomplete history.")
                date = note.get("date")
                if isinstance(date, bool) or not isinstance(date, (str, int)) or not str(date).isdigit():
                    raise WorkError("ClickUp comment is missing its pagination timestamp.")
                if not isinstance(note.get("comment_text"), str):
                    raise WorkError("ClickUp comment text is malformed; refusing incomplete history.")
                dates.append(int(date))
                note = {**note, "id": str(note["id"])}
                identity = note["id"]
                if identity in seen:
                    if seen[identity] != note:
                        raise WorkError("ClickUp comments changed during pagination. Restart the read before writes.")
                    continue
                seen[identity] = note
                result.append(note)
                added += 1
            if dates != sorted(dates, reverse=True) or (cursor and dates and dates[0] > int(cursor[0])):
                raise WorkError("ClickUp comment cursor order is inconsistent; refusing incomplete history.")
            if len(page) < 25:
                return result
            cursor = (str(page[-1]["date"]), str(page[-1]["id"]))
            if not added or cursor in cursors:
                raise WorkError("ClickUp pagination did not advance; refusing incomplete history.")
            cursors.add(cursor)
        raise WorkError("ClickUp comment page limit reached; refusing incomplete history.")
