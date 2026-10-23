"""Build source-derived, agent-first documentation without touching remote services."""

import argparse
import html
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
from urllib.parse import urlsplit, urlunsplit

import markdown

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from clickup_skills.clients import CONFIG_CLIENTS, SKILL_PATHS, render_config
from clickup_skills.cli import parser as cli_parser
from clickup_skills.mcp import TOOLS

REPO = "https://github.com/randrescastaneda/clickup-skills"
DEFAULT_URL = "https://randrescastaneda.github.io/clickup-skills/"
SOURCES = {
    "docs/sync-worker.md": ("sync-worker", "Optional sync worker", "Work with your agent"),
    "docs/project-decisions.md": ("project-decisions", "Project decisions", "Maintain"),
    "docs/clients.md": ("clients", "Client setup matrix", "Reference"),
    "docs/contract.md": ("contract", "Execution contract", "Reference"),
    "docs/wiki/github-clickup.md": ("github-integration", "Native integration setup", "Work with your agent"),
    "docs/validation.md": ("validation", "Validation & limits", "Reference"),
    "THIRD_PARTY_NOTICES.md": ("credits", "License & attribution", "Maintain"),
}
NAV = [
    ("Start here", [("index", "Overview"), ("installation", "Install for your team"), ("project-setup", "Bind your first project")]),
    ("Work with your agent", [("using-the-plugin", "Talk to your agent"), ("examples", "Usage examples"), ("synchronization", "GitHub, ClickUp & sync"), ("sync-worker", "Optional sync worker"), ("github-integration", "Native integration setup")]),
    ("Reference", [("reference", "Skills & MCP tools"), ("clients", "Client setup matrix"), ("profiles", "Backends & profiles"), ("binding-reference", "Project binding"), ("cli", "CLI for agents"), ("contract", "Execution contract"), ("validation", "Validation & limits"), ("troubleshooting", "Troubleshooting")]),
    ("Maintain", [("maintenance", "Documentation pipeline"), ("project-decisions", "Project decisions"), ("releases", "Version & releases"), ("credits", "License & attribution")]),
]


def run_git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def metadata(text):
    if text.startswith("---\n"):
        front, text = text[4:].split("\n---\n", 1)
        return dict(line.split(": ", 1) for line in front.splitlines() if ": " in line), text
    return {}, text


