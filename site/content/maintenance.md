---
title: Documentation & releases
description: How source changes become verified, deployed documentation on GitHub Pages.
section: Maintain
---
# Documentation that travels with the plugin.

This site lives in the plugin repository. GitHub Actions builds it from the checked-out source and deploys the verified static artifact to GitHub Pages. There is no separate docs repository to synchronize and no AI rewrite service or deployment token to maintain.

## What updates automatically

| Source of truth | Rebuilt site content |
| --- | --- |
| `pyproject.toml` | Current source package version and Python requirement |
| `skills/*/SKILL.md` | Skill inventory, descriptions and complete skill reference pages |
| `src/clickup_skills/mcp.py` | Actual MCP tool names, descriptions, required inputs and schemas |
| `src/clickup_skills/cli.py` | Current CLI commands and help |
| `profiles/*.json` + client renderers | Profile server inventory and generated per-client MCP configurations |
| `upstreams.lock.json` | Reviewed dependency baselines and explicit install policies; the ClickUp CLI follows `latest` |
| Operational Markdown in `docs/` | Client matrix, execution contract, native integration and validation pages |
| GitHub source revision / releases API | Build provenance, commit link, latest published release metadata |
| `site/content/` and `site/assets/` | Written guides, examples, design, search and navigation |

The site describes **current `main`**, which can be ahead of the latest release. The release page labels published releases separately. Every page links to its source revision. A release event rebuilds the current default-branch docs and refreshes release metadata; it does not silently replace the site with an older tag.

## When it runs

- Every push to `main`, including plugin, docs or configuration edits.
- Every pull request: build and validate without deploying.
- Published or edited releases: refresh release metadata and redeploy.
- Manual dispatch: rebuild or recover a deployment without changing source.

The deploy job runs only for default-branch or release/manual events after checks pass. PR builds have read-only permissions. Deployment grants `pages: write` and `id-token: write` only to the deployment job and uses the protected `github-pages` environment.

## Keep narrative guides honest

Generated references cannot explain the practical effect of every behavioral change. The docs-impact check compares a PR with its base: changes to runtime behavior, skills, manifests, profiles or dependency pins require a substantive guide/example/operational-doc change, or an explicit reviewed explanation in `site/docs-impact.json` of why the generated reference alone is sufficient. Editing CSS or this maintenance page alone does not satisfy the guide update requirement.

Reviewers should check installation responsibilities, plain-language examples, sync limits and acceptance rules against the proposed behavior. This check requires a decision; it does not claim to judge prose accuracy.

## Build and verify locally

These are maintainer tasks, not daily user commands:

```bash
python3 -m pip install -r site/requirements.txt
python3 scripts/build_docs.py
python3 scripts/check_docs.py
python3 scripts/check.py
```

The build writes only `dist/`. It generates the search index, client snippets, references, `llms.txt`, `llms-full.txt`, sitemap and provenance manifest from the same revision. Generated output is not committed back to `main`, so builds cannot create commit loops.

## First-time GitHub Pages setup

A repository admin chooses **Settings → Pages → Build and deployment → Source → GitHub Actions**. The workflow then uploads and deploys the build artifact. No personal access token is needed for ordinary deployment. The public URL is [randrescastaneda.github.io/clickup-skills/](https://randrescastaneda.github.io/clickup-skills/).

After merging, inspect the **Documentation & GitHub Pages** workflow and its `github-pages` deployment URL. If the job reports that Pages is disabled, an admin must enable the publishing source above. Repository admin access in a user account does not imply the connected GitHub App can change repository settings.

## Failure and recovery

Builds validate internal links/anchors, generated tool/skill coverage, content requirements and source manifests before upload. Plugin offline checks also run before deployment. A failure leaves the last successful deployment in place. Review the failing job, fix it in source and push again or rerun the workflow after correcting settings. The workflow’s deployment concurrency prevents overlapping publishes; it does not cancel an active production publish midway.

Rollback by reverting the source change through the normal repository review process and letting the same workflow deploy. Keep the prior successful deployment and source SHA in the Actions history. To verify a release refresh, compare the published release tag on [releases](releases.html) and the commit recorded in `build-manifest.json`.
