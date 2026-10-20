# Documentation website

Static, accessible documentation for people delegating work to agents. Maintained
in the plugin repository and deployed only through GitHub Actions to GitHub Pages.

- Curated pages: `site/content/*.md` (frontmatter: title, description, section).
- Presentation: `site/assets/`; shell and source-derived references: `scripts/build_docs.py`.
- Dependencies: `python3 -m pip install -r site/requirements.txt`.
- Build: `python3 scripts/build_docs.py`; validate: `python3 scripts/check_docs.py`.
- PR impact check: `python3 scripts/check_docs_impact.py --base <base-sha>`.
- Output: ignored `dist/`; no generated-file commits or automation commit loops.
- Full source/automation details: `site/content/maintenance.md`.

User-facing guides lead with agent prompts. Setup commands belong to the setup
agent/teammate; daily users should not need to operate the helper themselves.

When a behavior change affects onboarding or usage, update an applicable guide,
example, or operational document in the same PR. For a generated-reference-only
change, add an entry to `site/docs-impact.json` with `paths` (exact changed source
paths) and a concrete `reason` for why no guide change is needed. The impact check
only accepts newly added entries relative to the base, and checks coverage of all
changed behavioral source paths. This is an explicit review record, not an escape
hatch for missing docs.
