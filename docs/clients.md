# Set up your coding agent

**Choose the agent, not the editor.** For example, use the **Kilo** instructions when Kilo runs inside VS Code or Positron; use **Codex** when you run Codex there. These instructions are for local agents, not Copilot's GitHub-hosted cloud agent.

## The same two actions for everyone

**Prerequisites:** Your coding agent, Node.js 22+, Python 3.11+, Git, and [GitHub CLI](https://cli.github.com/) must be installed in the environment where the agent runs. The team must already have granted you access to its ClickUp Workspace and GitHub repository.

**Action 1 — Terminal.** Run the following from any directory in macOS Terminal or Windows PowerShell:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

Choose your agent when prompted; **press Enter for Kilo Code**. Or use one of the client-specific commands below to skip the chooser. This installs six workflow skills and the **official hosted ClickUp MCP**, reuses safe existing settings, and checks `gh` authentication. It does **not** generate or request a ClickUp personal API token. The GitHub MCP is **not** installed by default: `gh` handles GitHub operations. A separate GitHub MCP may already be built into your client or installed independently.

**Action 2 — Your coding agent.** Reload the agent and paste:

```prompt
Use clickup-setup to verify this ClickUp Skills installation. Discover all six
skills and the official ClickUp MCP. Connect it using the coding agent's browser
OAuth flow if needed. Verify read-only access to my ClickUp Workspace, List
and task, and to the intended GitHub repository using gh (or an already
working GitHub tool). Distinguish OAuth from local clickup_work authentication.
Report what passed and exactly what still needs me. Do not modify anything.
```

Only the **agent** can authorize and test ClickUp MCP OAuth. The terminal verifies `gh`, not the ClickUp browser session. Do not authorize writes solely because the MCP server appears as `connected`.

## Client-by-client instructions

### Kilo Code — verified on macOS

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo
```

- **Installed configuration:** `~/.config/kilo/kilo.jsonc` (`XDG_CONFIG_HOME` is respected). User skills go in `~/.kilo/skills/`.
- **Next:** Restart/reload Kilo. In the extension, open **Kilo Settings → Agent Behaviour → MCP Servers** (or the MCP settings panel) and check the `clickup_official` server. If it needs authorization, use the browser sign-in prompt. If the server already uses a different valid name, verify that name rather than adding a duplicate.
- **GitHub:** Kilo uses authenticated `gh` for this plugin. The GitHub remote MCP does **not** support Kilo's dynamic OAuth client registration. An unchanged legacy GitHub entry installed by this project is disabled; user-edited entries are preserved and may need manual review.
- **Acceptance status:** This client has been tested with the official ClickUp OAuth flow and a bounded GitHub-linked task pilot. A future ClickUp write still needs explicit scope/approval.

[Official Kilo MCP instructions](https://kilo.ai/docs/automate/mcp/using-in-kilo-code).

### Codex CLI or Codex extension — configuration tested; live OAuth not yet accepted

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client codex
```

- **Installed configuration:** `~/.codex/config.toml` (`CODEX_HOME` is respected); user skills go in `~/.agents/skills/`. Codex CLI and its editor extension share the MCP configuration.
- **Next:** Run `codex mcp list` to confirm `clickup_official`. If it requires OAuth, run `codex mcp login clickup_official` and complete the browser flow. In the Codex terminal UI, `/mcp` shows active servers.
- **GitHub:** Use `gh auth status` and verify actual repository reads; no extra GitHub MCP is required.

[Codex MCP documentation](https://developers.openai.com/codex/mcp). A generated configuration is **not** proof that this user's Codex session has connected.

### Claude Code — configuration tested; live OAuth not yet accepted

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client claude
```

- **Installed configuration:** `~/.claude.json`; user skills go in `~/.claude/skills/`.
- **Next:** Restart Claude Code. Use `claude mcp list` in your terminal or `/mcp` within Claude Code. Follow its browser OAuth authorization if `clickup_official` says it needs sign-in.
- **GitHub:** Use authenticated `gh` and check repository permissions. Hosted GitHub MCP is optional and has independent authorization.
- **Avoid duplicate installs:** The older Claude marketplace plugin is a separate installation route. Do **not** install both its skill/MCP copies and this installer into the same destinations.

[Claude Code MCP documentation](https://code.claude.com/docs/en/mcp). Do not treat the editor's own chat or Claude Desktop settings as the Claude Code CLI settings.

### GitHub Copilot CLI — configuration tested; live ClickUp OAuth not yet accepted

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client copilot
```

- **Installed configuration:** `~/.copilot/mcp-config.json`; user skills go in `~/.copilot/skills/`.
- **Next:** Run `copilot mcp list` or open `/mcp` in the Copilot CLI. Inspect `clickup_official` and follow any supported sign-in flow. Confirm an **authenticated ClickUp read** before performing any task work. If your Copilot CLI cannot complete OAuth, **stop** and report it; don't substitute an unverified token.
- **GitHub:** Copilot CLI already includes its own GitHub MCP, and the installer also checks your separate `gh` sign-in. Avoid installing an additional duplicate GitHub server.

[Copilot CLI MCP documentation](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers). **This target is the Copilot CLI, not VS Code Copilot Chat or Copilot's cloud agent.**

### GitHub Copilot Chat in VS Code (Agent mode) — project-scoped setup

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client vscode --project-dir /absolute/path/to/project
```

Replace the path with your **existing working repository** (quote it if it contains spaces). This is the only automatically supported VS Code MCP target; it does not configure a separate Copilot CLI session.

- **Installed configuration:** `.vscode/mcp.json` (top-level `servers`) and skills in `.github/skills/` in that project.
- **Next:** Open that folder in VS Code, approve Workspace Trust if requested, open Copilot Chat in **Agent mode**, and enable/authorize `clickup_official` in the available MCP server/tools controls. Check a read-only task call and `gh` access through the terminal tools available to the selected agent.
- **Other agents in VS Code:** If you use the Kilo extension, Codex extension, or Claude Code there, select `--client kilo`, `--client codex`, or `--client claude` instead.

[VS Code MCP instructions](https://code.visualstudio.com/docs/agent-customization/mcp-servers). Do not assume `.vscode/mcp.json` is loaded by Copilot CLI.

### OpenCode and Posit Assistant — advanced/manual, not part of automatic onboarding

**OpenCode:** The repository provides portable skills and a generic MCP renderer, **not** a verified one-command OpenCode adapter. Use the [advanced manual repository instructions](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing); verify OpenCode's current skill directories, native MCP schema, browser OAuth, and `gh` tool access before relying on it. Do not paste another client's configuration into OpenCode.

**Posit Assistant in Positron:** This is different from Kilo/Claude/Codex *running inside Positron*. Posit Assistant supports global `~/.posit/assistant/settings.json` and project `.posit/assistant/settings.json` with a top-level `mcpServers` object. For the official ClickUp endpoint, configure a remote server with `url: https://mcp.clickup.com/mcp` and `auth: "oauth"`; in Assistant run `/mcp` and select **Sign in**. The repository has an advanced `python3 scripts/configure.py --client posit --profile official` renderer, but no fully tested automatic skills installer for Posit Assistant. Verify tool discovery, skill loading and permissions manually before writes.

[Posit Assistant MCP documentation](https://assistant.posit.co/docs/reference/mcp-servers/).

## If you want the token-backed, fully scoped local helper

The default OAuth path uses agent-enforced scope, GitHub-first ordering, and duplicate checks. It **does not** have the local helper's operation journal, OS lock or scheduled sync worker. For those stricter local mechanisms, deliberately choose `--mode cli` and a client:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode cli --client kilo
```

Replace `kilo` with `codex`, `claude` or `copilot` as appropriate. The installer then provisions the private Python runtime, `@krodak/clickup-cli@latest`, and local `clickup_work` MCP. The upstream ClickUp CLI may ask you to create a **personal API token** at [ClickUp Settings → Apps](https://app.clickup.com/settings/apps). Complete that prompt **in the terminal**, never in chat, and then bind your project with verified Workspace/List/root task IDs. A running `clickup_work` server without an authenticated CLI or project binding does **not** imply full-helper readiness. Hosted OAuth does not authenticate the helper.

The older `setup --client CLIENT` and `update --client CLIENT` commands remain for advanced users and full-helper maintenance. On the OAuth-only route, rerun `onboard --client CLIENT` to refresh managed skills and hosted configuration.

## Standard Vercel Skills CLI — alternative, not an extra step

To let Vercel manage skill files and this installer manage only MCP configuration, run:

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

For Vercel-managed full-helper mode add `--mode cli` to the second command. Use `npx skills check` and `npx skills update -g` to update its copies. For a separately installed full helper use `npx --yes github:randrescastaneda/clickup-skills update --client kilo --skip-skills`. Do not install the same skill directory with both managers.

## Configuration, permissions and rollout boundaries

| Location or service | Meaning |
| --- | --- |
| Personal MCP settings | Configures **one agent on this device**, not every teammate |
| `.clickup/project.json` | Approved objective, GitHub repo/base and ClickUp Workspace/List/root task scope; **no credentials** |
| Official hosted ClickUp MCP | Authenticates with browser OAuth inside the **current agent**; a connection indicator alone is not an authorization test |
| `gh` CLI | Signs into GitHub in the current terminal environment; verify intended repository **write permission** separately |
| Native ClickUp–GitHub integration | Separate Workspace/repository administrator authorization; installing these skills does not enable it |

Settings are merged conservatively with private backups. Invalid/duplicate OAuth aliases or locally modified skill files stop installation. Unchanged previously installer-managed **Kilo** GitHub remote entries are disabled because their OAuth server cannot dynamically register Kilo; user-edited GitHub entries are preserved. In all clients, a previously configured GitHub MCP can remain present, but it is not required for the default workflow and should be checked separately.

For a working task, the agent must establish exact Workspace, home List, root ancestry and GitHub owner/repo **before any writes**, and use the [guarded official-MCP protocol](../skills/clickup-github/references/official-mcp-issue-first.md). **No automatic background work or native synchronization** is installed.

**Validation:** Kilo Code on macOS passed a real OAuth/GitHub-linked task pilot. Other agents have checked configuration formats and cross-platform offline tests, but **have not all undergone live OAuth acceptance**. A Windows Kilo installation has offline CI coverage, not live editor validation.

## Advanced or manual contributor setup

The old checkout-based scripts, alternative community MCP profiles and custom renderers remain available to contributors. They are **not** required after `onboard` and should not be presented as additional end-user steps. Consult the [repository README](https://github.com/randrescastaneda/clickup-skills#advanced-manual-installation--contributing), [execution contract](contract.html), and [validation status](validation.html) when modifying a backend or its trust model.
