---
title: Install for your team
description: Choose a route by what your machine has, with or without Node, then verify in your agent. Browser OAuth by default.
section: Start here
---
# Install, then verify in your agent.

## Choose ClickUp and GitHub independently

**Default: hosted ClickUp + GitHub CLI.** Use official ClickUp MCP with browser-based OAuth and reuse `gh` sign-in across authorized GitHub repositories. No ClickUp desktop app, ClickUp CLI, personal ClickUp token, local helper or bridge is required. The installer checks GitHub sign-in; only the running agent can verify ClickUp OAuth and actual repository access.

Use `onboard --mode hosted --github cli` explicitly for this combination. `--mode hosted --github hosted` instead selects an existing approved hosted GitHub connection. **Strict remote-only** (`--mode remote-only`, legacy `--mode oauth`) requires both connections to be hosted and never invokes `gh`. Missing or banned selected backends mean STOP; do not automatically fall back.

**Local-helper** (`--mode local-helper`, legacy `--mode cli`) separately installs `cup`/`cu-work` and requires its own ClickUp token. Existing `setup`/`update` keep their local-helper semantics. Hosted operations use agent-instruction safeguards, outside helper receipts, locks and completion gates.

Installation does not need Node: [choose a route](#choose-an-installation-route) by what the machine has. Node 22+ is needed only for the npx route and for local-helper mode, because Krodak's `cup` is an npm package. The default GitHub backend also needs an already allowed GitHub CLI. See [modes and host constraints](modes.html).

ClickUp says it keeps an allowlist of vetted MCP clients for the official server ([ClickUp MCP server](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server), [ClickUp setup guide, 8 September 2026](https://clickup.com/blog/how-to-use-clickup-mcp-server/)); Kilo, Codex and Copilot CLI are not named on it. If the browser authorization is refused for your client, stop and report it; do not switch to a bridge or a token.

Choose the **coding agent you actually use**, not merely the editor where it runs. The default ClickUp authentication method is **browser-based OAuth**. Each teammate must configure their own agent environment and authorize their own accounts.

## Choose an installation route

The route decides how the files arrive. The [selection](#choose-clickup-and-github-independently) decides which backends the agent uses, and every route installs the **hosted** selection unless you choose otherwise. Pick the first row this machine supports. Node.js is needed only for the npx route and for local-helper mode.

| What this machine has | Route | What you run |
| --- | --- | --- |
| Only the coding agent, plus one way to fetch files (git, `gh`, curl, PowerShell, a browser download) | **A. Agent-run manual install** | Paste the prompt below into the agent |
| GitHub CLI 2.90+ | **B. `gh skill`** (preview) | `gh skill install randrescastaneda/clickup-skills --all ...`, then register the MCP |
| Python 3.11+ and a clone or ZIP | **C. Python only** | `python3 scripts/setup.py onboard --client CLIENT` |
| Claude Code | **D. The client's plugin manager** | `claude plugin marketplace add randrescastaneda/clickup-skills` |
| Node 22+ and Python 3.11+ | **E. npx** | `npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT` |

`CLIENT` is `kilo`, `codex`, `claude`, `copilot` or `vscode` (VS Code Copilot Chat, which also needs `--project-dir /absolute/path/to/project`).

**One installation covers one agent.** Each agent reads its own skills folder and settings file, so install again for every agent you use, changing only `CLIENT`. There is no all-agents option. Your `gh` sign-in is shared by all of them; the ClickUp authorization is approved once inside each agent.

**Warning: one method per agent.** Do not install the skills for the same agent with two methods (for example the npx installer and the Claude Code plugin, or `gh skill` and the Python installer), or at both user and project scope: every skill then appears twice. If the skills are already installed for that agent, upgrade them with the method that installed them, or remove that copy before installing with another method. Some agents also read other agents' skill folders, so after adding a second agent, check that each skill appears once in both.

### A. Agent-run manual install

Paste this into the coding agent:

```prompt
Install ClickUp Skills for <Kilo Code | Codex | Claude Code | Copilot CLI> on this machine.
Node.js is not available here. Read
https://raw.githubusercontent.com/randrescastaneda/clickup-skills/main/INSTALL.md
and follow it exactly. Do not write anything to ClickUp or GitHub.
Stop and ask me if anything conflicts with what is already installed.
```

The agent follows the [install runbook](install-runbook.html): it fetches a pinned source, copies the six skill folders, checks each file's SHA-256 against `skills/MANIFEST.json`, registers the official ClickUp MCP with the client's own command or an exact settings snippet, and reports. It runs no downloaded script.

### B. GitHub CLI (`gh skill`, preview)

Needs `gh` 2.90 or later. The `gh skill` command group is a preview and may change.

| Client | Install the skills (user scope) |
| --- | --- |
| Claude Code | `gh skill install randrescastaneda/clickup-skills --all --agent claude-code --scope user` |
| Copilot CLI | `gh skill install randrescastaneda/clickup-skills --all --agent github-copilot --scope user` |
| Kilo Code | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.kilo/skills"` |
| Codex | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.agents/skills"` |

Add `--pin TAG` once a release tag exists. For Kilo and Codex pass `--dir`: `gh` 2.95 writes `--agent kilo` to `~/.kilocode/skills` and `--agent codex` to `~/.codex/skills`, not the folders this project uses. Update with `gh skill update --all`, adding the same `--dir` for Kilo and Codex. `gh skill` rewrites each `SKILL.md` frontmatter, so these copies belong to `gh`.

Then register the official ClickUp MCP: `python3 scripts/setup.py onboard --client CLIENT --skip-skills` from a clone, or step 8 of the [install runbook](install-runbook.html) (the client's own command or the settings snippet).

### C. Python only

```bash
git clone https://github.com/randrescastaneda/clickup-skills.git
cd clickup-skills
python3 scripts/setup.py onboard --client CLIENT
```

On Windows: `py -3 scripts\setup.py onboard --client CLIENT`. A ZIP download works instead of the clone. The `--mode`, `--github`, `--project-dir` and `--skip-skills` flags work as with npx. Update with `git pull` (or a new ZIP) and the same command.

The command ends with one `RESULT {...}` line of JSON for agents. Exit code 3 means installed, with `gh` still needing your sign-in; the GitHub backend was not switched. `python3 scripts/setup.py status --client CLIENT` shows what is installed and changes nothing.

### D. The client's own plugin manager

**Claude Code**, with no Node:

```bash
claude plugin marketplace add randrescastaneda/clickup-skills
claude plugin install clickup-skills@clickup-skills-marketplace
```

From a local clone, use a path starting with `./`, for example `claude plugin marketplace add ./clickup-skills`. The plugin supplies the six skills and the official ClickUp MCP (`clickup_official`) only. Plugin skills are namespaced (`clickup-skills:clickup-route`), so do not also install copies in `~/.claude/skills`.

**Copilot CLI** (from vendor documentation, untested here): `copilot plugin install randrescastaneda/clickup-skills`. GitHub's plugin reference says Copilot CLI reads a root `plugin.json` with an Agent Plugins `$schema`, a root `mcp.json` and a `skills/` folder, which this repository provides.

Codex has plugin marketplaces too, but OpenAI's documentation did not confirm the file a repository needs, so Codex uses routes A, B, C or E.

### E. npx

Needs Node 22+ and Python 3.11+:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT
```

## The npx route in detail

This route needs [Node.js 22+](https://nodejs.org/), Python 3.11+ and Git; the default backend also needs GitHub CLI (`gh`). The same command works in macOS Terminal and Windows PowerShell:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

The command installs from `main`, the repository's default branch. The installer asks which agent to configure. **Press Enter for Kilo Code (default).** If you already know the agent, append the appropriate `--client` option:

| Agent you actually run | Terminal command / option |
| --- | --- |
| Kilo Code, including its VS Code extension | `onboard --client kilo` |
| Codex CLI or Codex extension | `onboard --client codex` |
| Claude Code | `onboard --client claude` |
| GitHub Copilot **CLI** | `onboard --client copilot` |
| GitHub Copilot **Chat inside VS Code**, Agent mode | `onboard --client vscode --project-dir /absolute/path/to/project` |

For every row, the full command begins with `npx --yes github:randrescastaneda/clickup-skills`. **Run it once for each agent you actually use, not for all five.** For a VS Code extension that *is* Kilo, Codex, or Claude Code, use that agent's option—not `vscode`. The working project must already exist when using `--project-dir`.

[Detailed instructions for each agent](clients.html), including which settings file changes, OAuth steps and verification commands.

**What it does:** Installs six agent skills, adds ClickUp's official remote MCP endpoint (`https://mcp.clickup.com/mcp`) to your agent configuration and verifies/reuses `gh` browser sign-in by default. No hosted GitHub MCP or manually created per-repository token is needed for that backend. Use `--mode hosted --github hosted` to select an existing hosted connection; strict `--mode remote-only` never invokes `gh`. Settings and existing server entries are preserved. Conflicting or locally edited skill copies are not overwritten.

**What it does NOT do:** It does not install Krodak's CLI, access a private ClickUp token, authenticate ClickUp in the terminal, or enable the local helper's durable journal. **ClickUp OAuth happens inside your coding agent**, not through `npx`.

If the installer finds an existing equivalent ClickUp MCP server under a different name, it reuses it rather than installing a duplicate. An existing `clickup_work` server, if present, is preserved but **is not authenticated by hosted OAuth**.

## Reload your agent and verify OAuth

Restart or reload the **selected coding agent** and send this instruction in its chat:

```prompt
Use the clickup-setup skill to verify my OAuth-based ClickUp Skills installation.
Discover the six skills and the official ClickUp MCP tools. Verify GitHub
access via the selected GitHub backend (gh by default); stop if unavailable.
Guide me through the official ClickUp MCP's browser OAuth flow only if needed.
Verify read-only access to my intended Workspace, List and task, plus my GitHub
repository. Do not create or modify any tasks, issues or PRs.
Report the authenticated servers, exact scope, and missing setup (if any).
```

**Why is the second step needed?** The terminal configures the server; only your running coding agent can complete hosted ClickUp OAuth and discover the tools and permissions. The default installer **does not install GitHub MCP**, avoiding duplicate or incompatible GitHub authentication. The default uses `gh`; `--github hosted` delegates GitHub verification to the agent. Missing selected tools stop the workflow without automatic fallback.

For client-specific verification: **Kilo:** Kilo Settings → Agent Behaviour → MCP Servers; **Codex:** `codex mcp list` and, if needed, `codex mcp login clickup_official`; **Claude Code:** `/mcp`; **Copilot CLI:** `/mcp` or `copilot mcp list`; **VS Code Copilot Chat:** open Agent mode and check available MCP servers/tools. The ClickUp connection must perform an actual authenticated **read** before you authorize writes. See [each client's exact instructions](clients.html).

With GitHub CLI selected, an older unchanged installer-owned GitHub remote in Kilo is disabled; user-owned entries are preserved. With hosted GitHub selected, existing remote entries are retained for actual authentication verification.

<details markdown="1"><summary>Already using the official ClickUp MCP?</summary>

Your existing browser OAuth session may continue to work. The installer reuses a legitimate configured endpoint without replacing your sign-in or forcing a fresh ClickUp token. Reload the agent, then ask it to verify which server was discovered.

</details>

## What is included and what is not

| Default hosted ClickUp + GitHub CLI | Local-helper mode |
| --- | --- |
| **No ClickUp API token.** Official ClickUp MCP authorizes in the agent's browser flow | Requires the ClickUp CLI's personal API token, unless it is already configured |
| Six skills + hosted ClickUp MCP + reusable `gh` sign-in | Six skills + private Python workflow + Krodak CLI + local `clickup_work` MCP |
| Agents execute operations directly, following a [guarded host issue-first protocol](clickup-github.html) | Local helper enforces project scope and records durable operation receipts when a valid binding is configured |
| Markers and read-backs reduce duplicates; no local helper journal or cross-machine exactly-once guarantee | Helper journals and OS locks cover local writes, not other machines or direct host calls |

**Both modes require task/repository access and a verified project scope.** GitHub-first links, bounded writes, and safe retry rules are required in either mode. An authorized OAuth grant may be able to write even while you are *testing reads*: agents must respect the actual approved write scope.

### Optional: install the local helper instead

To enable the stricter local helper and its synchronization worker, choose `--mode local-helper` explicitly. It needs Node 22+, because Krodak's `cup` is an npm package:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode local-helper --client kilo
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

With hosted ClickUp, an agent can read an approved binding directly; it must verify the live identity/ancestry through the official MCP. An unbound agent must ask for explicit project scope **before writing**. It must not pretend that direct host calls use the local helper journal.

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

These two commands are an **alternative** to the single bundled installer, not an extra requirement. The `--skip-skills` option preserves Vercel-owned copies. For local-helper mode append `--mode local-helper` to the second command. Use Vercel's `skills check` / `skills update -g` to maintain its copies. Avoid duplicate skill managers in the same directory.

</details>

<details markdown="1"><summary>Extra clients, project scope, and contributor setup</summary>

Use the [per-agent guide](clients.html) for Codex, Claude Code, Copilot CLI, VS Code Copilot Chat, and Kilo verification steps. For project-specific configuration supply `--project-dir /absolute/path/to/project`; VS Code MCP uses `--client vscode` and requires that flag. The agent running in the editor owns tool discovery and its OAuth authorization. Preserve existing manual customizations; conflicts stop instead of overwriting files.

For OpenCode, Posit Assistant, and special/legacy clients, use the [client setup matrix](clients.html) and manual scripts in the [repository README](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing).

<div class="setup-chooser"><label for="client-choice">Advanced client configuration</label><select id="client-choice"><option value="claude">Claude Code</option><option value="codex">Codex</option><option value="copilot">GitHub Copilot</option><option value="kilo" selected>Kilo Code</option><option value="opencode">OpenCode</option><option value="posit">Posit Assistant</option><option value="vscode">VS Code MCP</option></select><div id="client-setup" aria-live="polite"></div></div>

<noscript>Client-specific commands are available in the <a href="clients.html">client setup matrix</a>.</noscript>

</details>

## Keep installations current

For the default hosted installation, rerun the same onboarding command to refresh the hosted MCP configuration and any skills managed by the installer:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo
```

If you selected a different backend, keep the same mode and backend flags when you rerun `onboard`.

For an installed token-backed local helper, `update` keeps its previous full-runtime semantics:

```bash
npx --yes github:randrescastaneda/clickup-skills update --client kilo
```

The local helper explicitly updates its private runtime and Krodak's latest CLI. Do not update in the middle of a task write. Reload the client and verify discovery after updates. Website publication never updates local agent installations.

## Optional native ClickUp–GitHub integration

The plugin does not install a GitHub webhook, activate native ClickUp GitHub links, start a synchronizer, or create automation rules. Those are separate tasks requiring authorized administrators and possibly plan features. See [native integration setup](github-integration.html), [ClickUp's integration guide](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration), and [GitHub Automations](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations).
