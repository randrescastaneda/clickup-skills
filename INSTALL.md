# Install ClickUp Skills by hand: a runbook for coding agents

You are a coding agent asked to install ClickUp Skills. Follow these steps in order. Each step has an action, a check, and a condition for stopping. When you stop, tell the user what you found and what they need to decide. This procedure needs no Node, npm, npx or Python.

## 1. Rules

- Install only for the client the user named. If you do not know it, ask.
- Never ask for, read or store a token or password.
- Never run a downloaded script. This procedure only copies Markdown, YAML and JSON files and edits one settings file.
- Never write to ClickUp or GitHub.
- If anything conflicts with what is already installed, stop and ask.

## 2. Inputs

| Input | Default | Notes |
| --- | --- | --- |
| Client | none: ask | Kilo Code, Codex, Claude Code, Copilot CLI or VS Code Copilot Chat |
| Scope | user | Project scope needs the absolute path of an existing project folder. VS Code Copilot Chat is project scope only. |
| GitHub backend | `gh` | An approved hosted GitHub connection only if the user says so |
| Version | the latest release tag | Use `main` only if no tag exists, and say so in the report |

Find the latest tag with `git ls-remote --tags https://github.com/randrescastaneda/clickup-skills`, or at `https://github.com/randrescastaneda/clickup-skills/releases/latest`. Below, `TAG` is that tag (or `main`).

## 3. Get the source

Create a new, empty temporary folder outside any project (`$TMPDIR` on macOS and Linux, `%TEMP%` on Windows) and work there. Use the first option that works:

1. `git clone --depth 1 --branch TAG https://github.com/randrescastaneda/clickup-skills`
2. `gh repo clone randrescastaneda/clickup-skills -- --depth 1 --branch TAG`, or `gh api repos/randrescastaneda/clickup-skills/zipball/TAG > clickup-skills.zip` and extract it.
3. Download and extract the archive:
   - macOS or Linux: `curl -fL -o clickup-skills.zip https://github.com/randrescastaneda/clickup-skills/archive/refs/tags/TAG.zip` (for `main`: `.../archive/refs/heads/main.zip`), then `unzip clickup-skills.zip`.
   - PowerShell: `Invoke-WebRequest -Uri https://github.com/randrescastaneda/clickup-skills/archive/refs/tags/TAG.zip -OutFile clickup-skills.zip`, then `Expand-Archive clickup-skills.zip`.
4. Fetch `https://raw.githubusercontent.com/randrescastaneda/clickup-skills/TAG/skills/MANIFEST.json`, then each file it lists, at `https://raw.githubusercontent.com/randrescastaneda/clickup-skills/TAG/skills/SKILL_NAME/PATH`, and `.../TAG/LICENSE`.
5. A folder the user provides.

**Check:** the source has `LICENSE`, `skills/MANIFEST.json` and six folders under `skills/`, each with a `SKILL.md`. The manifest's `version` matches `TAG` (without the leading `v`) unless you used `main`.
**Stop** if none of the options works, or if the check fails.

## 4. Preflight the destination

Find the skills folder for the client and scope in the table in step 7. For each of the six skills:

| Destination folder | Action |
| --- | --- |
| Absent | Copy it in step 5 |
| Present, and every file matches the manifest hash | Skip it |
| Present, and any file differs or is missing | **Stop and ask.** Never merge into or overwrite an existing folder |

Ignore `LICENSE` and installer receipts (`.clickup-skills.json`) when comparing. Copies installed by `gh skill` or `npx skills` have rewritten frontmatter: they never match this manifest, and those tools verify and update them. If you find such copies, stop and ask whether to keep them.

## 5. Copy

Copy each absent skill folder whole, with its subfolders, from `skills/` in the source into the destination skills folder. Copy the source `LICENSE` into each copied folder. Do not copy `skills/MANIFEST.json`.

**Check:** the six folders exist in the destination.

## 6. Verify every file

Compute the SHA-256 of each copied file and compare it with `skills/MANIFEST.json`, and the `LICENSE` copies with `license.sha256`:

- macOS: `shasum -a 256 FILE`; Linux: `sha256sum FILE` or `shasum -a 256 FILE`
- PowerShell: `(Get-FileHash -Algorithm SHA256 FILE).Hash.ToLower()`

**Stop** on any difference or missing file, and report it. Do not fix files by hand.

## 7. Register the official ClickUp MCP

The only server to add is the official ClickUp MCP at `https://mcp.clickup.com/mcp`, named `clickup_official`. Never add `clickup_work`, a GitHub server, or a bridge such as `mcp-remote`.

1. Open the settings file for the client and scope (table below). Look for every server whose URL is `https://mcp.clickup.com/mcp`, under any name.
2. If exactly one exists and has only `type`, `url`, `enabled`, `oauth`, `auth`, `timeout` or `tools` fields, reuse its name and add nothing. If it has other fields (headers, tokens, a command), stop and ask.
3. If two or more exist, stop and ask the user to remove the duplicates.
4. Otherwise use the client's own command where one is shown. If it is not available, or for the other clients, copy the settings file to `FILE.clickup-skills-backup-DATE`, then add the snippet's server entry inside the existing key object. Keep every other entry and comment. If the file does not exist, create it with the snippet.
5. **Check:** the file still parses (JSON, JSONC or TOML), and the URL appears exactly once.

