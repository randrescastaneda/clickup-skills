---
name: clickup-setup
description: Install, configure, verify, or update ClickUp Skills in an agent environment. Use when a teammate asks to install ClickUp Skills, finish Vercel skills CLI installation, set up Python/Krodak CLI/MCP, or resolve installation conflicts.
---

# Set up ClickUp Skills for an agent

This skill guides **local environment setup**, not changes to remote ClickUp tasks or GitHub issues. Detect the actual agent/client (Codex, Kilo, Claude Code, Copilot, or supported VS Code configuration), whether setup is personal or project-scoped, and which steps are already complete. Explain intended changes before running installation commands. Never request or print an access token in chat.

## Standard skills installation (recommended for Skills CLI users)

1. Confirm Node.js **22.20+**, Python **3.11+**, and Git are available. The Vercel `skills` CLI discovers each `skills/<name>/SKILL.md` in this repository. From the working project, or with `-g` for personal skills across projects, run:

   ```bash
   npx skills add randrescastaneda/clickup-skills -g
   ```

   Let the teammate choose the applicable agent. For non-interactive setup, add `-a codex`, `-a kilo`, `-a claude-code`, or `-a github-copilot` and `-y` as appropriate. The Skills CLI installs **skill files only**; it does not install the Python runtime, Krodak's CLI, or MCP configuration.

2. Complete local setup for the **same** agent without touching the Skills CLI-managed copies. Example for Kilo:

   ```bash
   npx --yes github:randrescastaneda/clickup-skills setup --client kilo --skip-skills
   ```

   Replace `kilo` with `codex`, `claude`, or `copilot`. For VS Code MCP configuration, use `--client vscode --project-dir /absolute/path/to/project`; the chosen agent still owns skill discovery. The installer creates a persistent private Python runtime, installs `@krodak/clickup-cli@latest`, and safely merges MCP settings. It does not depend on the transient npx cache for the installed MCP. `--skip-skills` also works for `update`.

3. **Alternative for a new teammate who wants a single command:** run `npx --yes github:randrescastaneda/clickup-skills setup --client CLIENT` instead. That installer also manages skill copies. Do **not** mix the two skill managers for the same destination. If the Skills CLI already installed the skills, use `--skip-skills` rather than overwriting or deleting those copies. An existing Claude marketplace plugin may already supply skills and servers; inspect it before installing duplicates.

## Authentication and checks

- Install GitHub CLI from https://cli.github.com/ if missing. Each teammate signs in locally, with their own accounts, using `npx --yes github:randrescastaneda/clickup-skills cup init`, `npx --yes github:randrescastaneda/clickup-skills cup auth`, and `gh auth login` as needed. Do not copy or collect tokens. A host GitHub MCP does **not** replace the local helper's requirement for `gh`.
- Reload the agent. Verify installed skill discovery, the `clickup_work` MCP tools, GitHub access, and an authorized ClickUp task read. Do not infer remote access from a successful local installation. Use `clickup-bind-project` only after the project owner supplies or approves the objective and root task.
- Report which steps actually passed and what still needs the teammate's sign-in, permissions, or project information. Do not create tasks or change remote status during setup.

## Updating without conflicting managers

For Skills CLI-managed installations, run `npx skills check` then `npx skills update -g` for personal skills (or `npx skills update -p` for project skills), **and separately** `npx --yes github:randrescastaneda/clickup-skills update --client CLIENT --skip-skills` to refresh the private Python/Krodak runtime and MCP paths. Re-run with the same project directory if relevant. For custom-installer-managed skills, only use its `update --client CLIENT` command; it refreshes those copies along with the runtime.

Never run upgrades during an active task mutation or automatically on MCP startup. Check conflicts and back up existing configuration. After an update, reload and verify tools; read the bound task again before any write.