def collect_pages():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    lock = json.loads((ROOT / "upstreams.lock.json").read_text(encoding="utf-8"))
    pins = {p.get("package"): p.get("version") for p in lock["projects"]}
    cup = next(p for p in lock["projects"] if p.get("package") == "@krodak/clickup-cli")
    cup_install_spec = cup["install_spec"]
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    substitutions = {"skill_count": str(len(skill_files)), "tool_count": str(len(TOOLS)), "cup_install_spec": cup_install_spec}
    pages = {}
    for path in sorted((ROOT / "site/content").glob("*.md")):
        front, body = metadata(path.read_text(encoding="utf-8"))
        for key, value in substitutions.items():
            body = body.replace("{{" + key + "}}", value)
        pages[path.stem] = {**front, "body": body, "source": path.relative_to(ROOT).as_posix()}
    for source, (slug, title, section) in SOURCES.items():
        pages[slug] = {"title": title, "section": section, "description": f"The repository's current {title.lower()}.",
                       "body": (ROOT / source).read_text(encoding="utf-8"), "source": source}
    skills = []
    for path in skill_files:
        front, body = metadata(path.read_text(encoding="utf-8"))
        name = front["name"]
        skills.append((name, front["description"]))
        pages[name] = {"title": name, "section": "Reference", "description": front["description"],
                       "body": f'<div class="callout">Generated from the installed skill source. <a href="reference.html">All skills and tools →</a></div>\n\n' + body,
                       "source": path.relative_to(ROOT).as_posix()}
    reference = ["# The workflow your agent follows.", "This reference is generated from the actual skill files and MCP tool definitions at build time. Tool names and required inputs are not maintained in a separate hand-written list.", "## Shared skills", "| Skill | What it guides |", "| --- | --- |"]
    reference += [f"| [{name}]({name}.html) | {description} |" for name, description in skills]
    reference += ["\n## Scoped workflow tools", "All tools require an absolute `project_dir` pointing to the working Git worktree. Optional task IDs use local focus where supported; agents should pass explicit IDs for parallel work. The local helper checks scope and keeps receipts. Host MCP calls enforce the same rules through the skills, outside that journal."]
    for tool in TOOLS:
        schema = tool["inputSchema"]
        reference += [f"\n### {tool['name']}", tool["description"], "**Required:** " + ", ".join(f"`{s}`" for s in schema["required"]) + ".", '<details markdown="1"><summary>Input schema for agents</summary>\n', "```json\n" + json.dumps(schema, indent=2) + "\n```\n", "</details>"]
    pages["reference"] = {"title": "Skills & MCP tools", "section": "Reference", "description": "Generated skills, MCP tool descriptions and input schemas.", "body": "\n\n".join(reference), "source": "src/clickup_skills/mcp.py"}
    profiles = ["# Choose the tools your agent actually needs.", "The default local runtime is `cup`. Routing recommendations do not benchmark servers, inspect the host inventory, or execute the chosen tool. Enable only the profiles you need and discover current tool schemas before using them.", "## Profiles from source", "| Profile | Named servers |", "| --- | --- |"]
    for path in sorted((ROOT / "profiles").glob("*.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        profiles.append(f"| `{path.stem}` | " + ", ".join(f"`{n}`" for n in config["mcpServers"]) + " |")
    profiles += ["\n## Execution and authentication", "| Backend | How it runs / signs in |", "| --- | --- |", "| `cup` | Direct local helper runtime; each teammate signs in with cup |", "| `rest-mcp` | Optional installed local Python MCP runtime; private CLICKUP_API_KEY / CLICKUP_API_KEY_FILE and CLICKUP_TEAM_ID; select routing.runtime explicitly |", "| `context-mcp` | Host MCP for richer context; defaults to read-minimal, so do not assume write tools |", "| `official` | Host ClickUp MCP with the teammate's OAuth sign-in |", "| `github-cli` | The helper uses gh with personal local authentication |", "| `github-mcp` | Agent calls host GitHub MCP with the client's supported authentication |", "\nThe helper does not silently fail over to another account or provider. Host official/context/GitHub tools execute outside the helper's local scope enforcement and journal. Missing tools must be addressed before dispatch; uncertain writes must be reconciled before any backend switch.", "\n## Reviewed dependencies", "| Package / project | Reviewed version / commit | Install policy | License |", "| --- | --- | --- | --- |"]
    profiles += [f"| `{p.get('package', p['repository'])}` | `{p.get('version', p['commit'])}` | {p.get('install_spec', 'Pinned' if p.get('package') else 'Reference only')} | {p['license']} |" for p in lock["projects"]]
    profiles += ["\nThese review records come from `upstreams.lock.json`; preserve notices when updating. The ClickUp CLI install policy follows the publisher’s `latest` tag, while its recorded version remains the reviewed compatibility baseline. Other executable MCP dependencies remain pinned. Free software does not remove service permissions, plan limits, rate limits or your model provider's charges.", "\n## Alternative local runtime", f"```bash\npython3 -m pip install 'clickup-rest-mcp=={pins['clickup-rest-mcp']}'\n```", "\nYour setup agent sets the private environment and explicitly selects `routing.runtime = rest-mcp` in the binding. The helper launches the installed executable; it does not install it in the middle of a task write. See [the contract](contract.html) and [client setup](clients.html)."]
    pages["profiles"] = {"title": "Backends & profiles", "section": "Reference", "description": "Generated profiles, reviewed dependency baselines and install policies.", "body": "\n\n".join(profiles), "source": "upstreams.lock.json"}
    pages["binding-reference"] = {"title": "Project binding", "section": "Reference", "description": "The source example for .clickup/project.json.", "body": "# The project binding.\n\nGenerated from `examples/project.json`. All IDs are illustrative. Review the repository, objective and actual remote task scope before using a binding.\n\n```json\n" + (ROOT / "examples/project.json").read_text(encoding="utf-8") + "\n```\n\n[Set up your project](project-setup.html) · [Read the execution contract](contract.html)", "source": "examples/project.json"}
    parser = cli_parser()
    parser.prog = "cu-work"
    commands = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices
    cli = ["# Commands are for your agent.", "Daily users delegate in plain language. This generated command reference helps setup agents, maintainers and debugging. Multiline bodies use files or structured MCP inputs, and global options precede subcommands.", "## Top-level help", "```text\n" + parser.format_help() + "```"]
    for name, command in commands.items():
        command.prog = "cu-work " + name
        cli += [f"\n## {name}", "```text\n" + command.format_help() + "```"]
    pages["cli"] = {"title": "CLI for agents", "section": "Reference", "description": "CLI help generated from the actual parser.", "body": "\n\n".join(cli), "source": "src/clickup_skills/cli.py"}
    return pages, project, skill_files


def client_setups():
    destinations = {"claude": "Use the marketplace plugin; it supplies its default MCP servers and skills.", "codex": "Merge the printed TOML into your Codex config.toml under [mcp_servers.*].", "copilot": "Merge the output into ~/.copilot/mcp-config.json or the installed harness's supported project .mcp.json.", "kilo": "Merge into the current Kilo .kilo/kilo.jsonc or existing kilo.jsonc, under mcp. Older extensions need their own legacy settings.", "opencode": "Install portable skills; verify your OpenCode version's MCP settings before adopting the portable manifest.", "posit": "Merge into .posit/assistant/settings.json under mcpServers. Configure skills using the installed Assistant's supported mechanism.", "vscode": "Merge into .vscode/mcp.json under servers. This does not configure a separate Copilot CLI session."}
    setups = {}
    for name, text in destinations.items():
        automatic = name in ("claude", "codex", "copilot", "kilo", "vscode")
        if automatic:
            commands = f"npx --yes github:randrescastaneda/clickup-skills onboard --client {name}"
            if name == "vscode":
                commands += " --project-dir /absolute/path/to/project"
            text = "OAuth-first setup: installs six skills and hosted ClickUp/GitHub MCP configuration; ClickUp browser authorization and tool verification happen inside the agent. Use --mode cli only for the token-backed local helper."
        else:
            commands = (f"python3 scripts/install_skills.py --client {name}\n" if name in SKILL_PATHS else "")
            commands += f"python3 scripts/configure.py --client {name if name in CONFIG_CLIENTS else 'portable'} --profile default"
        config = json.loads((ROOT / "profiles/default.json").read_text(encoding="utf-8"))
        setups[name] = {"text": text, "commands": commands, "automatic": automatic, "config": render_config(name if name in CONFIG_CLIENTS else "portable", config), "skills": "Project skills: .github/skills/" if name == "vscode" else "Personal skill path: ~/" + SKILL_PATHS[name][0] if name in SKILL_PATHS else "No automated skill installer target for this client; confirm its supported skill discovery."}
    return setups


def rewrite_links(body, source, source_map, sha):
    # Rewrite Markdown and HTML links to source files. Existing website URLs stay relative.
    def replace(match):
        prefix, raw, suffix = match.groups()
        if raw.startswith(("https:", "http:", "mailto:", "#")):
            if raw.startswith(REPO + "/blob/feat/clickup-project-workflows/"):
                raw = raw.replace("/blob/feat/clickup-project-workflows/", "/blob/" + sha + "/")
            return prefix + raw + suffix
        parsed = urlsplit(raw)
        if parsed.path.endswith(".html") or not parsed.path:
            return match.group(0)
        path = Path(os.path.normpath(str(Path(source).parent / parsed.path))).as_posix()
        if path in source_map:
            target = source_map[path] + ".html"
        elif (ROOT / path).is_file():
            target = REPO + "/blob/" + sha + "/" + path
        else:
            return match.group(0)
        return prefix + target + ("#" + parsed.fragment if parsed.fragment else "") + suffix
    return re.sub(r'(\]\()([^\s)]+)(\))', replace, body)


def render_page(slug, page, pages, project, sha, url):
    esc = html.escape
    source_map = {p["source"]: key for key, p in pages.items()}
    body = rewrite_links(page["body"], page["source"], source_map, sha)
    md = markdown.Markdown(extensions=["fenced_code", "tables", "toc", "md_in_html", "sane_lists"], extension_configs={"toc": {"permalink": "#"}})
    rendered = md.convert(body)
    nav = ""
    for section, links in NAV:
        nav += f'<div class="nav-group"><p>{section}</p>'
        for key, title in links:
            nav += f'<a href="{key}.html"' + (' aria-current="page" class="active"' if key == slug else '') + f'>{title}' + ('<span class="nav-new">18</span>' if key == 'examples' else '') + '</a>'
        nav += '</div>'
    toc = ''.join(f'<a href="#{esc(token["id"])}">{esc(token["name"])}</a>' for token in md.toc_tokens for token in ([token] if token['level'] == 2 else token.get('children', [])) if token['level'] == 2)
    if slug == "index":
        toc = '<span class="toc-note">A shared workflow for your team and its agents.</span>'
    flat = [key for _, links in NAV for key, _ in links]
    pager = ''
    if slug in flat:
        index = flat.index(slug)
        for offset, label in [(-1, '← Previous'), (1, 'Next →')]:
            n = index + offset
            if 0 <= n < len(flat):
                key = flat[n]
                pager += f'<a href="{key}.html"><span>{label}</span><strong>{esc(pages[key]["title"])}</strong></a>'
    canonical = url + slug + ".html" if slug != "index" else url
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f7f8f5"><title>{esc(page['title'])} · ClickUp Skills</title><meta name="description" content="{esc(page.get('description', 'ClickUp Skills documentation'))}"><link rel="canonical" href="{esc(canonical)}"><meta property="og:title" content="{esc(page['title'])} · ClickUp Skills"><meta property="og:description" content="{esc(page.get('description',''))}"><meta property="og:type" content="website"><meta property="og:url" content="{esc(canonical)}"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body class="{'home' if slug == 'index' else 'docs'}"><a class="skip-link" href="#content">Skip to content</a>
<header class="header"><a class="brand" href="index.html" aria-label="ClickUp Skills home"><span class="brand-mark" aria-hidden="true">⌃</span><span>clickup<span class="brand-light"> skills</span></span><span class="docs-badge">DOCS</span></a><button class="search-trigger" type="button" aria-haspopup="dialog"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><span>Find something…</span><kbd>⌘ K</kbd></button><div class="header-links"><a href="releases.html" class="version">v{esc(project['version'])}<span class="version-dot"></span></a><a class="github-link" href="{REPO}">GitHub <span>↗</span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="sidebar" aria-label="Open navigation">☰</button></div></header>
<aside class="sidebar" id="sidebar" aria-label="Documentation navigation"><div class="sidebar-top">THE AGENT WORKFLOW TOOLKIT</div><nav>{nav}</nav><a class="sidebar-bottom" href="installation.html"><span class="small-icon">↗</span><strong>New to the plugin?</strong><span>Start with the team setup guide.</span></a></aside><div class="nav-backdrop" hidden></div>
<div class="page-shell"><main id="content" tabindex="-1"><div class="breadcrumb"><span>Documentation</span><span>/</span>{esc(page['section'])}</div><article>{rendered}</article><nav class="pager" aria-label="Adjacent pages">{pager}</nav><footer class="footer"><span>ClickUp Skills <span class="footer-dot">·</span> Built for agents. Useful for people.</span><a href="{REPO}/blob/{sha}/{page['source']}">View source ↗</a><a href="{REPO}/commit/{sha}">Source {sha[:7]}</a></footer></main><aside class="on-this-page" aria-label="On this page"><p>ON THIS PAGE</p>{toc}<div class="toc-help"><span>Something missing?</span><a href="{REPO}/issues">Open an issue ↗</a><a href="llms.txt">Agent-readable docs ↗</a></div></aside></div>
<dialog id="search-dialog" aria-label="Search documentation"><div class="search-field"><label class="sr-only" for="search-input">Search documentation</label><input id="search-input" type="search" placeholder="Search guides, examples, tools…" autocomplete="off"><button id="close-search" aria-label="Close search">Esc</button></div><div id="search-results" aria-live="polite"><p class="search-hint">Search by task, client, tool or setup step.</p></div><div class="search-footer">Type to search · Tab to navigate · Enter to open</div></dialog><div class="toast" role="status" aria-live="polite"></div>
</body></html>'''


def build(output, release_file=None, base_url=DEFAULT_URL):
    output = Path(output).resolve()
    if output == ROOT or ROOT not in output.parents:
        raise ValueError("Output must be a build subdirectory inside the repository")
    # Never delete arbitrary user files: only allow our designated ignored output.
    if output != ROOT / "dist":
        raise ValueError("Documentation output must be the repository dist directory")
    if output.exists():
        shutil.rmtree(output)
    output.mkdir()
    pages, project, skill_files = collect_pages()
    sha = run_git("rev-parse", "HEAD")
    release = json.loads(Path(release_file).read_text(encoding="utf-8")) if release_file else None
    release_body = "# Source version & published releases.\n\n## Current documentation\n\nThis site is built from current `main`. The source package version is **" + project["version"] + "**; source may be ahead of a published release. Python requirement from source: `" + project["requires-python"] + "`.\n\nSource revision: [" + sha[:7] + "](" + REPO + "/commit/" + sha + ").\n\n## Latest published release\n\n"
    if release:
        release_body += f"[{html.escape(release['tag_name'])}]({release['html_url']}) · Published {release['published_at']}\n\n" + "Release notes and downloadable assets are available on GitHub. Check the release tag before installing; these docs describe current main.\n"
    else:
        release_body += "No published release metadata is bundled in this build. Install from a reviewed source revision; the source package version alone is not proof of a GitHub release. [View GitHub releases](" + REPO + "/releases).\n"
    release_body += "\n## Updating teammates\n\nA new release or website deployment does not update an installed plugin. Each teammate or their setup agent must update their checkout or marketplace installation, refresh managed skill copies and review dependency/configuration changes. See [installation updates](installation.html#keep-installations-current)."
    pages["releases"] = {"title": "Version & releases", "section": "Maintain", "description": "Source version, build provenance and published release metadata.", "body": release_body, "source": "pyproject.toml"}
    shutil.copytree(ROOT / "site/assets", output / "assets")
    search = []
    for slug, page in pages.items():
        document = render_page(slug, page, pages, project, sha, base_url)
        (output / (slug + ".html")).write_text(document, encoding="utf-8")
        plain = re.sub(r"<[^>]+>", " ", markdown.markdown(page["body"], extensions=["fenced_code", "tables"]))
        search.append({"title": page["title"], "url": slug + ".html", "section": page["section"], "text": html.unescape(re.sub(r"\s+", " ", plain))})
    for name, data in [("search-index.json", search), ("client-setups.json", client_setups()), ("build-manifest.json", {"source_sha": sha, "source_version": project["version"], "skill_count": len(skill_files), "tools": [t["name"] for t in TOOLS], "pages": sorted(pages), "latest_release": release})]:
        (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / ".nojekyll").touch()
    (output / "llms.txt").write_text("# ClickUp Skills\n\nAgent-first ClickUp/GitHub workflow documentation.\n\n" + "\n".join(f"- [{p['title']}]({base_url}{s}.html): {p.get('description','')}" for s, p in pages.items()) + "\n\n[Full documentation](" + base_url + "llms-full.txt)\n", encoding="utf-8")
    (output / "llms-full.txt").write_text("\n\n".join("# " + p["title"] + "\nSource: " + REPO + "/blob/" + sha + "/" + p["source"] + "\n\n" + p["body"] for p in pages.values()), encoding="utf-8")
    (output / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + html.escape(base_url + (s + '.html' if s != 'index' else '')) + '</loc></url>' for s in pages) + '</urlset>', encoding="utf-8")
    (output / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: " + base_url + "sitemap.xml\n", encoding="utf-8")
    not_found = {"title": "Page not found", "section": "Documentation", "description": "Find your way back to the documentation.", "body": '# This page has moved.\n\n[Return to the documentation](' + base_url + ') or search from the home page.', "source": "site/README.md"}
    # Absolute asset/navigation paths keep GitHub Pages' nested 404 responses usable.
    error = render_page("404", not_found, pages, project, sha, base_url)
    error = re.sub(r'(href|src)="(?!https?:|#|mailto:)([^"]+)"', lambda m: m[1] + '="' + base_url + m[2] + '"', error)
    (output / "404.html").write_text(error, encoding="utf-8")
    print(f"Built {len(pages)} documentation pages; {len(skill_files)} skills; {len(TOOLS)} MCP tools → {output}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release-json")
    p.add_argument("--base-url", default=DEFAULT_URL)
    args = p.parse_args()
    if not args.base_url.startswith("https://") or not args.base_url.endswith("/"):
        p.error("--base-url must be an absolute HTTPS URL ending in /")
    build(ROOT / "dist", args.release_json, args.base_url)
