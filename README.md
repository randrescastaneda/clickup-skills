# ClickUp Skills

[Documentation and team setup](https://randrescastaneda.github.io/clickup-skills/) · [Agent usage examples](https://randrescastaneda.github.io/clickup-skills/examples.html)

Give coding agents one project objective and ClickUp task scope, then keep their
implementation, subtasks, progress, and GitHub PRs connected to that scope.

Use the CLI when it is a good fit, a free community MCP when it saves work or
covers a missing operation, and the official MCP when its service features fit.
This repository supplies the shared workflow, rather than another broad API wrapper.

## What is included

| Component | Purpose |
| --- | --- |
| Five portable skills | Bind a project, route tools, work a task, link GitHub, resume/handoff |
| `cu-work` CLI | Verify scope, create GitHub-associated subtasks, link issues/PRs, sync discussions, and gate completion |
| `clickup_work` MCP | The same nine scoped workflow tools for MCP-capable agents |
| Claude Code marketplace + portable/Codex manifests | Team installation from this repository |
| Copilot, Kilo, VS Code, and Posit adapters | Render each client's own MCP format from the same profiles |
| Optional MCP profiles | Official ClickUp, rich-context community MCP, and REST community MCP |
| GitHub MCP configuration | Host-native GitHub access alongside the workflow tools |

There is no paid integration dependency. ClickUp/GitHub service permissions,
rate limits, plan features, and your model provider's charges still apply.

## One-command installation per teammate

Install Python 3.11+, Node 22+, and Git first. Then run this from any directory:

```bash
npx --yes github:randrescastaneda/clickup-skills setup --client kilo
```

Replace `kilo` with `codex`, `claude`, or `copilot`. The installer creates a private
Python environment, installs **Krodak's `@krodak/clickup-cli@latest`**, copies the
five skills, and merges the client's personal MCP settings. No manual clone,
virtual-environment activation, Python install commands, or separate skill/config
commands are needed. The GitHub form works without an npm registry publication.

Existing settings and JSONC comments are preserved. Settings changes receive a
private backup; conflicting MCP entries or locally edited skills stop setup.
The MCP command uses an absolute persistent runtime path, independent of the
temporary npx cache. Nothing installs or updates during task writes.

Each teammate then authenticates individually (the installer prints these steps):

```bash
npx --yes github:randrescastaneda/clickup-skills cup init
npx --yes github:randrescastaneda/clickup-skills cup auth
# Install GitHub CLI from https://cli.github.com/ first, then:
gh auth login
```

Reload the agent and ask it to verify the five skills, MCP tools, and account
access. The local GitHub workflow requires GitHub CLI; installing GitHub MCP alone
does not supply it. This setup does not change remote tasks or enable a native
integration. Bind the working project below after installation.

To update the plugin runtime, managed skills/configuration, and Krodak CLI:

```bash
npx --yes github:randrescastaneda/clickup-skills update --client kilo
```

Repeat for each client you installed. Plain `setup` reuses an unchanged runtime;
`update` explicitly refreshes Krodak's latest release. Do this between task writes,
then have the agent read the bound task before resuming. Other executable MCP
dependencies keep their reviewed pins.

For project-scoped setup, append `--project-dir /absolute/path/to/project`.
VS Code uses `--client vscode` with that flag. Optional `--profile official` or
`--profile context` adds the corresponding existing adapter; OAuth/API-key setup
is still personal. Advanced REST and OpenCode setup remain documented below.
Do not install the same skills/servers both with this installer and with Claude's
marketplace plugin. The installer configures current Kilo, not legacy extensions.

Agents can access the managed shell workflow with `npx --yes
github:randrescastaneda/clickup-skills work <cu-work arguments>`; everyday users
delegate in plain language. MCP-based agents use the configured workflow tools.

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

The default plugin connects the scoped workflow MCP and GitHub's hosted MCP.
Authorize GitHub through your client's supported authentication flow. Installing
the plugin does not install Python/Node executables or grant workspace access.

Codex and OpenCode can use the same portable skills:

```bash
python3 scripts/install_skills.py --client codex
# Or: python3 scripts/install_skills.py --client opencode
python3 scripts/configure.py --client codex --profile default
```

Merge the printed TOML into your Codex MCP configuration; the script never edits
your configuration. Restart/reload the client if needed. The skill installer
copies the same five skills and their license, and refuses conflicting or locally
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

Run in the repository you want the agent to work on, not in this plugin checkout:

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

## Choose a backend

| Profile / backend | Use | Execution |
| --- | --- | --- |
| `cup` | Ordinary task operations with compact JSON/file-based text | Directly by `cu-work`; default runtime |
| `rest-mcp` | Free Python MCP with broad API operations | Directly by `cu-work`, or host tools |
| `context-mcp` | Rich task context, comments, images | Host tools; optional read-minimal profile |
| `official` | Official workspace search and service-specific capabilities | Host tools; OAuth |
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
limits. No OAuth integration, webhook, background worker, merge, or deployment
is installed automatically.

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
