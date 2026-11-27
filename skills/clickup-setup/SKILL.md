---
name: clickup-setup
description: Install, verify, update or repair ClickUp Skills for Kilo Code, Codex, Claude Code, Copilot CLI or VS Code Copilot Chat, with or without Node. Choose hosted ClickUp with GitHub through gh or a hosted connection, strict remote-only, or the optional local helper. Use for onboarding, safe MCP configuration and diagnosing setup.
license: MIT
compatibility: Any agent that loads Agent Skills. Scripted routes need Python 3.11+ or gh 2.90+; Node 22+ only for npx and local-helper mode. Configures the official ClickUp MCP; GitHub through gh or an approved hosted connection.
---

# Guided ClickUp Skills setup

Select the ClickUp mode and the GitHub backend independently. Preserve existing settings, customized skills, skills managed by another installer, and authorized sessions. Keep credentials out of chat and Git: never request, read or copy a personal access token. The user's agent, not this skill, performs hosted ClickUp OAuth. Native ClickUp–GitHub integration is separate from the coding agent's GitHub access.

## 1. What does the user want?

| Request | What to do | Writes |
| --- | --- | --- |
| Verify only | Run the checklist in section 4 | Nothing anywhere |
| Install | Confirm the client and the scope (user, or project with an absolute path); check for an existing installation (below); choose a route from section 3; then section 4 | Skills folder and one settings file |
| Update | Rerun the same route with the same flags; then section 4 | Only unmodified managed copies |
| Repair | Diagnose with section 4, then the smallest fix the user approves | Local files only |

Verify and repair never write to ClickUp or GitHub. Confirm the actual coding agent before installing: choose the agent, not the editor it runs in.

An installation covers one agent. Each agent has its own skills folder and settings file, so a second agent needs its own installation; there is no all-agents option. The `gh` sign-in is shared; the ClickUp authorization is approved once in each agent.

Before installing by any route, check whether the skills are already installed for that agent: `python3 scripts/setup.py status --client CLIENT` when Python is available, otherwise step 3 of [`references/manual-install.md`](references/manual-install.md). If they are, stop and ask the user to choose: leave the installation as it is, remove it, or upgrade it. Upgrade with the method that installed it, or remove that copy first and then install with another method. Never leave two copies for one agent.

## 2. Which backends?

| Selection | ClickUp | GitHub | `onboard` flags |
| --- | --- | --- | --- |
| **hosted** (default) | Official OAuth MCP | `gh` | none, or `--mode hosted --github cli` |
| **hosted** + hosted GitHub | Official OAuth MCP | An approved hosted connection | `--mode hosted --github hosted` |
| **remote-only** | Official OAuth MCP | Approved hosted connection only; never `gh` | `--mode remote-only` |
| **local-helper** | Separate `cup` / `cu-work` runtime with a personal token | `gh` | `--mode local-helper` |

`--mode oauth` and `--mode cli` are legacy aliases of `remote-only` and `local-helper`. Contradictory selections are rejected before anything is written.

The official MCP lives at `https://mcp.clickup.com/mcp`. Hosted ClickUp never installs or authenticates `cup`, `cu-work`, the ClickUp app or a bridge, and never asks for a ClickUp token. `npx mcp-remote` is a local bridge, so it never counts as a hosted connection.

## 3. Install routes

Pick the first route the machine supports. Always pass the client explicitly: `CLIENT` is one of `kilo`, `codex`, `claude`, `copilot`, or `vscode` (VS Code Copilot Chat, which needs `--project-dir /absolute/project`).

| Route | Needs | Command |
| --- | --- | --- |
| A. Agent-run manual install | A way to fetch files | Follow [`references/manual-install.md`](references/manual-install.md) step by step (the same text as `INSTALL.md`) |
| B. GitHub CLI (preview) | `gh` 2.90+ | `gh skill install randrescastaneda/clickup-skills --all` with the target below, then register the MCP as in route A, or with route C plus `--skip-skills` |
| C. Python only | Python 3.11+ and a clone or ZIP | `python3 scripts/setup.py onboard --client CLIENT` (Windows: `py -3 scripts\setup.py onboard --client CLIENT`) |
| D. Claude Code plugin | Claude Code and git | `claude plugin marketplace add randrescastaneda/clickup-skills`, then `claude plugin install clickup-skills@clickup-skills-marketplace` |
| E. npx | Node 22+ and Python 3.11+ | `npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT` |

Route B targets: `--agent claude-code --scope user`, `--agent github-copilot --scope user`, `--dir "$HOME/.kilo/skills"` for Kilo and `--dir "$HOME/.agents/skills"` for Codex. `gh` 2.95 puts `--agent kilo` and `--agent codex` in other folders. Update with `gh skill update --all`, adding the same `--dir`.

Routes C and E take the flags from section 2 and `--project-dir /absolute/project` for project scope. They end with one `RESULT {...}` line of JSON: `status` is `ready` or `action-needed`, and `next` lists what the user still has to do. Exit code 3 means installed, with the selected GitHub backend (`gh`) still needing the user; it is not a failure, and the backend was not switched. Use `--skip-skills` when another installer (`gh skill`, `npx skills`) owns the skill copies. `setup` and `update` remain local-helper commands.

