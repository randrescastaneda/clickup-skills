"""Validate the built documentation: links, source coverage, snippets and page contracts."""

from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from clickup_skills.clients import CONFIG_CLIENTS, render_config
from clickup_skills.mcp import TOOLS


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.tags, self.headings = set(), [], [], []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if "id" in attrs:
            assert attrs["id"] not in self.ids, "Duplicate ID: " + attrs["id"]
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])
        if tag in ("h1", "h2", "h3"):
            self.headings.append(tag)


def main():
    output = ROOT / "dist"
    assert (output / "index.html").is_file(), "Build docs first"
    documents = {p: Page(p.read_text(encoding="utf-8")) for p in output.glob("*.html")}
    errors = []
    for path, parsed in documents.items():
        text = path.read_text(encoding="utf-8")
        assert '<html lang="en">' in text and '<title>' in text and 'name="description"' in text, path
        assert 'id="content"' in text and parsed.headings.count("h1") == 1, path
        assert "{{" not in text and "[TODO" not in text, path
        assert any(t == "a" and a.get("href") == "#content" for t, a in parsed.tags), path
        for raw in parsed.links:
            url = urlsplit(raw)
            if url.scheme or url.netloc:
                assert url.scheme in {"http", "https", "mailto"}, (path, raw)
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(output):
                errors.append((path.name, raw, "escapes output"))
            elif not target.is_file():
                errors.append((path.name, raw, "missing file"))
            elif url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
                errors.append((path.name, raw, "missing anchor"))
    assert not errors, "Internal link failures: " + repr(errors)
    manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
    assert manifest["tools"] == [t["name"] for t in TOOLS]
    skills = sorted((ROOT / "skills").glob("*/SKILL.md"))
    assert manifest["skill_count"] == len(skills)
    ref = (output / "reference.html").read_text(encoding="utf-8")
    for tool in TOOLS:
        assert tool["name"] in ref and tool["description"] in ref
        assert tool["name"] in documents[output / "reference.html"].ids
    for skill in skills:
        assert (output / (skill.parent.name + ".html")).is_file()
    examples = (output / "examples.html").read_text(encoding="utf-8")
    assert examples.count('class="language-prompt"') == 18, "Examples must render as copyable prompts"
    assert examples.count('data-category=') == 18
    installation = (output / "installation.html").read_text(encoding="utf-8")
    assert 'class="language-bash"' in installation and "Who does what" in installation
    assert "Each teammate" in installation and "Project lead" in installation
    lock = json.loads((ROOT / "upstreams.lock.json").read_text(encoding="utf-8"))
    cup = next(p for p in lock["projects"] if p.get("package") == "@krodak/clickup-cli")
    command = "npm install -g " + cup["install_spec"]
    assert command in installation and command in (ROOT / "README.md").read_text(encoding="utf-8")
    assert "npm install -g " + cup["package"] + "@" + cup["version"] not in installation
    setups = json.loads((output / "client-setups.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "profiles/default.json").read_text(encoding="utf-8"))
    for client, data in setups.items():
        assert data["config"] == render_config(client if client in CONFIG_CLIENTS else "portable", config)
    index = json.loads((output / "search-index.json").read_text(encoding="utf-8"))
    assert {p["url"] for p in index} == {p + ".html" for p in manifest["pages"]}
    assert all(p["title"] and len(p["text"]) > 40 for p in index)
    assert (output / "llms.txt").stat().st_size and (output / "llms-full.txt").stat().st_size
    print(f"Documentation checks passed: {len(documents)} HTML pages, internal links/anchors, rendered prompts, source-derived tools/skills, client snippets, search and agent-readable outputs.")


if __name__ == "__main__":
    main()