<!-- clients:start -->
| Client | User skills folder | Project skills folder | User settings file | Project settings file |
| --- | --- | --- | --- | --- |
| Kilo Code | `~/.kilo/skills/` | `.kilo/skills/` | `~/.config/kilo/kilo.jsonc` | `.kilo/kilo.jsonc` |
| Codex | `~/.agents/skills/` | `.agents/skills/` | `~/.codex/config.toml` | `.codex/config.toml` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` | `~/.claude.json` | `.mcp.json` |
| Copilot CLI | `~/.copilot/skills/` | `.github/skills/` | `~/.copilot/mcp-config.json` | `.mcp.json` |
| VS Code Copilot Chat | none | `.github/skills/` | none | `.vscode/mcp.json` |

Kilo respects `XDG_CONFIG_HOME` and Codex respects `CODEX_HOME`. Kilo uses an existing project-root `kilo.jsonc` instead of `.kilo/kilo.jsonc` when there is one.

**Kilo Code**

Add this to the settings file:

```json
{
  "mcp": {
    "clickup_official": {
      "type": "remote",
      "url": "https://mcp.clickup.com/mcp"
    }
  }
}
```

**Codex**

Native command (from vendor documentation, untested here):

```bash
codex mcp add clickup_official --url https://mcp.clickup.com/mcp
codex mcp login clickup_official
```

Or add this to the settings file:

```toml
[mcp_servers.clickup_official]
url = "https://mcp.clickup.com/mcp"
```

**Claude Code**

Native command (from vendor documentation, untested here):

```bash
claude mcp add --transport http clickup_official --scope user https://mcp.clickup.com/mcp
```

Or add this to the settings file:

```json
{
  "mcpServers": {
    "clickup_official": {
      "type": "http",
      "url": "https://mcp.clickup.com/mcp"
    }
  }
}
```

**Copilot CLI**

Add this to the settings file:

```json
{
  "mcpServers": {
    "clickup_official": {
      "type": "http",
      "url": "https://mcp.clickup.com/mcp",
      "tools": [
        "*"
      ]
    }
  }
}
```

**VS Code Copilot Chat**

Add this to the settings file:

```json
{
  "servers": {
    "clickup_official": {
      "type": "http",
      "url": "https://mcp.clickup.com/mcp"
    }
  }
}
```
<!-- clients:end -->

## 8. GitHub backend

- **`gh` selected:** run `gh auth status` and report the result. Do not sign in for the user: if it is not signed in, tell them to run `gh auth login`. If `gh` is missing, tell them to install it from `https://cli.github.com/`.
- **Hosted GitHub selected:** do not touch `gh`. The user verifies the approved hosted GitHub connection in the client.
- Never switch from one backend to the other.

## 9. Hand over to the user

Ask the user to reload the client and approve the ClickUp browser authorization:

| Client | Reload, then authorize |
| --- | --- |
| Kilo Code | **Developer: Reload Window** in VS Code; Settings → Agent Behaviour → MCP Servers |
| Codex | `codex mcp login clickup_official`; check with `codex mcp list` |
| Claude Code | Restart; `/mcp` |
| Copilot CLI | Restart; `/mcp` |
| VS Code Copilot Chat | Trust the project folder; Copilot Chat in **Agent mode**; MCP server controls |

ClickUp keeps an allowlist of vetted MCP clients. If the authorization is refused, stop and report it; never substitute a token or a bridge.

## 10. Verify read-only, then report

After the reload, use the `clickup-setup` skill to check, read-only: the six skills are discovered; the ClickUp server is present once and authorized; a read of the intended Workspace, List and task works; the selected GitHub backend can read the intended repository.

Report: client, scope, selection (hosted with `gh`, hosted with hosted GitHub, or remote-only), version or commit (say if it was `main`), folders copied or skipped, settings file and backup path, the server name, whether you added the server entry, and what the user still has to do. Then delete the temporary source folder.

## 11. Update and uninstall

- **Update:** find the installed version by comparing the installed files with each release's manifest, newest first. Replace a folder only if all its files match a released manifest. Then repeat steps 3 to 6 for the new version.
- **Uninstall:** remove each of the six folders only if its files match a released manifest. Remove the server entry only if this procedure added it (see the install report; if unknown, ask).

## 12. Routes with fewer steps

Use these instead when the machine allows; each one replaces steps 3 to 7.

- **GitHub CLI 2.90+ (preview feature):** `gh skill install randrescastaneda/clickup-skills --all` plus `--agent claude-code --scope user` (Claude Code), `--agent github-copilot --scope user` (Copilot CLI), `--dir "$HOME/.kilo/skills"` (Kilo) or `--dir "$HOME/.agents/skills"` (Codex); add `--pin TAG` once a tag exists. Then step 7.
- **Python 3.11+:** in the source folder, `python3 scripts/setup.py onboard --client CLIENT` (Windows: `py -3 scripts\setup.py onboard --client CLIENT`). This runs code from the repository: use it only if the user agrees.
- **Claude Code:** `claude plugin marketplace add randrescastaneda/clickup-skills`, then `claude plugin install clickup-skills@clickup-skills-marketplace`.
- **Node 22+:** `npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT`.
