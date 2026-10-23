# Team clients and editors

One set of workflow skills and executables is shared. Discovery paths and MCP
configuration belong to each agent, even when several agents run in one editor.
These adapters are based on publisher documentation checked on 2026-10-19.

## Recommended setup: browser OAuth by default

Prerequisites for macOS and Windows: Node.js 22+, Python 3.11+, Git, and GitHub CLI.

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

Select the coding agent (**Kilo Code default**) or provide `--client kilo|codex|claude|copilot`.
This installs the **six** agent skills and the hosted official ClickUp MCP
(`https://mcp.clickup.com/mcp`) plus GitHub MCP config. It validates `gh`
authentication and opens GitHub's browser flow if needed. It does **not**
install Krodak, a private Python workflow runtime, or ask for ClickUp's
personal token. A preexisting configured local `clickup_work` server is
preserved but is not authenticated through the official MCP.

Reload the selected **agent**. Complete the ClickUp MCP's independent browser
OAuth authorization when prompted and verify tool discovery, read-only
Workspace/task permissions and intended GitHub repository access. Hosted
GitHub MCP has its **own** OAuth; authenticating `gh` does not authenticate
a GitHub MCP. Only the agent's connected tools can establish live permissions.

OAuth-hosted calls are **agent-guarded** using
[the issue-first protocol](../skills/clickup-github/references/official-mcp-issue-first.md).
They bypass local helper scope enforcement, journal, OS lock, and worker.
Do not claim these guarantees or silently fall back to the CLI after an
uncertain host write.

