# Install ClickUp Skills by hand: a runbook for coding agents

You are a coding agent asked to install ClickUp Skills. Follow these steps in order. Each step has an action, a check, and a condition for stopping. When you stop, tell the user what you found and what they need to decide. This procedure needs no Node, npm, npx or Python.

## 1. Rules

- Install only for the client the user named. If you do not know it, ask.
- Never ask for, read or store a token or password.
- Never run a downloaded script. This procedure only copies Markdown, YAML and JSON files and edits one settings file.
- Never write to ClickUp or GitHub.
- An installation covers one agent. To use the skills in another agent, run this procedure again for that agent.
- Never leave two copies of the skills for the same agent: every skill would appear twice. Step 3 checks for this.
- If anything conflicts with what is already installed, stop and ask.

## 2. Inputs

| Input | Default | Notes |
| --- | --- | --- |
| Client | none: ask | Kilo Code, Codex, Claude Code, Copilot CLI or VS Code Copilot Chat |
| Scope | user | Project scope needs the absolute path of an existing project folder. VS Code Copilot Chat is project scope only. |
| GitHub backend | `gh` | An approved hosted GitHub connection only if the user says so |
| Test targets | ask, or leave for step 11 | The Workspace, List, task and GitHub repository to read in the check after the reload |
| Version | the latest release tag | Use `main` only if no tag exists. If the user names a branch or commit, use that instead. Say which in the report |

Find the latest tag with `git ls-remote --tags https://github.com/randrescastaneda/clickup-skills`, or at `https://github.com/randrescastaneda/clickup-skills/releases/latest`. Below, `TAG` is that tag (or `main`, or the branch or commit the user named; for a branch, the archive URL is `.../archive/refs/heads/BRANCH.zip`). Without a tag there is no version to match: record the commit SHA for the report instead.

## 3. Check for an existing installation

Do this before downloading anything.

1. Look for the folders `clickup-bind-project`, `clickup-github`, `clickup-handoff`, `clickup-route`, `clickup-setup` and `clickup-work-task` in the client's user skills folder and, if you are inside a project, its project skills folder (table in step 8). For Kilo also look in `~/.kilocode/skills/`, and for Codex in `~/.codex/skills/`: `gh skill` puts its copies there.
2. Claude Code only: run `claude plugin list` and look for `clickup-skills`.
3. If you find nothing, continue with step 4.
4. If you find an installation, work out which method installed it:

| Sign | Installed by | How that method upgrades it |
| --- | --- | --- |
| A `.clickup-skills.json` file in each folder | This project's installer (npx, or `python3 scripts/setup.py`) | Rerun the same `onboard --client CLIENT` command |
| `SKILL.md` frontmatter has a `metadata:` block with `github-` or `local-path` keys | `gh skill install` | `gh skill update --all`, adding `--dir FOLDER` if it was installed with `--dir` |
| The `clickup-skills` plugin is listed | The Claude Code marketplace plugin | `claude plugin update clickup-skills@clickup-skills-marketplace` |
| None of these | A manual copy made with this runbook, or `npx skills` | Step 12, or `npx skills update` |

5. **Stop.** Tell the user what you found, where, and which method installed it. Ask them to choose one:
   - **Leave it as it is.** Change nothing and end here.
   - **Remove it.** Move the six folders into a dated backup folder beside the skills folder, not inside it (for example `~/.kilo/clickup-skills-backup-DATE/`); do not delete them. Remove the plugin with `claude plugin uninstall clickup-skills@clickup-skills-marketplace`. Leave the settings file and its ClickUp server entry alone unless the user asks. Then end here, or continue with step 4 if the user also wants a fresh install.
   - **Upgrade it.** Either with the method that installed it (table above), or by switching to this manual method: remove the existing copy as described, then continue with step 4.

**Check:** before you continue, no copy of the six skills remains for this agent, in either scope or as a plugin.
**Stop** if the user has not chosen, or if a copy would remain next to the new one.

## 4. Get the source

Create a new, empty temporary folder outside any project and work there. Follow the user's own rule for temporary folders if they have one; otherwise use `$TMPDIR` on macOS and Linux, `%TEMP%` on Windows. Use the first option that works:

