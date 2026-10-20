"""Fetch public latest-release metadata for the docs build; never print tokens."""

import json
import os
from pathlib import Path
import urllib.error
import urllib.request

url = "https://api.github.com/repos/randrescastaneda/clickup-skills/releases/latest"
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "clickup-skills-docs"}
if os.environ.get("GH_TOKEN"):
    headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
try:
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        data = json.load(response)
    data = {key: data[key] for key in ("tag_name", "html_url", "published_at")}
except urllib.error.HTTPError as exc:
    if exc.code != 404:
        raise RuntimeError("Could not refresh release metadata; HTTP " + str(exc.code)) from None
    data = None
Path("release-metadata.json").write_text(json.dumps(data) + "\n", encoding="utf-8")
print("Release metadata refreshed." if data else "No published GitHub release yet.")