### Explicit full local workflow (token-backed)

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode cli --client kilo
```

This installs the private Python runtime, Krodak's latest CLI, six managed
skills and the local `clickup_work` MCP. The `cup` terminal prompt accepts
the personal API token generated on ClickUp's Settings → Apps website and
verifies it. Existing valid credentials are reused. The helper's actual
task scope and receipt guarantees require a verified `.clickup/project.json`.
The old `setup --client kilo` is still software-only; `update --client kilo`
refreshes a previously installed token-backed full runtime. Re-running
`onboard --client kilo` refreshes OAuth hosted config and managed skills,
without installing the token-backed runtime.

### Alternative: standard Vercel Skills CLI

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

This lets Vercel manage **skills only** while our installer manages
hosted MCP configuration; it is an alternative, not a required extra step.
For a full local helper append `--mode cli` to the second command. Update
Vercel-managed skills with `npx skills update -g` and a separately installed
local helper with `npx --yes github:randrescastaneda/clickup-skills update
--client kilo --skip-skills`. Never let two managers edit the same skill
copies.

Project-scoped installations use `--project-dir /absolute/project`;
VS Code MCP configuration requires `--client vscode` plus that flag.
Conflicting MCP settings and locally edited skills are preserved and require
explicit resolution.

| Client | Personal configuration managed by setup |
| --- | --- |
| Kilo | `~/.config/kilo/kilo.jsonc` (respects `XDG_CONFIG_HOME`) |
| Codex | `~/.codex/config.toml` (respects `CODEX_HOME`) |
| Claude Code | `~/.claude.json`, preserving all other settings |
| Copilot | `~/.copilot/mcp-config.json` |

Project setup uses the destinations below (Codex: `.codex/config.toml`);
project Codex config may require trusting the project in Codex. Existing project
`kilo.jsonc` takes precedence over creating `.kilo/kilo.jsonc`.

Settings updates retain a private sibling backup. Managed server receipts prevent
overwriting locally changed commands. Existing GitHub servers are reused, including
an equivalent remote URL under another name. JSONC comments and unrelated TOML are
retained. Ambiguous settings stop setup. Existing default `cu-work mcp` entries
from our renderer can be migrated; custom commands require deliberate resolution.

Runtime files live under `~/.local/share/clickup-skills/` by default
(`CLICKUP_SKILLS_HOME` overrides this). Each update creates a new runtime; older
runtimes are retained so other clients and running sessions keep their paths.
No global npm install, administrator privileges, shell profile edits, or environment
activation are needed. Installed MCP commands never depend on the npx cache.

**Authentication is mode-specific.** OAuth mode authenticates ClickUp inside the coding agent; the token-backed full-helper mode uses terminal `cup init`/`cup auth`. Both require independently authenticated GitHub access. Never paste tokens into a repository, issue, PR or agent chat. Installing a plugin never activates the native ClickUp–GitHub integration.

The older scripts below remain useful for custom settings, OpenCode, Posit
Assistant, and the REST profile. They print configuration rather than merging it.

## Configuration matrix

Run `python3 scripts/configure.py --client CLIENT --profile official` to print
configuration. Merge the named servers into existing settings; do not replace
unrelated settings. Use `default`, `context`, or `rest` for another profile.

| Client | Renderer | MCP destination | Project skill directory |
| --- | --- | --- | --- |
| Codex CLI / Codex extension | `codex` | Codex `config.toml`, `[mcp_servers.*]` | `.agents/skills/` |
| Claude Code | `claude` | Project `.mcp.json`, or use this repo's marketplace plugin | `.claude/skills/` |
| VS Code MCP configuration | `vscode` | `.vscode/mcp.json`, top-level `servers` | `.github/skills/` for Copilot |
| Copilot CLI / VS Code Copilot harness | `copilot` | `~/.copilot/mcp-config.json`, or supported project `.mcp.json` | `.github/skills/` |
| Current Kilo Code | `kilo` | `.kilo/kilo.jsonc` or existing `kilo.jsonc`, top-level `mcp` | `.kilo/skills/` |
| Posit Assistant in Positron | `posit` | `.posit/assistant/settings.json`, top-level `mcpServers` | Consult the installed Assistant's skill configuration |

VS Code MCP and Copilot CLI MCP are different formats. Current Copilot harness
sessions have their own discovery; a file under `.vscode/` alone is not a
portable Copilot CLI setup. Use the renderer for the session actually running.
If GitHub MCP is already provided by your agent, omit the duplicate `github`
entry while merging the configuration.

Older Kilo releases can use legacy `.kilocode/` locations and a different MCP
shape. The `kilo` renderer targets the current documented `mcp` / command-array
format. If an installed extension still uses legacy settings, use its MCP UI to
enter the same executable/arguments or remote URLs; verify that version's skill
path before installation. Do not paste the current format into a legacy file.

## Install the shared skills

For personal skills, run the installer from this checkout with the agent name:

```bash
python3 scripts/install_skills.py --client copilot
python3 scripts/install_skills.py --client kilo
python3 scripts/install_skills.py --client claude
python3 scripts/install_skills.py --client codex
```

Each teammate installs only the clients they use. To install in a project:

```bash
python3 scripts/install_skills.py --client copilot --scope project --project-dir /absolute/project
```

The default is a standalone copy, so it works without symlink privileges on
Windows. Copies include our MIT license. After updating the checkout, rerun
with `--update` to refresh managed copies that have not been locally modified.
Conflicts are checked before any skill is installed. `--method link` is an
optional alternative for local development. Avoid installing duplicate copies
of the same skills through both a marketplace plugin and personal directories.

## VS Code and Positron

Use the adapter for the agent you run, not merely the editor's name. Codex and
Claude Code can run in a terminal inside either editor. Kilo's own configuration
belongs to Kilo, and the Posit Assistant configuration belongs to Posit Assistant.
Positron's available extensions and Assistant capabilities can differ from VS
Code; confirm the installed extension rather than assuming feature parity.

Every local stdio process still needs `cu-work` on its executable PATH, plus
`cup` or the configured REST MCP runtime for helper task operations. Installing
an editor plugin does not install those executables or authenticate ClickUp.
Remote official MCP uses each person's OAuth sign-in. Project config stores
environment-variable references; renderers never substitute secret values.

## Verification status

Offline tests validate all seven rendering targets across four profiles, the
environment-reference syntax, skill paths, repeated installation, collision
handling, and updates that preserve local changes. Linux/macOS/Windows CI runs
these checks. An actual installed agent must still discover the six skills,
list/call its MCP tools, and complete the live task/PR pilot. Configuration
contract tests are not a claim that every editor/extension version was opened.

## Publisher references

- [VS Code skills](https://code.visualstudio.com/docs/agent-customization/agent-skills)
- [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
- [Copilot CLI MCP configuration](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers)
- [Kilo skills](https://kilo.ai/docs/customize/skills)
- [Kilo MCP](https://kilo.ai/docs/automate/mcp/using-in-kilo-code)
- [Posit Assistant MCP](https://assistant.posit.co/docs/reference/mcp-servers/)
- [Positron extensions](https://positron.posit.co/extensions.html)
- [Codex MCP](https://developers.openai.com/codex/mcp/)
- [Claude plugin reference](https://code.claude.com/docs/en/plugins-reference)
