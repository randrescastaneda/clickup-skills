---
title: Install for your team
description: One terminal command, then one agent verification. Browser OAuth by default.
section: Start here
---
# Install and connect in two actions.

Choose the **coding agent you actually use**, not merely the editor where it runs. The default ClickUp authentication method is **browser-based OAuth**. Each teammate must configure their own agent environment and authorize their own accounts.

## 1. Run one command in your terminal

Install [Node.js 22+](https://nodejs.org/), Python 3.11+, Git, and [GitHub CLI](https://cli.github.com/) first. The same command works in macOS Terminal and Windows PowerShell:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

The installer asks which agent to configure: press **Enter for Kilo Code (default)**, or select Codex, Claude Code, or GitHub Copilot. You can also supply the client directly, e.g. `--client codex`.

**What it does:** Installs six agent skills, adds ClickUp's official remote MCP endpoint (`https://mcp.clickup.com/mcp`) and GitHub MCP to your agent configuration, and checks GitHub CLI authorization. If you have already signed in with `gh`, that sign-in is reused; otherwise its browser login starts. Settings and existing server entries are preserved. Conflicting or locally edited skill copies are not overwritten.

**What it does NOT do:** It does not install Krodak's CLI, access a private ClickUp token, authenticate ClickUp in the terminal, or enable the local helper's durable journal. **ClickUp OAuth happens inside your coding agent in Step 2**, not through `npx`.

If the installer finds an existing equivalent ClickUp MCP server under a different name, it reuses it rather than installing a duplicate. An existing `clickup_work` server, if present, is preserved but **is not authenticated by hosted OAuth**.

## 2. Reload your agent and verify OAuth

Restart or reload the **selected coding agent** and send this instruction in its chat:

```prompt
Use the clickup-setup skill to verify my OAuth-based ClickUp Skills installation.
Discover the six skills and the actual official ClickUp and GitHub MCP tools.
Guide me through the official ClickUp MCP's browser OAuth flow only if needed.
Verify read-only access to my intended Workspace, List and task, plus my GitHub
repository. Do not create or modify any tasks, issues or PRs.
Report the authenticated servers, exact scope, and missing setup (if any).
```

**Why is the second step needed?** The terminal can install the configuration; only your running coding agent can complete its hosted OAuth and actually discover the available tools and permissions. GitHub CLI sign-in and a hosted GitHub MCP's OAuth are independent.

<details markdown="1"><summary>Already using the official ClickUp MCP?</summary>

Your existing browser OAuth session may continue to work. The installer reuses a legitimate configured endpoint without replacing your sign-in or forcing a fresh ClickUp token. Reload the agent, then ask it to verify which server was discovered.

</details>

## What is included and what is not

| Default OAuth mode | Full local helper mode |
| --- | --- |
| **No ClickUp API token.** Official ClickUp MCP authorizes in the agent's browser flow | Requires the ClickUp CLI's personal API token, unless it is already configured |
| Six skills + hosted ClickUp/GitHub MCP configuration | Six skills + private Python workflow + Krodak CLI + local `clickup_work` MCP |
| Agents execute operations directly, following a [guarded host issue-first protocol](clickup-github.html) | Local helper enforces project scope and records durable operation receipts when a valid binding is configured |
| Markers and read-backs reduce duplicates; no local helper journal or cross-machine exactly-once guarantee | Helper journals and OS locks cover local writes, not other machines or direct host calls |

**Both modes require task/repository access and a verified project scope.** GitHub-first links, bounded writes, and safe retry rules are required in either mode. An authorized OAuth grant may be able to write even while you are *testing reads*: agents must respect the actual approved write scope.

### Optional: install the full helper instead

To enable the stricter local helper and its synchronization worker, choose `--mode cli` explicitly:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode cli --client kilo
```

This installs our Python workflow and Krodak's `{{cup_install_spec}}`. If the user's personal ClickUp CLI sign-in has not been configured, the terminal guides them to [ClickUp Settings → Apps](https://app.clickup.com/settings/apps) to generate a token and enter it securely via `cup init`; `cup auth` verifies it. Existing valid CLI credentials are reused. This **does not** authorize the official hosted MCP. Keep tokens out of tasks, chats, commands, and version control.

The original software-only command remains supported and intentionally does not authenticate accounts:

```bash
npx --yes github:randrescastaneda/clickup-skills setup --client kilo
```

## Who does what

| Role | Responsibility |
| --- | --- |
| Workspace owner/admin | Grant access to ClickUp Workspaces/Lists and optionally configure the native GitHub integration/automations |
| Repository/organization admin | Give the right teammates and GitHub App access to the intended repositories |
| Each teammate | Run the installer and approve **their own** browser authorizations |
| Project lead + agent | Verify objective, GitHub owner/repo/base, ClickUp Workspace/List/root tasks and task permissions |
| Each agent + teammate | Confirm skill discovery, bounded writes and a small end-to-end pilot before production automation |

A teammate installing the plugin does not install it for the entire team. No credentials are shared through `.clickup/project.json`.

## Bind your working project

The *project you are actually editing* (not the ClickUp Skills repository) can contain `.clickup/project.json` binding its objective, repository, Workspace, home List, roots and statuses. The [project setup](project-setup.html) explains it.

In OAuth mode, an agent can read an approved binding directly; it must verify the live identity/ancestry through the official MCP. An unbound agent must ask for explicit project scope **before writing**. It must not pretend that direct host calls use the local helper journal.

## Small approved write pilot

After read-only access is verified, choose a disposable or explicitly authorized task. Ask the agent to verify the GitHub issue or PR **before** creating a child, include the canonical issue/PR URL in the initial description, read it back via `text_content`, append exactly one managed GitHub backlink, and re-run the preflight expecting zero extra writes. The host agent follows [the official-MCP guarded workflow](clickup-github.html); it stops on incomplete history or uncertain writes.

Do not mark a task Done simply because a PR exists. The linked merged non-draft PR, current checks, and acceptance evidence are separate gates.

## Alternative and advanced installation

<details markdown="1"><summary>Standard Vercel Skills CLI (manage skills separately)</summary>

The standard Vercel CLI installs skills but does **not** configure hosted MCPs or the local Python helper:

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

These two commands are an **alternative** to the single bundled installer, not an extra requirement. The `--skip-skills` option preserves Vercel-owned copies. For the local full-helper option append `--mode cli` to the second command. Use Vercel's `skills check` / `skills update -g` to maintain its copies. Avoid duplicate skill managers in the same directory.

</details>

<details markdown="1"><summary>Extra clients, project scope, and contributor setup</summary>

Run `onboard --client codex`, `onboard --client claude`, or `onboard --client copilot` to skip the agent chooser. For project-specific configuration supply `--project-dir /absolute/path/to/project`; VS Code MCP configuration uses `--client vscode` and requires that flag. The agent that runs in the editor owns tool discovery and its OAuth authorization. Preserve existing manual customizations; conflicts stop instead of overwriting files.

For OpenCode, Posit Assistant, and special/legacy clients, use the [client setup matrix](clients.html) and manual scripts in the [repository README](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing).

<div class="setup-chooser"><label for="client-choice">Advanced client configuration</label><select id="client-choice"><option value="claude">Claude Code</option><option value="codex">Codex</option><option value="copilot">GitHub Copilot</option><option value="kilo" selected>Kilo Code</option><option value="opencode">OpenCode</option><option value="posit">Posit Assistant</option><option value="vscode">VS Code MCP</option></select><div id="client-setup" aria-live="polite"></div></div>

<noscript>Client-specific commands are available in the <a href="clients.html">client setup matrix</a>.</noscript>

</details>

## Keep installations current

For an OAuth-only installation, run the same onboarding command with your existing `--client` to reconcile the hosted MCP configuration; update the six skills at the same time if our installer owns them:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo
```

For an installed token-backed local helper, `update` keeps its previous full-runtime semantics:

```bash
npx --yes github:randrescastaneda/clickup-skills update --client kilo
```

The full helper explicitly updates its private runtime and Krodak's latest CLI. Do not update in the middle of a task write. Reload the client and verify discovery after updates. Website publication never updates local agent installations.

## Optional native ClickUp–GitHub integration

The plugin does not install a GitHub webhook, activate native ClickUp GitHub links, start a synchronizer, or create automation rules. Those are separate tasks requiring authorized administrators and possibly plan features. See [native integration setup](github-integration.html), [ClickUp's integration guide](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration), and [GitHub Automations](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations).
