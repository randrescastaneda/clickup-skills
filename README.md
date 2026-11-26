# ClickUp Skills

## Choose ClickUp and GitHub independently

**Default: hosted ClickUp + GitHub CLI.** Use official ClickUp MCP with browser-based OAuth and reuse `gh` sign-in across authorized GitHub repositories. No ClickUp desktop app, ClickUp CLI, personal ClickUp token, local helper or bridge is required. The installer checks GitHub sign-in; only the running agent can verify ClickUp OAuth and actual repository access.

Use `onboard --mode hosted --github cli` explicitly for this combination. `--mode hosted --github hosted` instead selects an existing approved hosted GitHub connection. **Strict remote-only** (`--mode remote-only`, legacy `--mode oauth`) requires both connections to be hosted and never invokes `gh`. Missing or banned selected backends mean STOP; do not automatically fall back.

**Local-helper** (`--mode local-helper`, legacy `--mode cli`) separately installs `cup`/`cu-work` and requires its own ClickUp token. Existing `setup`/`update` keep their local-helper semantics. Hosted operations use agent-instruction safeguards, outside helper receipts, locks and completion gates.

Installation does not need Node: [choose a route](#choose-an-installation-route) by what the machine has. Node 22+ is needed only for the npx route and for local-helper mode, because Krodak's `cup` is an npm package. The default GitHub backend also needs an already allowed GitHub CLI. See [modes and host constraints](docs/modes.md).

[Documentation and team setup](https://randrescastaneda.github.io/clickup-skills/) · [Agent usage examples](https://randrescastaneda.github.io/clickup-skills/examples.html)

Give coding agents one project objective and ClickUp task scope, then keep their
implementation, subtasks, progress, and GitHub PRs connected to that scope.

**Default:** use ClickUp's official browser-OAuth MCP through your coding agent
and the selected GitHub backend (`gh` by default) for direct GitHub operations. The optional local `cu-work` helper uses
Krodak's CLI and a separate personal-token sign-in to enforce project scope,
record durable receipts and run a bounded sync worker. Other community MCPs are
advanced options, not required installation steps.

## What is included

| Component | Purpose |
| --- | --- |
| Six portable skills | Set up and verify the installation, bind a project, route tools, work a task, link GitHub, resume/handoff |
| Optional `cu-work` CLI | With `--mode local-helper` (legacy alias `--mode cli`): enforce scope, create GitHub-associated subtasks, link issues/PRs, sync discussions, and gate completion |
| Optional `clickup_work` MCP | With `--mode local-helper`: the same nine local-helper tools; hosted OAuth does not authenticate it |
| Optional `sync-worker` | Preview or poll comments for explicit linked tasks on one authenticated machine |
| Claude Code marketplace + portable/Codex manifests | Team installation from this repository |
| Copilot, Kilo, VS Code, and Posit adapters | Render each client's own MCP format from the same profiles |
| Optional MCP profiles | Official ClickUp, rich-context community MCP, and REST community MCP |
| Optional GitHub MCP configuration | Host-specific approved connection; remote-only never invokes local `gh` |

There is no paid integration dependency. ClickUp/GitHub service permissions,
rate limits, plan features, and your model provider's charges still apply.

## Choose an installation route

The route decides how the files arrive. The [selection](#choose-clickup-and-github-independently) decides which backends the agent uses, and every route installs the **hosted** selection unless you choose otherwise. Pick the first row this machine supports. Node.js is needed only for the npx route and for local-helper mode.

| What this machine has | Route | What you run |
| --- | --- | --- |
| Only the coding agent, plus one way to fetch files (git, `gh`, curl, PowerShell, a browser download) | **A. Agent-run manual install** | Paste the prompt below into the agent |
| GitHub CLI 2.90+ | **B. `gh skill`** (preview) | `gh skill install randrescastaneda/clickup-skills --all ...`, then register the MCP |
| Python 3.11+ and a clone or ZIP | **C. Python only** | `python3 scripts/setup.py onboard --client CLIENT` |
| Claude Code | **D. The client's plugin manager** | `claude plugin marketplace add randrescastaneda/clickup-skills` |
| Node 22+ and Python 3.11+ | **E. npx** | `npx --yes github:randrescastaneda/clickup-skills onboard --client CLIENT` |

`CLIENT` is `kilo`, `codex`, `claude`, `copilot` or `vscode` (VS Code Copilot Chat, which also needs `--project-dir /absolute/path/to/project`). Use one route per machine: two installers must never manage the same skill folder.

### A. Agent-run manual install

Paste this into the coding agent:

```prompt
Install ClickUp Skills for <Kilo Code | Codex | Claude Code | Copilot CLI> on this machine.
Node.js is not available here. Read
https://raw.githubusercontent.com/randrescastaneda/clickup-skills/main/INSTALL.md
and follow it exactly. Do not write anything to ClickUp or GitHub.
Stop and ask me if anything conflicts with what is already installed.
```

The agent follows the [install runbook](INSTALL.md): it fetches a pinned source, copies the six skill folders, checks each file's SHA-256 against `skills/MANIFEST.json`, registers the official ClickUp MCP with the client's own command or an exact settings snippet, and reports. It runs no downloaded script.

### B. GitHub CLI (`gh skill`, preview)

Needs `gh` 2.90 or later. The `gh skill` command group is a preview and may change.

| Client | Install the skills (user scope) |
| --- | --- |
| Claude Code | `gh skill install randrescastaneda/clickup-skills --all --agent claude-code --scope user` |
| Copilot CLI | `gh skill install randrescastaneda/clickup-skills --all --agent github-copilot --scope user` |
| Kilo Code | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.kilo/skills"` |
| Codex | `gh skill install randrescastaneda/clickup-skills --all --dir "$HOME/.agents/skills"` |

Add `--pin TAG` once a release tag exists. For Kilo and Codex pass `--dir`: `gh` 2.95 writes `--agent kilo` to `~/.kilocode/skills` and `--agent codex` to `~/.codex/skills`, not the folders this project uses. Update with `gh skill update --all`, adding the same `--dir` for Kilo and Codex. `gh skill` rewrites each `SKILL.md` frontmatter, so these copies belong to `gh`.

Then register the official ClickUp MCP: `python3 scripts/setup.py onboard --client CLIENT --skip-skills` from a clone, or step 7 of the [install runbook](INSTALL.md) (the client's own command or the settings snippet).

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

## After installing: verify in the agent

Reload your coding agent and paste:

```prompt
Use the clickup-setup skill to verify the six skills, my official ClickUp
MCP OAuth connection, selected GitHub backend (gh by default), and read-only Workspace/task access.
Guide me through browser authorization only if needed. Do not change
anything. Report exactly what is connected and what is missing.
```

Only the running agent can authorize the hosted OAuth connection. For direct official-MCP writes, the [guarded issue-first protocol](skills/clickup-github/references/official-mcp-issue-first.md) requires verified Workspace/List/root/repository scope, a confirmed GitHub target before task creation, duplicate-marker checks, read-backs, and safe recovery. **These are agent-enforced checks**, not local transaction guarantees. [See the exact command and authorization steps for Kilo, Codex, Claude Code, Copilot CLI and VS Code Copilot Chat](docs/clients.md).

### Optional: local helper with durable receipts

The stricter local workflow requires Node 22+, independent ClickUp CLI authentication and a valid project binding. Enable it **explicitly**:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode local-helper --client kilo
```

This installs our private Python workflow, Krodak's `@krodak/clickup-cli@latest`, and the local `clickup_work` MCP. If needed, the terminal guides a **personal API token** sign-in from [ClickUp Settings → Apps](https://app.clickup.com/settings/apps). The token-based helper cannot borrow the official MCP's OAuth session. Conversely, its durable receipts, scoped mutations, and shared OS lock do **not** apply when an agent calls the hosted MCP directly.

The earlier software-only `setup --client kilo` and full-runtime `update --client kilo` commands remain supported. A hosted installation refreshes configuration/managed skills by rerunning the same `onboard` command, including any explicit backend flags. Existing local `clickup_work` settings are not removed or authenticated by switching to OAuth.

### Alternative: manage skills through Vercel

```bash
npx skills add randrescastaneda/clickup-skills -g
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --skip-skills
```

This is an **alternative** to the one-command bundled installer, not an additional mandatory step. `--skip-skills` leaves Vercel's copies intact. Add `--mode local-helper` to the second command if you deliberately want the local helper. Update Vercel copies using `npx skills check` and `npx skills update -g`, and update the local helper (if installed) with `npx --yes github:randrescastaneda/clickup-skills update --client kilo --skip-skills`. Do not let two installers manage the same skill directory.

For project-scoped agents add `--project-dir /absolute/project`. VS Code's MCP configuration uses `--client vscode` and that flag. Onboarding neither modifies remote tasks nor enables ClickUp's native GitHub integration. Full instructions: [team installation](https://randrescastaneda.github.io/clickup-skills/installation.html).

## Advanced manual installation / contributing

The checkout-based route remains available for contributors and custom clients.

Python 3.11+ is required. The local helper's ClickUp CLI (`cup`) also requires Node 22+. Authenticate
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

Claude Code's marketplace plugin is [route D](#d-the-clients-own-plugin-manager). It supplies the six
skills and the official ClickUp MCP (`clickup_official`) only; it adds no
`clickup_work` or GitHub server, and it does not install or authenticate the
Python/Krodak runtime. Installing it does not grant Workspace/repository access.

Codex and OpenCode can use the same portable skills:

```bash
python3 scripts/install_skills.py --client codex
# Or: python3 scripts/install_skills.py --client opencode
python3 scripts/configure.py --client codex --profile remote-only
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

**Advanced: token-backed local helper only (`--mode local-helper`).** The following `cu-work` commands require the separately installed local helper and its authenticated CLI. Run them in the repository you want the agent to work on, not in this plugin checkout:

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
| `official` | Default hosted ClickUp: agent reads/writes directly through ClickUp's official MCP | Host tools; **not** executed through `cu-work` |
| `github-cli` / `github-mcp` | PRs, repository state, issues, and checks | `gh` in helper, or host GitHub tools |

```bash
cu-work --project-dir /absolute/project route task.context --available cup,context-mcp,official
python3 scripts/configure.py --client claude --profile context
python3 scripts/configure.py --client codex --profile local-helper
```

`route` is a deterministic recommendation over the capabilities you supply. It
does not benchmark servers, inspect the host inventory, or execute the selected
tool. The agent discovers the actual MCP schemas and applies scope checks. Enable
only the profiles you need; merge their named servers into your client settings
without removing other servers. When using a Claude plugin, avoid registering its
default `clickup_official` server a second time under global/project settings.

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

**With hosted ClickUp, ask the coding agent in plain language** to read the approved task, verify GitHub targets before new subtasks, record progress and link PR evidence. The agent follows the [guarded issue-first protocol](skills/clickup-github/references/official-mcp-issue-first.md), but does not have the local helper's durable receipts or worker.

**Advanced local-helper mode (`--mode local-helper`)** — only here do the `cu-work` commands below apply:

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
