---
title: Install for your team
description: Who installs what, where it runs, and how everyone knows it works.
section: Start here
---
# Install once. Delegate every day.

The plugin is installed **in the coding agent’s environment**, not as a ClickUp app for every user. Setup combines shared workspace access, personal tools, and one project binding. You can ask your setup agent or IT teammate to run the installation steps; you approve sign-ins and access.

## Who does what

One person may hold several roles. Shared setup does not sign in other teammates or install anything on their computers.

| Role | Responsibility | Where / how often |
| --- | --- | --- |
| ClickUp owner or admin | Grant access to the intended Space/List; optionally connect GitHub and configure native automations | ClickUp Workspace; once per shared integration |
| GitHub repository or organization admin | Grant repository access and approve the GitHub App for the **repository owner’s account or organization**; map repositories when using the native integration | GitHub organization/account and ClickUp; once per repository/integration |
| Each teammate (or their IT/setup agent) | Install the local runtime and agent skills; merge the correct MCP configuration; sign in with their own ClickUp and GitHub accounts | Each machine, container, or remote agent environment they use |
| Project lead + agent | Select the objective and root task(s), verify IDs, create the binding, and map exact ClickUp statuses | Each working repository / worktree |
| Each teammate + agent | Confirm skill discovery, tool access, scope, and a small end-to-end pilot | Each agent/client after initial setup or a material change |

**Every teammate authenticates individually.** A maintainer installing the plugin on their laptop does not install it for the team. A shared project binding contains identifiers and an objective, never credentials.

## 1. Run one setup command

Have Python 3.11+, Node 22+, and Git installed where the agent runs. Then run:

```bash
npx --yes github:randrescastaneda/clickup-skills setup --client kilo
```

Replace `kilo` with `codex`, `claude`, or `copilot`. Your setup agent can run this for you. **No manual clone, virtual environment, activation, or separate Python scripts.** The command works directly from GitHub; it does not require a separately published npm package.

The installer creates a private Python environment, installs Krodak’s `{{cup_install_spec}}`, copies the five skills, and merges your agent’s MCP settings. It uses personal directories without a global npm install or administrator privileges. Existing settings and JSONC comments are preserved; changed settings receive a private backup. Conflicting MCP entries and locally edited skills stop setup for deliberate resolution.