1. `git clone --depth 1 --branch TAG https://github.com/randrescastaneda/clickup-skills`
2. `gh repo clone randrescastaneda/clickup-skills -- --depth 1 --branch TAG`, or `gh api repos/randrescastaneda/clickup-skills/zipball/TAG > clickup-skills.zip` and extract it.
3. Download and extract the archive:
   - macOS or Linux: `curl -fL -o clickup-skills.zip https://github.com/randrescastaneda/clickup-skills/archive/refs/tags/TAG.zip` (for `main`: `.../archive/refs/heads/main.zip`), then `unzip clickup-skills.zip`.
   - PowerShell: `Invoke-WebRequest -Uri https://github.com/randrescastaneda/clickup-skills/archive/refs/tags/TAG.zip -OutFile clickup-skills.zip`, then `Expand-Archive clickup-skills.zip`.
4. Fetch `https://raw.githubusercontent.com/randrescastaneda/clickup-skills/TAG/skills/MANIFEST.json`, then each file it lists, at `https://raw.githubusercontent.com/randrescastaneda/clickup-skills/TAG/skills/SKILL_NAME/PATH`, and `.../TAG/LICENSE`.
5. A folder the user provides.

**Check:** the source has `LICENSE`, `skills/MANIFEST.json` and six folders under `skills/`, each with a `SKILL.md`. If you used a tag, the manifest's `version` matches it (without the leading `v`); otherwise note the commit SHA.
**Stop** if none of the options works, or if the check fails.

## 5. Preflight the destination

After step 3 the destination is normally empty. Find the skills folder for the client and scope in the table in step 8, and confirm it for each of the six skills:

| Destination folder | Action |
| --- | --- |
| Absent | Copy it in step 6 |
| Present, and every file matches the manifest hash | Skip it |
| Present, and any file differs or is missing | **Stop and ask.** Never merge into or overwrite an existing folder |

Ignore `LICENSE` and installer receipts (`.clickup-skills.json`) when comparing. Copies installed by `gh skill` or `npx skills` have rewritten frontmatter: they never match this manifest, and those tools verify and update them. If you find such copies, go back to step 3.

## 6. Copy

Copy each absent skill folder whole, with its subfolders, from `skills/` in the source into the destination skills folder. Copy the source `LICENSE` into each copied folder. Do not copy `skills/MANIFEST.json`.

**Check:** the six folders exist in the destination.

## 7. Verify every file

Compute the SHA-256 of each copied file and compare it with `skills/MANIFEST.json`, and the `LICENSE` copies with `license.sha256`:

- macOS or Linux, a whole folder at once: `find FOLDER -type f -exec shasum -a 256 {} +` (Linux also has `sha256sum`)
- PowerShell: `Get-ChildItem -Recurse -File FOLDER | Get-FileHash -Algorithm SHA256` (compare in lower case)

Any hashing tool already on the machine will do. Never run code from the downloaded source to do it.

**Stop** on any difference or missing file, and report it. Do not fix files by hand.

## 8. Register the official ClickUp MCP

The only server to add is the official ClickUp MCP at `https://mcp.clickup.com/mcp`, named `clickup_official`. Never add `clickup_work`, a GitHub server, or a bridge such as `mcp-remote`.

1. Open the settings file for the client and scope (table below). Look for every server whose URL is `https://mcp.clickup.com/mcp`, under any name.
2. If exactly one exists and has only `type`, `url`, `enabled`, `oauth`, `auth`, `timeout` or `tools` fields, reuse its name and add nothing. If it has other fields (headers, tokens, a command), stop and ask.
3. If two or more exist, stop and ask the user to remove the duplicates.
4. Otherwise register the server. Whichever way you use, first copy the settings file to `FILE.clickup-skills-backup-DATE`.
   - Prefer the client's own command where one is shown below. If it is not on PATH, look for the binary the client ships (the Claude Code extension for VS Code keeps it under `resources/native-binary/claude` in its extension folder), or ask the user to run the command.
   - Otherwise add the snippet's server entry inside the existing key object, keeping every other entry and comment. If the file does not exist, create it with the snippet.
   - Do not hand-edit a settings file that the running client rewrites. Claude Code rewrites `~/.claude.json` while it runs: use its command, or ask the user to close Claude Code first.
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

