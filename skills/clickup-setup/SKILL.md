---
name: clickup-setup
description: Install, configure, verify, or update ClickUp Skills in an agent environment. Use when a teammate asks to install ClickUp Skills, finish Vercel skills CLI installation, set up Python/Krodak CLI/MCP, or resolve installation conflicts.
---

# Set up ClickUp Skills for an agent

This skill guides **local environment setup**, not changes to remote ClickUp tasks or GitHub issues. Detect the actual agent/client (Codex, Kilo, Claude Code, Copilot, or supported VS Code configuration), whether setup is personal or project-scoped, and which steps are already complete. Explain intended changes before running installation commands. Never request or print an access token in chat.

## Recommended: guided onboarding for a new teammate

1. Check Node.js 22.20+, Python 3.11+, Git, and GitHub CLI. Tell the teammate to run this command in macOS Terminal or Windows PowerShell:

   ```bash
   npx --yes github:randrescastaneda/clickup-skills onboard
   ```

   It first asks for an agent (Kilo Code default); `--client codex`, `--client claude`, `--client copilot`, or `--client kilo` bypasses the chooser. The command installs the six skills, private Python runtime, Krodak's latest CLI, and safe MCP configuration merge. It then *checks* existing ClickUp and GitHub CLI credentials and only prompts for missing authentication. It never asks the agent to collect tokens.

2. For ClickUp, the user creates/copies their own personal token at https://app.clickup.com/settings/apps and enters it into the **ClickUp CLI's terminal prompt**. `cup auth` verifies identity. For GitHub, `gh auth login --web` handles browser authorization. Already-valid sign-ins are reused. If GitHub CLI is missing, point to https://cli.github.com/ and rerun the same command; installed state is retained.

3. Reload the agent and check **all six** skill discoveries, installed `clickup_work` MCP tools and actual GitHub MCP tools, read-only account access, and any bound project/repository scope. The hosted GitHub MCP may require its own OAuth authorization through the client's UI; `gh` login does not grant that authorization. Do not infer remote access from local success. Use `clickup-bind-project` only after the project owner supplies/approves the objective and root task. Do not create tasks or modify remote state during initial verification.

4. Report which checks passed and the smallest missing action. Native GitHub integration and automations require separate team administrator setup.

## Alternative: Vercel Skills CLI or manual setup

For teammates deliberately using the standard Skills CLI, install the skills independently:

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills setup --client kilo --skip-skills
```

The Vercel CLI does not install the Python runtime, Krodak CLI, or MCP settings. To use the guided authentication with Skills CLI-managed copies, run `npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills`. Do **not** use both installers to manage the same skill copies.

The legacy `npx --yes github:randrescastaneda/clickup-skills setup --client kilo` remains available for software-only installs and prints separate CLI authentication commands. For VS Code MCP configuration, use `--client vscode --project-dir /absolute/path/to/project`; the actual coding agent still owns skill discovery. An existing Claude marketplace plugin may already supply the skills/servers, so inspect before installing duplicates. The checkout-based Python scripts support additional/legacy clients.

## Updating without conflicting managers

For Skills CLI-managed installations, run `npx skills check` then `npx skills update -g` for personal skills (or `npx skills update -p` for project skills), **and separately** `npx --yes github:randrescastaneda/clickup-skills update --client CLIENT --skip-skills` to refresh the private Python/Krodak runtime and MCP paths. Re-run with the same project directory if relevant. For custom-installer-managed skills, only use its `update --client CLIENT` command; it refreshes those copies along with the runtime.

Never run upgrades during an active task mutation or automatically on MCP startup. Check conflicts and back up existing configuration. After an update, reload and verify tools; read the bound task again before any write.
