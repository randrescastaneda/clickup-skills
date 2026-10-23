---
name: clickup-setup
description: Install, authenticate, validate, or update ClickUp Skills for OAuth-based agents or the token-backed local helper. Use for team onboarding, safe MCP configuration, choosing a backend, or diagnosing setup.
---

# Guided ClickUp Skills setup

Do not request or copy personal access tokens in chat. The user's **agent/client**, not this skill, performs hosted ClickUp OAuth. Confirm the actual coding agent and whether its config is global or project-scoped. Existing local settings, skills managed by another installer, and authorized sessions must be preserved.

## Recommended: one terminal command, one agent action

Prerequisites: Node.js 22+, Python 3.11+, Git, and GitHub CLI (`gh`).

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

The terminal chooser defaults to **Kilo Code**; `--client kilo|codex|claude|copilot` skips it. The default `--mode oauth` installs the six workflow skills and configures the **official hosted ClickUp MCP** and GitHub access (`gh` for Kilo; compatible GitHub MCP for other clients), without provisioning Krodak's CLI or prompting for a personal ClickUp API token. Existing `clickup_work` is preserved but is **not** authenticated by hosted OAuth. The terminal checks `gh` authentication, launching GitHub's browser flow if required. The remote GitHub MCP does not support dynamic client registration for Kilo, so Kilo's default OAuth setup does **not** add that server. It disables only an unchanged entry this installer previously added; user-managed GitHub servers remain untouched (and must be tested or disabled by the user). Validate same-URL ClickUp MCP aliases for OAuth safety before reuse; refuse duplicates.

**After reloading the actual agent**, discover the six skills and current MCP tool schemas. Verify the official ClickUp MCP's OAuth status through that client's authorization UI, its authenticated Workspace, exact intended task/List access, and GitHub account/repository access via `gh` (hosted GitHub MCP OAuth, if used, is independent of `gh`). A successful terminal install proves only software/configuration, **not** hosted OAuth or live task permission. Never write a task during discovery.

In Kilo, official MCP is a remote server at `https://mcp.clickup.com/mcp`; Kilo can prompt for browser OAuth when it connects. If the current config already contains an equivalent endpoint under a different name, reuse its actual name rather than adding duplicate servers.

## Explicit full-helper mode (personal token)

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode cli --client kilo
```

This installs the private Python helper runtime, Krodak's latest ClickUp CLI and managed `clickup_work` MCP in addition to skills/GitHub tooling. The upstream `cup init` terminal flow may require a personal API token created in [ClickUp Settings → Apps](https://app.clickup.com/settings/apps). `cup auth` verifies it; already valid sign-ins are reused. The helper's strict workspace/list/root validation and durable receipts also require a **verified project binding**; a running local MCP process alone is not proof of authorized task access.

The previous `setup --client kilo` and `update --client kilo` commands retain their software-only full-helper behavior. Do not switch an uncertain write from the official MCP to the CLI. Hosted OAuth credentials are **never** imported into `cup`.

## Vercel-managed skills (alternative)

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

This leaves Vercel-owned skills untouched while configuring the OAuth server and GitHub authentication. For Vercel-managed full-helper mode, add `--mode cli` to the second command. Do not use two installers to manage the same skill copies. When updating, use Vercel's updater for skills and `update --client CLIENT --skip-skills` for a separately installed local CLI runtime. For an OAuth-only installation, rerun `onboard --client CLIENT --skip-skills` to reconcile host server configuration; Vercel updates skills separately.

VS Code MCP requires `--client vscode --project-dir /absolute/project`. Legacy agents, OpenCode and Posit Assistant use the advanced setup matrix. For team usage, each teammate signs in with their own account. Native ClickUp–GitHub integration, automations, and any continuously running worker are separate administrator tasks.

## Before the first write

- Identify **OAuth host-agent** versus **full helper** explicitly. OAuth operations must follow the [guarded issue-first host protocol](../clickup-github/references/official-mcp-issue-first.md); agent-enforced protections do not substitute for the helper journal.
- Verify exact GitHub repo/base, ClickUp Workspace/List/root ancestry, allowed task and write budget. If no verified binding/scope exists, do not write.
- Report discovered tools, authenticated identities, missing permissions, and precisely which component requires action. Never announce `clickup_work` authenticated merely because it starts.
- For an update, preserve existing settings, refuse local conflicts, reload the agent and re-check actual discovery. No automatic update during task writes.