Native command (run once by an agent with Claude Code 2.1.332 on macOS, 26 November 2026):

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

## 9. GitHub backend

- **`gh` selected:** run `gh auth status` and report the result. Do not sign in for the user: if it is not signed in, tell them to run `gh auth login`. If `gh` is missing, tell them to install it from `https://cli.github.com/`.
- **Hosted GitHub selected:** do not touch `gh`. The user verifies the approved hosted GitHub connection in the client.
- Never switch from one backend to the other.

## 10. Report, then hand over

The read-only check needs a reloaded client, so it cannot run in this session. Finish here:

1. Report: client, scope, selection (hosted with `gh`, hosted with hosted GitHub, or remote-only), version or commit (say if it was `main`), folders copied or skipped, the result of step 7, settings file and backup path, the server name, whether you added the server entry, the `gh` state, and what the user still has to do.
2. Delete the temporary source folder.
3. Ask the user to reload the client and approve the ClickUp browser authorization:

| Client | Reload, then authorize |
| --- | --- |
| Kilo Code | **Developer: Reload Window** in VS Code; Settings → Agent Behaviour → MCP Servers |
| Codex | `codex mcp login clickup_official`; check with `codex mcp list` |
| Claude Code | Restart; `/mcp` |
| Copilot CLI | Restart; `/mcp` |
| VS Code Copilot Chat | Trust the project folder; Copilot Chat in **Agent mode**; MCP server controls |

4. Give the user this prompt for the new session, with the names filled in when you know them:

```text
Use the clickup-setup skill to run its read-only verification for CLIENT, SCOPE scope,
GitHub backend BACKEND. Do not write to ClickUp or GitHub. Check: the six clickup-* skills
are discovered, each exactly once; the official ClickUp server (https://mcp.clickup.com/mcp)
is configured once and authorized; a read of Workspace "NAME", List "NAME" and task "ID"
works; and the repository OWNER/REPO can be read. Give a pass or fail line for each check,
and what to fix for any failure.
```

ClickUp keeps an allowlist of vetted MCP clients. If the authorization is refused, stop and report it; never substitute a token or a bridge.

## 11. Verify read-only, in the new session

After the reload and the authorization, use the `clickup-setup` skill to check, read-only: the six skills are discovered, each exactly once; the ClickUp server is present once and authorized; a read of the intended Workspace, List and task works; the selected GitHub backend can read the intended repository. Ask the user for those names if they were not given. Never write during verification.

## 12. Update and uninstall

- **Update:** find the installed version by comparing the installed files with each release's manifest, newest first. Replace a folder only if all its files match a released manifest. Then repeat steps 4 to 7 for the new version.
- **Uninstall:** remove each of the six folders only if its files match a released manifest. Remove the server entry only if this procedure added it (see the install report; if unknown, ask).

## 13. Routes with fewer steps

Use these instead when the machine allows; each one replaces steps 4 to 8. Do step 3 first whichever route you use, and never combine two routes for one agent.

- **GitHub CLI 2.90+ (preview feature):** `gh skill install randrescastaneda/clickup-skills --all` plus `--agent claude-code --scope user` (Claude Code), `--agent github-copilot --scope user` (Copilot CLI), `--dir "$HOME/.kilo/skills"` (Kilo) or `--dir "$HOME/.agents/skills"` (Codex); add `--pin TAG` once a tag exists. Then step 8.
- **Python 3.11+:** in the source folder, `python3 scripts/setup.py onboard --client CLIENT` (Windows: `py -3 scripts\setup.py onboard --client CLIENT`). This runs code from the repository: use it only if the user agrees.
- **Claude Code:** `claude plugin marketplace add randrescastaneda/clickup-skills`, then `claude plugin install clickup-skills@clickup-skills-marketplace`.
- **Node 22+:** `npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT`.
