---
title: Troubleshooting
description: Diagnose the layer that failed without replaying uncertain writes.
section: Reference
---
# Find the missing layer.

Start with the actual agent session and working repository. Authentication in another editor or browser does not authenticate this environment.

| Symptom | What to check / ask the agent |
| --- | --- |
| `cu-work` is missing | **Normal with default hosted ClickUp:** use official hosted ClickUp MCP and the selected GitHub backend (`gh` by default); stop if unavailable. Only `onboard --mode local-helper` installs the persistent local helper; that mode exposes `clickup_work` and writes `cu-work` launchers to `~/.local/share/clickup-skills/bin` (or `CLICKUP_SKILLS_HOME/bin`); add that folder to PATH. |
| The plugin installed but tasks cannot be read | Hosted ClickUp: check **this agent's** `clickup_official` browser authorization and its Workspace/List read permission. Local-helper mode: check separate `cup` token authentication and project binding. |
| Every skill appears twice | The skills were installed for this agent by two methods (for example the installer and the Claude Code plugin), at both user and project scope, or this agent also reads another agent's skills folder. Keep one copy: ask the agent to run the existing-installation check in the [install runbook](install-runbook.html), then remove the extra copy or upgrade with the method that installed it |
| After an agent-run install, the agent says installer files are missing or suggests npx | Normal: the [install runbook](install-runbook.html) deletes its source when it finishes, so no installer stays on the machine. Do not run npx on that installation; its `onboard` would add a second method. To check the files, ask the agent to repeat runbook steps 4 and 7 (fetch the source, compare hashes), or run `python3 scripts/setup.py status --client CLIENT` from a clone of the same or a later release |
| Skills are not discovered | Use the actual agent’s discovery path, reload the session, and add the project instruction; avoid duplicate copies |
| MCP config is rejected | Choose the correct renderer: VS Code, Copilot, Codex, Kilo and Posit use different shapes |
| GitHub cannot connect | Default hosted ClickUp uses `gh auth status` for GitHub. Strict remote-only needs an approved hosted GitHub connection with repository access. If unavailable, stop; do not install `gh` or a bridge as fallback. Local-helper users can check `gh auth status`. In Kilo, the previous remote GitHub MCP may fail due to unsupported dynamic registration; the installer disables only an unchanged, installer-owned copy. |
| GitHub reads work but writes return 403 | Check the GitHub App on the repository owner’s account/organization and its selected repository permissions |
| “No binding” / origin mismatch | Hosted ClickUp: verify the project's `.clickup/project.json` directly (or obtain approved exact task scope); the helper may not be installed. Local-helper mode: bind the **working project repository**, verify its origin and its local helper receipt state. Never bind the plugin checkout by accident. |
| Task is rejected as out of scope | Re-read native ID, Workspace, home List and ancestry; review cross-list moves before changing scope |
| Status change fails | Discover the List’s exact status names and update `github.status_map` deliberately |
| `npx`, `npm` or Node is not available | Install without Node: let the agent follow the [install runbook](install-runbook.html) (route A), or use `gh skill install` or `python3 scripts/setup.py onboard --client CLIENT`; Claude Code can use its plugin manager. See [installation routes](installation.html#choose-an-installation-route). Only local-helper mode needs Node. |
| A task write timed out | Inspect receipts and complete remote evidence before retrying; do not switch providers to replay |
| Comment reconciliation stops at 25 | Use explicit paginated host reads for complete ClickUp history; fetch threaded replies there |
| PR merged but task is still open | Verify acceptance, current linked PR/base and latest PR-head CI; merge alone is insufficient |
| No GitHub activity appears in ClickUp | Verify native integration, repo/Space mapping, access and actual `CU-TASK_ID` references |
| Comments stop copying when the agent closes | Session tools run when invoked. The optional worker must be started separately on an authenticated machine; inspect its timestamp/status and use the explicit complete-history reader for long histories |

## A compact diagnosis prompt

```prompt
Diagnose the ClickUp Skills issue in this session. Check the working repository,
binding, actual agent client, skill discovery, executables, current tool schemas
and account permissions. Read remote evidence where authorized. Separate local
setup, MCP authentication, task scope and native integration. Do not repeat any
uncertain mutation. Report the smallest concrete fix and anything you need from me.
```

## Scope, credentials and sharing

Keep personal tokens out of configuration committed to Git, screenshots and task comments. Rendered configurations use environment references rather than substituting secret values. Discussion copies share content with the bound repository’s audience; use the intended scope and directional reconciliation where appropriate.

See [validation status](validation.html) for what has actually been tested. Passing configuration checks is separate from a live installed-client pilot.
