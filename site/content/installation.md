---
title: Installation
description: Choose from five ways to install ClickUp Skills. Start with the recommended prompt for your own coding agent.
section: Start here
---
<div class="install-hero">
<div>
<h1 id="install-then-verify-in-your-agent">Install with your own agent</h1>
<p>Give your coding agent the setup prompt. It installs the six skills and configures ClickUp. You approve browser sign-in when prompted.</p>
<a class="install-cta" href="#a-agent-run-manual-install">Get the setup prompt</a>
</div>
<ol class="install-steps" aria-label="Recommended setup steps">
<li><span aria-hidden="true">1</span><div><strong>Paste the prompt</strong><small>Open the coding agent you use.</small></div></li>
<li><span aria-hidden="true">2</span><div><strong>Let your agent install</strong><small>It checks files and configures access.</small></div></li>
<li><span aria-hidden="true">3</span><div><strong>Sign in and verify</strong><small>Reload your agent and test read access.</small></div></li>
</ol>
</div>

## Choose from five installation methods {: #choose-an-installation-route }

<nav class="install-methods" aria-label="Installation methods">
<a class="install-method install-method-primary" href="#a-agent-run-manual-install"><span>A · Recommended</span><strong>Use your own agent</strong><small>Copy a prompt and let your agent set up the skills.</small></a>
<a class="install-method" href="#b-github-cli-gh-skill-preview"><span>B</span><strong>GitHub CLI</strong><small>Manage skills with <code>gh skill</code> (preview).</small></a>
<a class="install-method" href="#c-python-only"><span>C</span><strong>Python only</strong><small>Use the installer from a clone or ZIP.</small></a>
<a class="install-method" href="#d-the-clients-own-plugin-manager"><span>D</span><strong>Plugin manager</strong><small>Install through a supported agent’s marketplace.</small></a>
<a class="install-method" href="#e-npx"><span>E</span><strong>npx</strong><small>Run the installer with Node and Python.</small></a>
</nav>

<div class="install-note" markdown="1">
**One method per agent.** Each teammate installs for each agent they use and approves their own ClickUp sign-in. If an agent already has the skills, use the same method to update them or remove the old copy before switching.
</div>

## A. Use your own agent {: #a-agent-run-manual-install }

<p class="install-intro">Pick the agent you want to set up, then copy the prompt into its chat. Your agent needs a way to fetch the repository files, such as Git or a browser download.</p>

<div class="install-prompt" markdown="1">

<div class="install-client" id="install-client-picker" hidden>
<label for="install-client">Your coding agent</label>
<select id="install-client">
<option value="">Use my current agent</option>
<option>Kilo Code</option>
<option>Codex</option>
<option>Claude Code</option>
<option>Copilot CLI</option>
<option>VS Code Copilot Chat</option>
</select>
</div>

```prompt
Install ClickUp Skills for the coding agent I am using. Ask me which one if unclear.
Use the agent-run setup in
https://raw.githubusercontent.com/randrescastaneda/clickup-skills/main/INSTALL.md
and follow it exactly. Do not write anything to ClickUp or GitHub.
Stop and ask me if anything conflicts with what is already installed.
```

</div>