The installed MCP command points to a persistent runtime outside the temporary npx cache. You can close the terminal after setup; no environment activation is needed. Install GitHub CLI from [its official distribution](https://cli.github.com/) as well: the local workflow uses `gh` for GitHub operations.

<div class="callout"><strong>What remains personal?</strong> Every teammate signs in to their own accounts. Installation cannot grant Workspace or repository access, approve OAuth, or enable the team’s native integrations.</div>

<details markdown="1"><summary>Advanced clients and contributor installations</summary>

The checkout-based Python scripts remain available for contributors, OpenCode, Posit Assistant, legacy clients, and custom MCP settings. Follow the [client setup matrix](clients.html) or [repository README](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing). The automatic installer supports current Kilo, Codex, Claude Code, Copilot, and project-scoped VS Code. Do not install duplicate skills/servers through both the installer and Claude’s marketplace plugin.

</details>

<div class="callout"><strong>Using an environment with no shell?</strong> An agent can use existing host ClickUp and GitHub MCPs with the same skills and scope rules. This bypasses the local helper and its receipt journal; the agent must perform equivalent checks itself. See <a href="synchronization.html#host-mcp-only-environments">host MCP-only environments</a>.</div>

## 2. Choose the actual agent client

Use the client running your session, even inside VS Code or Positron. The editor name alone does not identify the agent’s skill paths or MCP format.

<div class="setup-chooser"><label for="client-choice">My agent client</label><select id="client-choice"><option value="claude">Claude Code</option><option value="codex">Codex</option><option value="copilot">GitHub Copilot</option><option value="kilo" selected>Kilo Code</option><option value="opencode">OpenCode</option><option value="posit">Posit Assistant</option><option value="vscode">VS Code MCP</option></select><div id="client-setup" aria-live="polite"></div></div>

<noscript>The interactive chooser requires JavaScript. All client commands and destinations are available in the <a href="clients.html">client setup matrix</a>.</noscript>

The one-command installer merges personal settings by default. Append `--project-dir /absolute/path/to/project` for project scope; VS Code requires that flag. Existing GitHub MCP servers are reused. The advanced Python renderer still prints configuration only, for clients outside automatic setup.

## 3. Authenticate and verify discovery

Setup prints the remaining account steps. Each teammate runs:

```bash
npx --yes github:randrescastaneda/clickup-skills cup init
npx --yes github:randrescastaneda/clickup-skills cup auth
gh auth login
```

`cup init` prompts locally for the teammate’s ClickUp configuration; `cup auth` verifies it. Never put tokens in a task, repository, or chat. The managed CLI also respects its existing personal authentication, so teammates already signed in do not need a second account setup. A configured GitHub MCP has its own authorization and does not replace `gh` authentication for the local helper.

Then ask your agent:

```prompt
Check my ClickUp Skills installation. Confirm the five workflow skills are
available, discover the actual ClickUp and GitHub tool schemas, and report
which accounts and repository permissions this session can use. Do not create
or modify tasks yet. Tell me any missing setup in plain language.
```

For a local runtime, ask the agent to call the installed workflow MCP, then check ClickUp and GitHub sign-in separately. Shell-based agents can access the same managed helper using `npx --yes github:randrescastaneda/clickup-skills work` followed by the usual `cu-work` arguments. `doctor` checks local prerequisites and binding validity; it does **not** establish remote scope or inspect credentials.

## 4. Bind a working project

Your **working project repository** is where `.clickup/project.json` belongs. Installation does not bind a project or change remote tasks. The project lead supplies the objective, repository, ClickUp Workspace, List, and root task link(s); the agent resolves and verifies the actual IDs. Follow [project setup](project-setup.html).

## 5. Run a small team pilot

Choose a disposable or team-approved test task. Have the agent read it, create one GitHub-associated subtask, record one progress update, and link a draft test PR. Verify both directions of the links and preserve the PR’s original description. Repeat an identical operation and a comment reconciliation; expect no duplicate writes.

Confirm that an unrelated task is rejected and that a draft/open PR, pending checks, or missing acceptance evidence keeps the task open. Test each teammate’s actual client; rendered configuration passing CI does not prove that every installed editor or extension loads it.

## Keep installations current

Ask your setup agent to refresh the installed client:

```bash
npx --yes github:randrescastaneda/clickup-skills update --client kilo
```

Replace `kilo` with your client and use the same `--project-dir` when updating a project installation. This refreshes the Python workflow, managed skill copies, MCP command paths, and Krodak’s CLI to its current `latest` release. Repeat for each client you use. Plain `setup` reuses an unchanged runtime; updates are explicit and never run during MCP startup or task writes.

Existing local skill edits and conflicting server changes stop the update. Earlier runtimes stay available for other installed clients and running sessions. After updating, reload the agent, verify discovery, and have it read the bound task before resuming writes. A failed compatibility check needs deliberate resolution. Other executable MCP dependencies keep their reviewed pins.

For advanced checkout or Claude marketplace installations, use that installation method’s update flow. **Website redeployment does not update teammates’ installed tools.**

## Optional shared integration

The plugin works without a paid integration dependency. Native GitHub activity linking and optional ClickUp automations are separate admin tasks. The repository’s reviewed guidance states that native activity linking is available on all ClickUp plans; GitHub Automation integrations require Business or above. Verify current plan/UI details in [ClickUp’s official integration guide](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration) and [automation guide](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations).

Continue with [native integration setup](github-integration.html) if the team wants activity links while agents are offline. Installing this plugin does not install a webhook or background comment worker.
