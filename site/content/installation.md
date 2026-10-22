---
title: Install for your team
description: One guided terminal command, then one read-only agent check.
section: Start here
---
# Install and connect in two actions.

You install ClickUp Skills **where your coding agent runs**, not separately inside the ClickUp app. Each teammate sets up their own machine or agent environment. The installer handles the local software, and you personally authorize ClickUp and GitHub.

## 1. Terminal: install, connect accounts, and verify sign-in

Make sure **Node.js 22+, Python 3.11+, Git, and [GitHub CLI](https://cli.github.com/)** are installed first. Run **one command** in Terminal (macOS) or PowerShell (Windows):

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

The command guides you through these actions in order:

1. **Choose your agent.** Press Enter for **Kilo Code (default)**, or select Codex, Claude Code, or GitHub Copilot. To skip the chooser, pass `--client codex` (or another client name).
2. **Install automatically.** It installs the six agent skills, a private Python workflow runtime, Krodak’s `{{cup_install_spec}}`, and your agent's MCP configuration. There is no manual checkout, virtual-environment activation, or separate install/configuration step.
3. **Connect ClickUp if needed.** If an existing ClickUp CLI sign-in verifies successfully, it is reused. Otherwise, open [ClickUp Settings → Apps](https://app.clickup.com/settings/apps) in your browser, generate or copy your **personal API token**, return to the terminal, and follow the ClickUp CLI prompts to enter it and the Workspace ID. The terminal verifies the account using `cup auth`. Do **not** paste tokens into an agent chat, task, or repository.
4. **Connect GitHub if needed.** If `gh` is already signed in, it is reused. Otherwise, GitHub CLI opens its **browser authorization flow** and verifies sign-in when complete.
5. **Finish local verification.** The command confirms that the software setup and personal CLI sign-ins succeeded. Reload your coding agent for the next step.

The command uses the same installer on **macOS and Windows**. If GitHub CLI is missing, it provides [installation instructions](https://cli.github.com/); install it and rerun the **same** `onboard` command. The earlier completed setup and valid account sign-ins are reused.

**Important distinction:** `npx` starts the installer. It does not personally authorize either account. **ClickUp uses a token you create on the ClickUp website and enter in its CLI; GitHub uses browser-based authorization via `gh`.** Your ClickUp CLI stores the personal token in your local user configuration, so protect that account and never commit its configuration to Git.

<div class="callout"><strong>What this does not do:</strong> It cannot grant ClickUp Workspace access, grant GitHub repository permissions, approve organization installations, or activate the team's optional native ClickUp–GitHub integration. The hosted GitHub MCP may require <em>its own</em> OAuth authorization inside your coding agent; signing in with <code>gh</code> does not authorize that separate server.</div>

## 2. Agent: verify it can actually use the tools

**Restart or reload your coding agent**, then paste this single instruction into its chat:

```prompt
Use the clickup-setup skill to verify this ClickUp Skills installation.
Confirm all six skills load and discover the actual clickup_work and GitHub
MCP tool schemas. Verify read-only access to my ClickUp account and GitHub
account, plus the intended project/workspace and repository if they are
already bound. If a hosted MCP requires browser OAuth, guide me through
the client’s authorization UI. Do not create or modify tasks, issues, or
PRs. Report which checks passed and the smallest missing action, if any.
```

**Why the separate agent step?** The terminal can confirm installed files, configuration, and local CLI authentication. Only your running agent can confirm that it has discovered the six skills and the correct hosted/installed MCP tools, and that those tools can reach the intended resources.

## Who does what

One person can perform several roles. Installing on one machine does **not** authenticate or install for other teammates.

| Role | Responsibility | When / where |
| --- | --- | --- |
| ClickUp owner/admin | Grant each teammate access to the correct Workspace/List; optionally enable native GitHub integration and automations | Shared Workspace setup |
| GitHub repo/org admin | Grant repository access and approve the correct GitHub App / organization integration | Shared repository or organization setup |
| Each teammate | Run the terminal command, approve personal sign-ins, then use the agent verification prompt | Once per machine/agent environment |
| Project lead + agent | Select the project objective, working repository, ClickUp List/root tasks, and verify IDs and statuses | Each working project |
| Each teammate + agent | Validate permissions and a small end-to-end task/PR pilot | After first setup or material changes |

The plugin uses the user’s own permissions; it never grants broader remote access simply by installing.

## 3. Bind your working project

The repository **you are working on**, not the ClickUp Skills plugin repository, holds `.clickup/project.json`. Installation cannot choose your project scope for you. The project lead supplies the objective, GitHub repository, ClickUp Workspace/List, and root task links. The agent resolves and verifies IDs and the exact status names. See [project setup](project-setup.html).

## 4. Test a small end-to-end workflow

Choose a disposable or explicitly approved task. Ask your agent to read it, create a GitHub-associated subtask, link a draft test PR, and record a progress update. Verify reciprocal links, preserved descriptions, and no duplicates on repeat. Do not mark a task Done merely because a PR exists: acceptance, merge, and latest-head checks must satisfy the project policy.

## Alternative installers and advanced configuration

<details markdown="1"><summary>Standard Vercel Skills CLI (skills managed separately)</summary>

To manage the skills through Vercel instead of our bundled installer, run:

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills setup --client kilo --skip-skills
```

This is an **alternative**, not an additional required installation step. Vercel installs skills only; `--skip-skills` lets our setup install the runtime and MCP configuration without overwriting those copies. Run the account steps afterward using `npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills` if you want the guided authentication. Do not let two managers install skills to the same destination.

</details>

<details markdown="1"><summary>Manual setup, extra clients, and project-scoped installation</summary>

The previous installer command remains supported:

```bash
npx --yes github:randrescastaneda/clickup-skills setup --client kilo
```

That command installs software only, and prints separate authentication instructions. Prefer `onboard` for new team members. Use `--client codex`, `--client claude`, or `--client copilot` as needed. Use `--client vscode --project-dir /absolute/path/to/project` for VS Code project-scoped MCP. Existing GitHub MCP servers are reused, and local configuration changes receive a private backup. Conflicting MCP settings or locally edited skills stop the installer rather than overwriting your work.

The checkout-based Python scripts remain useful for OpenCode, Posit Assistant, legacy clients, contributors, and customized MCP profiles. Use the [client setup matrix](clients.html) or [repository README](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing).

<div class="setup-chooser"><label for="client-choice">Advanced setup for client</label><select id="client-choice"><option value="claude">Claude Code</option><option value="codex">Codex</option><option value="copilot">GitHub Copilot</option><option value="kilo" selected>Kilo Code</option><option value="opencode">OpenCode</option><option value="posit">Posit Assistant</option><option value="vscode">VS Code MCP</option></select><div id="client-setup" aria-live="polite"></div></div>

<noscript>Client-specific commands are also available in the <a href="clients.html">client setup matrix</a>.</noscript>

</details>

<details markdown="1"><summary>Environments without a shell</summary>

An agent can reuse existing host ClickUp and GitHub MCPs with the same skills and scope rules. This bypasses the local helper’s receipt journal; the agent must perform equivalent scope and recovery checks itself. See [host MCP-only environments](synchronization.html#host-mcp-only-environments).

</details>

## Keep installations current

For installations entirely managed by this plugin, ask your setup agent to refresh the installed client:

```bash
npx --yes github:randrescastaneda/clickup-skills update --client kilo
```

Replace `kilo` with your client and include the same project scope if applicable. Updates refresh the persistent Python runtime, managed skills and MCP configuration, and Krodak’s latest release. Other reviewed MCP dependencies keep their pins. Existing local edits stop an unsafe update; running sessions keep their earlier runtimes. Reload and ask the agent to verify after updating. Routine task writes never trigger updates.

For a Vercel-managed installation, use `npx skills check` and `npx skills update -g` (or `-p` for project skills), and separately update the runtime with `npx --yes github:randrescastaneda/clickup-skills update --client kilo --skip-skills`.

## Optional native ClickUp–GitHub integration

Native GitHub activity linking and ClickUp automations are **shared administrator tasks**, separate from local CLI and MCP sign-in. Connecting your CLI does not install a webhook or continuous comment-sync worker. The reviewed guidance states native links are available across ClickUp plans, while GitHub Automations require Business or above; verify current details in [ClickUp’s official integration guide](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration) and [automation guide](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations).

See [native integration setup](github-integration.html) if the team needs GitHub activity connected while agents are offline.