The agent follows the [install runbook](install-runbook.html), verifies all six skill folders against the SHA-256 manifest and registers the official ClickUp MCP. This method needs no Node.js or Python. [Check your agent’s requirements](clients.html) · [Verify after setup](#reload-your-agent-and-verify-oauth)

## B–E. Other installation methods

Node.js is needed only for the npx route and for local-helper mode. For the Python and npx routes, use `kilo`, `codex`, `claude`, `copilot` or `vscode` as `CLIENT`. The `vscode` option is for VS Code Copilot Chat and also needs `--project-dir /absolute/path/to/project`.

<details class="install-option" id="b-github-cli-gh-skill-preview" markdown="1">
<summary><strong>B. GitHub CLI</strong><span>gh 2.90+ · preview</span></summary>

Needs `gh` 2.90 or later. The `gh skill` command group is a preview and may change.

| Client | Install the skills (user scope) |
| --- | --- |
| Claude Code | `gh skill install randrescastaneda/clickup-skills --all --agent claude-code --scope user` |
| Copilot CLI | `gh skill install randrescastaneda/clickup-skills --all --agent github-copilot --scope user` |
| Kilo Code | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.kilo/skills"` |
| Codex | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.agents/skills"` |

Add `--pin TAG` once a release tag exists. For Kilo and Codex pass `--dir`: `gh` 2.95 writes `--agent kilo` to `~/.kilocode/skills` and `--agent codex` to `~/.codex/skills`, not the folders this project uses. Update with `gh skill update --all`, adding the same `--dir` for Kilo and Codex. `gh skill` rewrites each `SKILL.md` frontmatter, so these copies belong to `gh`.

Then register the official ClickUp MCP: `python3 scripts/setup.py onboard --client CLIENT --skip-skills` from a clone, or step 8 of the [install runbook](install-runbook.html) (the client's own command or the settings snippet).

</details>

<details class="install-option" id="c-python-only" markdown="1">
<summary><strong>C. Python only</strong><span>Python 3.11+</span></summary>

```bash
git clone https://github.com/randrescastaneda/clickup-skills.git
cd clickup-skills
python3 scripts/setup.py onboard --client CLIENT
```

On Windows: `py -3 scripts\setup.py onboard --client CLIENT`. A ZIP download works instead of the clone. The `--mode`, `--github`, `--project-dir` and `--skip-skills` flags work as with npx. Update with `git pull` (or a new ZIP) and the same command.

The command ends with one `RESULT {...}` line of JSON for agents. Exit code 3 means installed, with `gh` still needing your sign-in; the GitHub backend was not switched. `python3 scripts/setup.py status --client CLIENT` shows what is installed and changes nothing.

</details>

<details class="install-option" id="d-the-clients-own-plugin-manager" markdown="1">
<summary><strong>D. Plugin manager</strong><span>Claude Code · Copilot CLI instructions</span></summary>

**Claude Code**, with no Node:

```bash
claude plugin marketplace add randrescastaneda/clickup-skills
claude plugin install clickup-skills@clickup-skills-marketplace
```

From a local clone, use a path starting with `./`, for example `claude plugin marketplace add ./clickup-skills`. The plugin supplies the six skills and the official ClickUp MCP (`clickup_official`) only. Plugin skills are namespaced (`clickup-skills:clickup-route`), so do not also install copies in `~/.claude/skills`.

**Copilot CLI** (from vendor documentation, untested here): `copilot plugin install randrescastaneda/clickup-skills`. GitHub's plugin reference says Copilot CLI reads a root `plugin.json` with an Agent Plugins `$schema`, a root `mcp.json` and a `skills/` folder, which this repository provides.

Codex has plugin marketplaces too, but OpenAI's documentation did not confirm the file a repository needs, so Codex uses routes A, B, C or E.

</details>

<details class="install-option" id="e-npx" markdown="1">
<summary><strong>E. npx</strong><span>Node 22+ · Python 3.11+ · Git</span></summary>

<div id="the-npx-route-in-detail"></div>

The default backend also needs GitHub CLI (`gh`). The same command works in macOS Terminal and Windows PowerShell:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT
```

Omit `--client` to pick the agent interactively:

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

**ClickUp OAuth happens inside your coding agent.** The optional local helper provides a separate token-backed workflow and durable journal.

If the installer finds an existing equivalent ClickUp MCP server under a different name, it reuses it rather than installing a duplicate. An existing `clickup_work` server, if present, is preserved but **is not authenticated by hosted OAuth**.

</details>

## Reload your agent and verify OAuth

For Option A, follow your agent’s runbook handoff. For any method, reload the agent you configured and paste this prompt to check access:

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

## Choose ClickUp and GitHub independently

**Default: hosted ClickUp + GitHub CLI.** Use official ClickUp MCP with browser-based OAuth and reuse `gh` sign-in across authorized GitHub repositories.

<details class="install-option" markdown="1">
<summary><strong>Backend options and host restrictions</strong></summary>

The installer checks GitHub sign-in. The running agent verifies ClickUp OAuth and repository access.

Use `onboard --mode hosted --github cli` explicitly for this combination. `--mode hosted --github hosted` instead selects an existing approved hosted GitHub connection. **Strict remote-only** (`--mode remote-only`, legacy `--mode oauth`) requires both connections to be hosted and never invokes `gh`. Missing or banned selected backends mean STOP; do not automatically fall back.

**Local-helper** (`--mode local-helper`, legacy `--mode cli`) separately installs `cup`/`cu-work` and requires its own ClickUp token. Existing `setup`/`update` keep their local-helper semantics. Hosted operations use agent-instruction safeguards, outside helper receipts, locks and completion gates.

The default GitHub backend needs an already allowed GitHub CLI. See [modes and host constraints](modes.html).

ClickUp says it keeps an allowlist of vetted MCP clients for the official server ([ClickUp MCP server](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server), [ClickUp setup guide, 8 September 2026](https://clickup.com/blog/how-to-use-clickup-mcp-server/)); Kilo, Codex and Copilot CLI are not named on it. If the browser authorization is refused for your client, stop and report it; do not switch to a bridge or a token.

</details>

## Hosted and local-helper setup {: #what-is-included-and-what-is-not }

<details class="install-option" markdown="1">
<summary><strong>Compare hosted and local-helper setup</strong></summary>

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

</details>

## Who does what

| Role | Responsibility |
| --- | --- |
| Workspace owner/admin | Grant access to ClickUp Workspaces/Lists and optionally configure the native GitHub integration/automations |
| Repository/organization admin | Give the right teammates and GitHub App access to the intended repositories |
| Each teammate | Ask their coding agent to install the skills or choose another method, then approve **their own** browser authorizations |
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

Use the same method you installed with. For Option A, ask your agent to follow the upgrade steps in the [install runbook](install-runbook.html). For the npx route, rerun the same onboarding command to refresh the hosted MCP configuration and any skills it manages:

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