- Use one method per agent, and one scope (user or project). Two installers must never manage the same skill folder, and Claude Code plugin skills are namespaced, so a second copy in `~/.claude/skills` makes every skill appear twice.
- The installer validates an existing official-server entry under another name before reusing it, reuses that name, and refuses duplicates. Do the same by hand in route A.
- With the default `gh` backend, the installer checks the existing sign-in and offers GitHub's browser login when needed. If `gh` is missing, report the prerequisite; never install it silently or change the selected backend.
- One `gh` sign-in serves every authorized repository. Do not create a token per repository.

## 4. Verify after any route

With Python and the plugin source, `python3 scripts/setup.py status --client CLIENT [--project-dir DIR]` prints the skills' states, the settings file, the official-server names, the recorded selection and the `gh` sign-in, and changes nothing. The source is a clone or ZIP of the installed release or a later one; installers before version 0.2.0 have no `status` command. For a skill without an installer receipt, `unmanaged-identical` means it matches that source and `unmanaged-different` means another version or local edits.

Route A deletes its source after installing, so no installer stays on the machine. That is expected, not a missing file. To check a route A copy, get the source again and compare hashes (steps 4 and 7 of [`references/manual-install.md`](references/manual-install.md)), or run `status` from it. Never run npx or another installer to check or repair a route A copy: `onboard` would put a second method on the same folders.

1. Reload the client. On Kilo VS Code, use **Developer: Reload Window** and a fresh task, then compare the skill loader's bodies with the installed files: the observed 7.8.18 backend cached old bodies despite a new task. Do not delete caches or copies speculatively.
2. Discover the six skills and the real MCP tool schemas.
3. Check that the official ClickUp server is configured exactly once. Reuse an existing alias with the same URL; refuse duplicates.
4. Authorize OAuth in the client (section 5).
5. Make an authenticated read of the intended Workspace, List and root task ancestry. A connected or configured server alone proves nothing.
6. Verify the selected GitHub backend with a read of the exact repository: `gh` or the approved hosted connection.

A successful terminal install proves only software and configuration, not hosted OAuth or task permission. Never write a task during verification.

## 5. Authorize ClickUp in each client

| Client | Where to authorize and check |
| --- | --- |
| Kilo Code | Settings → Agent Behaviour → MCP Servers |
| Codex | `codex mcp list`; when needed `codex mcp login clickup_official` |
| Claude Code | `/mcp` |
| Copilot CLI | `/mcp` or `copilot mcp list` |
| VS Code Copilot Chat | Trusted project, **Agent mode**; installed with `--client vscode --project-dir /absolute/project` |

If a client's browser flow is unsupported or fails, stop and report it. Never improvise static credentials.

ClickUp keeps an allowlist of vetted MCP clients, so a refused authorization can mean the client is not on it. Report that; do not work around it.

## 6. Hosted GitHub and remote-only

These selections never invoke `gh` authentication. Verify an approved existing hosted GitHub connection with real repository, issue, PR and check tools. Kilo's earlier GitHub OAuth attempt through dynamic client registration failed; that does not establish incompatibility with every supported authentication method. Do not create credentials or apps, or broaden organization access, without explicit authorization.

A missing or banned selected connection means STOP. Remote-only forbids `gh`.

## 7. Local-helper mode

Local-helper mode needs Node, because Krodak's `cup` is an npm package: use route E with `--mode local-helper`. It installs the private Python runtime, the Krodak CLI and `clickup_work`, and uses `gh` for GitHub.

- The personal-token flow (`cup init`, then `cup auth`) happens in the terminal, never in chat.
- ClickUp CLI token authentication is separate from hosted OAuth. Hosted OAuth is never imported into `cup`.
- Helper receipts, OS locks and completion checks require a valid project binding. They do not protect direct hosted calls.
- Never use a preserved local helper as a hosted ClickUp fallback.
- Never replay an uncertain write through another backend.

## 8. Native integration and first writes

Prefer configured native ClickUp–GitHub activity linking and approved automations, for their actual coverage. They do not expose GitHub operations to the agent through the ClickUp MCP, and they do not synchronize every comment. Use the selected GitHub backend for direct issue and PR edits, code review and CI verification. Establish one owner for issue creation and comment mirroring, to avoid duplicates.

Before any hosted write, load the guarded protocol in the sibling skill `clickup-github`, file [`references/official-mcp-issue-first.md`](../clickup-github/references/official-mcp-issue-first.md). Verify the exact scope, the GitHub target, complete duplicate reads, bounded writes, read-back and uncertain outcomes. These are agent safeguards, outside helper journals, locks and gates.

- Do not update tools in the middle of task writes.
- Native connections, automations and permanent workers need separate setup by the people who administer them.
- Each teammate signs in with their own accounts.

## Report

Report the discovered skills and tools, the authenticated identities, missing permissions, and exactly which component needs action. Never call `clickup_work` authenticated merely because it starts.
