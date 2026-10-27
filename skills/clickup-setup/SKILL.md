---
name: clickup-setup
description: Install, authenticate, validate, or update ClickUp Skills in explicit remote-only or local-helper mode. Use for team onboarding, safe MCP configuration, choosing an authorized mode, or diagnosing setup.
---

# Guided ClickUp Skills setup

Choose the authorized mode before changing configuration. Respect organizational service bans and preserve existing settings, customized skills and sessions. Never request tokens in chat. A hosted MCP connection is distinct from the ClickUp desktop app, local CLI and REST API credentials.

## Remote-only (default)

Use portable skills with approved official hosted ClickUp MCP at `https://mcp.clickup.com/mcp` and an approved hosted GitHub connection when the workflow needs GitHub. No ClickUp desktop app, `cup`, `cu-work`, local CLI/helper or `npx mcp-remote` bridge is required or permitted as automatic fallback. If a required approved connection or direct remote OAuth support is absent, **STOP and report it**; do not install tools or bypass policy.

For **no extra local tools**, use a browser/admin-provided reviewed repository copy and copy/import the six `skills/` directories and references into the existing host's supported skill location. Preserve MIT notices. Add/reuse the official ClickUp connection through the host's native direct HTTP/OAuth UI, plus an approved hosted GitHub connection. Verify the host supports both portable skills and these remote connections. See [modes and host constraints](https://github.com/randrescastaneda/clickup-skills/blob/main/docs/modes.md); there is no universal manifest format.

If local Node.js 22+, Python 3.11+ and Git are already allowed, this optional convenience command copies skills and configures the endpoint:

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode remote-only --client kilo
```

Omit `--client` for the chooser. `--mode oauth` is a legacy alias; it no longer invokes `gh auth`. This command is **not** a no-install route: it executes local installer code. It never proves OAuth, task permission or hosted GitHub access. `--skip-skills` preserves skills owned by Vercel/another installer. Do not use two installers for the same copies.

After reload, discover all six skills and real MCP schemas. Authorize official ClickUp OAuth only in the host, then verify authenticated identity, Workspace/List/root ancestry and intended GitHub repository via approved hosted reads. A connected server alone is insufficient. Codex uses `codex mcp list` / `codex mcp login clickup_official`; Claude Code uses `/mcp`; Copilot CLI uses `/mcp`; VS Code needs a trusted project and Agent mode. These existing-host commands do not install a bridge.

Kilo's prior macOS ClickUp pilot used local `gh` for GitHub. GitHub remote OAuth DCR was incompatible; this is **not** full remote-only acceptance. Without another approved working hosted GitHub connection, stop GitHub-dependent work. See [per-agent details](https://github.com/randrescastaneda/clickup-skills/blob/main/docs/clients.md).

## Local-helper (explicit)

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --mode local-helper --client kilo
```

Legacy `--mode cli` and software-only `setup` / `update` remain supported. This installs the private Python runtime, Krodak's latest CLI and `clickup_work`, with `gh` for GitHub. Separate personal ClickUp CLI token authentication uses `cup init` / `cup auth`; tokens belong in the terminal's credential flow, never chat or committed config. Hosted OAuth does not authenticate `cup`.

Use local tools only where user and organization allow them. The helper's scope/journal/OS locks and completion checks require a verified project binding; running the process alone proves none of that. Existing local configuration is preserved by remote-only setup but must not be used for remote-only operations. Do not change mode to replay a failed or uncertain write.

## Before the first write

Load the [guarded issue-first host protocol](../clickup-github/references/official-mcp-issue-first.md). Verify exact GitHub repository/base and target **before** child creation, live ClickUp identity/Workspace/List/root ancestry, duplicate markers, bounded writes, readback and uncertain-outcome handling. In remote-only these are **agent-instruction safeguards**, not helper-enforced journal, locks or completion gates. No safety-parity claim is made. If scope or evidence is missing, stop before writing.

Do not update tools during task writes. After an authorized update, reload and reverify discovery and scope. No credentials, grants or global settings changes are implied merely by a task mentioning ClickUp. Native integrations, automations and recurring workers are separate administrator work.
