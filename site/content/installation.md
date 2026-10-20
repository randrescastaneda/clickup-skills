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

## 1. Prepare personal tools

For the local helper path, install Python 3.11+, Node 22+, Git, and the GitHub CLI in the environment where the agent runs. The agent must inherit a PATH containing `cu-work`, `cup`, and `gh`. Install the ClickUp CLI using the publisher’s `latest` release tag. The recorded version in the dependency review file documents the reviewed baseline; it does not restrict installations to that version.

<details open markdown="1"><summary>Installation steps for your setup agent</summary>

```bash
git clone https://github.com/randrescastaneda/clickup-skills.git
cd clickup-skills
python3 -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows PowerShell instead:
# .venv\Scripts\Activate.ps1
python -m pip install -e .
npm install -g {{cup_install_spec}}
cup init
cup auth
# Install GitHub CLI from https://cli.github.com/ first, then:
gh auth login
```

Keep this checkout and virtual environment available. Launch the agent from the activated environment, or configure its local MCP command with the absolute path to `.venv/bin/cu-work` (Windows: `.venv\Scripts\cu-work.exe`). Authentication is a personal action; never paste tokens into a repository, task, or chat.

</details>

A local MCP call still runs `cu-work` on that machine. Its GitHub operations use `gh`, even if the client also has GitHub MCP configured. These are separate authentication paths.

<div class="callout"><strong>Using an environment with no shell?</strong> An agent can use existing host ClickUp and GitHub MCPs with the same skills and scope rules. This bypasses the local helper and its receipt journal; the agent must perform equivalent checks itself. See <a href="synchronization.html#host-mcp-only-environments">host MCP-only environments</a>.</div>

## 2. Choose the actual agent client

Use the client running your session, even inside VS Code or Positron. The editor name alone does not identify the agent’s skill paths or MCP format.

<div class="setup-chooser"><label for="client-choice">My agent client</label><select id="client-choice"><option value="claude">Claude Code</option><option value="codex">Codex</option><option value="copilot">GitHub Copilot</option><option value="kilo">Kilo Code</option><option value="opencode">OpenCode</option><option value="posit">Posit Assistant</option><option value="vscode">VS Code MCP</option></select><div id="client-setup" aria-live="polite"></div></div>

<noscript>The interactive chooser requires JavaScript. All client commands and destinations are available in the <a href="clients.html">client setup matrix</a>.</noscript>

The configuration renderer **prints configuration; it does not edit settings**. Merge only the needed named servers into existing settings. Preserve unrelated servers. When using Claude’s marketplace plugin, avoid adding its `clickup_work` and `github` servers again globally. If GitHub MCP already exists, reuse it rather than duplicating it.

## 3. Authenticate and verify discovery

Ask your agent:

```prompt
Check my ClickUp Skills installation. Confirm the five workflow skills are
available, discover the actual ClickUp and GitHub tool schemas, and report
which accounts and repository permissions this session can use. Do not create
or modify tasks yet. Tell me any missing setup in plain language.
```

For a local runtime, ask the agent to verify `cu-work` on its own PATH, then check ClickUp and GitHub sign-in separately. `doctor` checks local prerequisites and binding validity; it does **not** establish remote scope or inspect credentials.

## 4. Bind a working project

The plugin checkout is the installation source. Your **working project repository** is where `.clickup/project.json` belongs. The project lead supplies the objective, repository, ClickUp Workspace, List, and root task link(s); the agent resolves and verifies the actual IDs. Follow [project setup](project-setup.html).

## 5. Run a small team pilot

Choose a disposable or team-approved test task. Have the agent read it, create one GitHub-associated subtask, record one progress update, and link a draft test PR. Verify both directions of the links and preserve the PR’s original description. Repeat an identical operation and a comment reconciliation; expect no duplicate writes.

Confirm that an unrelated task is rejected and that a draft/open PR, pending checks, or missing acceptance evidence keeps the task open. Test each teammate’s actual client; rendered configuration passing CI does not prove that every installed editor or extension loads it.

## Keep installations current

Ask your setup agent to update the plugin checkout with a fast-forward pull, review changes, and refresh only managed, unmodified skill copies:

```bash
git pull --ff-only
python3 scripts/install_skills.py --client codex --update
npm install -g {{cup_install_spec}}
cup --version
```

The npm command installs or upgrades to the release currently tagged `latest`; it does not start an automatic updater. Ask the agent to read the bound task after an upgrade and confirm compatibility before task writes. If a new release is incompatible, report the failure and deliberately select a known working version. Do not update executables in the middle of a task write.

Replace `codex` with the installed client. For Claude marketplace installations, use the client’s plugin update flow instead. Reload the agent, review profile/dependency changes, and repeat the discovery check. **Website redeployment does not update teammates’ installed tools.**

## Optional shared integration

The plugin works without a paid integration dependency. Native GitHub activity linking and optional ClickUp automations are separate admin tasks. The repository’s reviewed guidance states that native activity linking is available on all ClickUp plans; GitHub Automation integrations require Business or above. Verify current plan/UI details in [ClickUp’s official integration guide](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration) and [automation guide](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations).

Continue with [native integration setup](github-integration.html) if the team wants activity links while agents are offline. Installing this plugin does not install a webhook or background comment worker.
