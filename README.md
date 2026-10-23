# ClickUp Skills

[Documentation and team setup](https://randrescastaneda.github.io/clickup-skills/) · [Agent usage examples](https://randrescastaneda.github.io/clickup-skills/examples.html)

Give coding agents one project objective and ClickUp task scope, then keep their
implementation, subtasks, progress, and GitHub PRs connected to that scope.

**Default:** use ClickUp's official browser-OAuth MCP through your coding agent
and authenticated `gh` for GitHub. The optional local `cu-work` helper uses
Krodak's CLI and a separate personal-token sign-in to enforce project scope,
record durable receipts and run a bounded sync worker. Other community MCPs are
advanced options, not required installation steps.

## What is included

| Component | Purpose |
| --- | --- |
| Six portable skills | Bind a project, route tools, work a task, link GitHub, resume/handoff |
| Optional `cu-work` CLI | With `--mode cli`: enforce scope, create GitHub-associated subtasks, link issues/PRs, sync discussions, and gate completion |
| Optional `clickup_work` MCP | With `--mode cli`: the same nine local-helper tools; hosted OAuth does not authenticate it |
| Optional `sync-worker` | Preview or poll comments for explicit linked tasks on one authenticated machine |
| Claude Code marketplace + portable/Codex manifests | Team installation from this repository |
| Copilot, Kilo, VS Code, and Posit adapters | Render each client's own MCP format from the same profiles |
| Optional MCP profiles | Official ClickUp, rich-context community MCP, and REST community MCP |
| Optional GitHub MCP configuration | Advanced agent-specific option; default onboarding uses authenticated `gh` |

There is no paid integration dependency. ClickUp/GitHub service permissions,
rate limits, plan features, and your model provider's charges still apply.

## Recommended: browser OAuth in two actions

**Prerequisites:** Node.js 22+, Python 3.11+, Git, and [GitHub CLI](https://cli.github.com/). Run in macOS Terminal or Windows PowerShell:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard
```

The installer asks which coding agent to use (**Kilo Code is the default**). It installs six portable skills, configures **ClickUp's official hosted MCP**, and verifies GitHub CLI sign-in. It uses authenticated **`gh` for GitHub in all clients**; a GitHub MCP is optional and must be authenticated separately. Existing agent settings are preserved. It does **not** ask for a ClickUp personal API token or install the Krodak CLI. [See the exact command and authorization steps for Kilo, Codex, Claude Code, Copilot CLI and VS Code Copilot Chat](docs/clients.md).

**Then reload your coding agent and paste:**

```prompt
Use the clickup-setup skill to verify the six skills, my official ClickUp
MCP OAuth connection, GitHub tools, and read-only Workspace/task access.
Guide me through browser authorization only if needed. Do not change
anything. Report exactly what is connected and what is missing.
```

Only the running agent can authorize the hosted OAuth connection. For direct official-MCP writes, the [guarded issue-first protocol](skills/clickup-github/references/official-mcp-issue-first.md) requires verified Workspace/List/root/repository scope, a confirmed GitHub target before task creation, duplicate-marker checks, read-backs, and safe recovery. **These are agent-enforced checks**, not local transaction guarantees.

### Optional: full local helper with durable receipts

The stricter local workflow requires independent ClickUp CLI authentication and a valid project binding. Enable it **explicitly**:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode cli --client kilo
```

This installs our private Python workflow, Krodak's `@krodak/clickup-cli@latest`, and the local `clickup_work` MCP. If needed, the terminal guides a **personal API token** sign-in from [ClickUp Settings → Apps](https://app.clickup.com/settings/apps). The token-based helper cannot borrow the official MCP's OAuth session. Conversely, its durable receipts, scoped mutations, and shared OS lock do **not** apply when an agent calls the hosted MCP directly.

The earlier software-only `setup --client kilo` and full-runtime `update --client kilo` commands remain supported. An OAuth-only installation refreshes configuration/managed skills by rerunning `onboard --client kilo`. Existing local `clickup_work` settings are not removed or authenticated by switching to OAuth.

### Alternative: manage skills through Vercel

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

This is an **alternative** to the one-command bundled installer, not an additional mandatory step. `--skip-skills` leaves Vercel's copies intact. Add `--mode cli` to the second command if you deliberately want the local helper. Update Vercel copies using `npx skills check` and `npx skills update -g`, and update the local helper (if installed) with `npx --yes github:randrescastaneda/clickup-skills update --client kilo --skip-skills`. Do not let two installers manage the same skill directory.

For project-scoped agents add `--project-dir /absolute/project`. VS Code's MCP configuration uses `--client vscode` and that flag. Onboarding neither modifies remote tasks nor enables ClickUp's native GitHub integration. Full instructions: [team installation](https://randrescastaneda.github.io/clickup-skills/installation.html).

## Advanced manual installation / contributing

The checkout-based route remains available for contributors and custom clients.

Python 3.11+ is required. The preferred CLI also requires Node 22+. Authenticate
with each teammate's own accounts; do not share a token through this repository.

```bash
git clone https://github.com/randrescastaneda/clickup-skills.git
cd clickup-skills
python3 -m pip install -e .
npm install -g @krodak/clickup-cli@latest
cup init
cup auth
# Install GitHub CLI through its official distribution, then:
gh auth login
```

The CLI follows the publisher’s `latest` release tag when installed or updated.
Existing installations do not update themselves: ask your setup agent to rerun
`npm install -g @krodak/clickup-cli@latest`, check `cup --version`, and verify a
read of the bound task before resuming writes. The version in `upstreams.lock.json`
is a reviewed compatibility baseline, not a restriction on CLI upgrades.

Use a virtual environment or `pipx` if your system Python is externally managed.
Keep the `cu-work` executable on the PATH inherited by your coding agent.
This repository is public. Each teammate still needs access to the working GitHub repository and ClickUp Workspace.

Claude Code:

```text
/plugin marketplace add randrescastaneda/clickup-skills
/plugin install clickup-skills@clickup-skills-marketplace
```

This **advanced marketplace path is separate from the recommended OAuth
onboarding** and may configure the local workflow MCP and a GitHub MCP. It does
not install or authenticate the Python/Krodak runtime. Prefer `onboard --client
claude` for browser-OAuth-only setup; do not install duplicate skills or servers.
Installing the marketplace plugin does not grant Workspace/repository access.

Codex and OpenCode can use the same portable skills:

```bash
python3 scripts/install_skills.py --client codex
# Or: python3 scripts/install_skills.py --client opencode
python3 scripts/configure.py --client codex --profile default
```

Merge the printed TOML into your Codex MCP configuration; the script never edits
your configuration. Restart/reload the client if needed. The skill installer
copies the same six skills and their license, and refuses conflicting or locally
modified skills. Use `--update` to refresh unmodified managed copies after updating
this checkout, or opt into `--method link`. Clients supporting portable Agent Plugins can install the root
`plugin.json`/`mcp.json` package directly.

For GitHub Copilot and Kilo Code:

```bash
python3 scripts/install_skills.py --client copilot
python3 scripts/configure.py --client vscode --profile official
# Copilot CLI / VS Code's Copilot harness has its own config format:
python3 scripts/configure.py --client copilot --profile official

python3 scripts/install_skills.py --client kilo
python3 scripts/configure.py --client kilo --profile official
```

The same skills and executables work with an agent run from VS Code or Positron;
the agent/client controls discovery and authentication. Posit Assistant has a
separate MCP settings format (`--client posit`). See the
[client setup matrix](docs/clients.md) for paths, version differences, and which
parts have been tested. Configuration checks do not prove installed-client behavior.

## Bind each working project

**OAuth-first installation:** The agent uses the official ClickUp MCP to verify the project scope, then writes the approved `.clickup/project.json` locally. No `cu-work` binary, personal token or helper journal is needed. Ask your agent:

```prompt
Bind this working repository to ClickUp Skills. Verify its GitHub origin and
base branch, my ClickUp Workspace, home List, and approved root task IDs.
Ask me for missing facts, read any existing binding, and make only the local
binding after verification. Do not create or modify remote tasks.
```

**Advanced: token-backed full helper only (`--mode cli`).** The following `cu-work` commands require the separately installed local helper and its authenticated CLI. Run them in the repository you want the agent to work on, not in this plugin checkout:

```bash
cu-work --project-dir /absolute/path/to/project init \
  --name 'Poverty dashboard' \
  --objective 'Deliver the approved dashboard with verified data' \
  --workspace 1234567 --list 901234567890 --task 86native \
  --repository your-team/your-project
cu-work --project-dir /absolute/path/to/project task
cu-work --project-dir /absolute/path/to/project doctor
```

The IDs above are examples. Use native ClickUp IDs; the binding skill can resolve
task links/custom IDs with a read tool. `init` creates `.clickup/project.json`
without remote writes. `task` verifies the actual task's workspace, home list,
and ancestry. Commit the binding if its identifiers/objective are appropriate for
the project's audience. It contains no credentials.

Repeat `--task` to bind multiple roots in the same home list. Different lists
need separate bindings/worktrees in this version. Edit the binding's
`github.status_map` using the list's exact status names before changing phases.
See [the example binding](examples/project.json).

Tell the agent:

> Use this project's ClickUp binding. Work on task 86native toward the recorded
> objective, create subtasks only where useful, keep progress current, and link
> the resulting GitHub PR. Put ready work in review; mark done only after the
> acceptance criteria, merge, and latest-head checks are verified.

For automatic discovery, add the short instruction from `clickup-bind-project`
to the working project's existing AGENTS.md / CLAUDE.md. Installation alone does
not force every agent to load a skill in every repository.

## Advanced: choose a local-helper backend

| Profile / backend | Use | Execution |
| --- | --- | --- |
| `cup` | Ordinary task operations with compact JSON/file-based text | Directly by `cu-work`; default runtime |
| `rest-mcp` | Free Python MCP with broad API operations | Directly by `cu-work`, or host tools |
| `context-mcp` | Rich task context, comments, images | Host tools; optional read-minimal profile |
| `official` | Default OAuth mode: agent reads/writes directly through ClickUp's official MCP | Host tools; **not** executed through `cu-work` |
| `github-cli` / `github-mcp` | PRs, repository state, issues, and checks | `gh` in helper, or host GitHub tools |

```bash
cu-work --project-dir /absolute/project route task.context --available cup,context-mcp,official
python3 scripts/configure.py --client claude --profile context
python3 scripts/configure.py --client codex --profile official
```

`route` is a deterministic recommendation over the capabilities you supply. It
does not benchmark servers, inspect the host inventory, or execute the selected
tool. The agent discovers the actual MCP schemas and applies scope checks. Enable
only the profiles you need; merge their named servers into your client settings
without removing other servers. When using a Claude plugin, avoid registering its
default `clickup_work`/`github` servers a second time under global/project settings.

To execute the local helper through the alternative free MCP:

```bash
python3 -m pip install 'clickup-rest-mcp==2026.10.15.1'
```

Set `CLICKUP_API_KEY` (or `CLICKUP_API_KEY_FILE`) and `CLICKUP_TEAM_ID` in your
private environment, then set `routing.runtime` to `rest-mcp` in the binding.
The helper launches the installed executable, never installs it during a task
write. The rich-context profile pins `@hauptsache.net/clickup-mcp@1.9.0` and
defaults to read-minimal; its available write tools must not be assumed.

With no shell, the skills can use existing ClickUp/GitHub MCP tools directly.
They must enforce the same scope and completion checks themselves. Those calls
are not proxied or journaled by `cu-work`. See [the execution contract](docs/contract.md).

## Daily workflow

**In OAuth mode, ask the coding agent in plain language** to read the approved task, verify GitHub targets before new subtasks, record progress and link PR evidence. The agent follows the [guarded issue-first protocol](skills/clickup-github/references/official-mcp-issue-first.md), but does not have the local helper's durable receipts or worker.

**Advanced full-helper mode (`--mode cli`)** — only here do the `cu-work` commands below apply:

```bash
cu-work --project-dir /absolute/project focus --task 86native
cu-work --project-dir /absolute/project subtask --task 86native \
  --title 'Validate input data' --description-file /tmp/subtask.md --key '86native:validate:v1'
cu-work --project-dir /absolute/project progress --task 86native \
  --message-file /tmp/progress.md --key '86native:validation-passed:v1'
# Create the PR with gh or GitHub MCP first, then:
cu-work --project-dir /absolute/project link-pr --task 86native --pr 42 --key '86native:pr42:link:v1'
cu-work --project-dir /absolute/project sync-comments --task 86native
cu-work --project-dir /absolute/project phase --task 86native --phase review --key '86native:review:v1'
# After acceptance, merge, and CI verification:
cu-work --project-dir /absolute/project phase --task 86native --phase done --pr 42 \
  --verification-file /tmp/verification.md --key '86native:pr42:done:v1'
```

Reuse a key only for identical inputs. New progress needs a new key. Multiline
text is passed through files or structured MCP arguments, not shell interpolation.
Prefer explicit task IDs for parallel work. Local focus/receipts are isolated per
Git worktree, not per agent session; agents sharing a worktree share state.

`link-pr` preserves unrelated PR text and records the link on both systems. A
partial failure is resumed one side at a time. A task is not completed merely
because a PR exists. Completion requires a linked, merged, non-draft PR targeting
the bound base, successful PR-head checks, and a supplied verification summary.
No checks is allowed only with an explicit `require_checks=false` project policy.
The helper records the agent's acceptance evidence; it cannot judge its truth.

Every new subtask receives a GitHub target before creation: an existing bound
repo/issue/PR supplied by `--github-target`, or a new/reused issue by default.
`link-github --target URL` associates existing tasks. Progress includes both
systems' URLs and mirrors to associated issue/PR discussions. `sync-comments`
reconciles human discussion snapshots with source links, deduplication, and echo
suppression; it does not change statuses or run in the background.

Follow the [team setup wiki](docs/wiki/README.md) for native GitHub activity links,
optional ClickUp Automations, host-MCP execution, and synchronization limits.
Native integration is available on all ClickUp plans; GitHub Automation
integrations require Business or above. Free MCP software does not remove plan
limits. No native ClickUp–GitHub connection, webhook, running background worker,
merge, or deployment is installed automatically. Official ClickUp MCP OAuth
is authorized separately inside the agent.

An optional [comment-sync worker](docs/sync-worker.md) can poll explicitly listed
tasks when agents are offline. It defaults to a read-only preview; `--apply
--watch` starts bounded polling on the authenticated machine. No service starts
during setup. Default upstream readers stop at 25 comments. An explicit
`routing.comment_reader = clickup-api` override provides complete, GET-only
comment pagination with private environment credentials; writes keep using
the selected CLI/MCP. Live worker acceptance remains unfinished.

Current delivered behavior and rollout gaps are recorded in
[project decisions](docs/project-decisions.md).

## Verify and contribute

```bash
python3 scripts/check.py
```

Checks cover cross-project isolation, uncertain writes, repeated calls, partial
ClickUp/GitHub linkage, completion gates, subprocess argument safety, MCP stdio,
client metadata, and configuration rendering. They use offline fixtures and never
touch a real workspace. See [validation notes](docs/validation.md) for the live
pilot results and remaining client acceptance steps.

The original implementations are credited in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
Reviewed commits/package versions and preserved MIT notices are in
`upstreams.lock.json` and `third_party/`. Upstream tools are dependencies; this
repository owns project context, routing policy, skills, and workflow coordination.
