---
title: Troubleshooting
description: Diagnose the layer that failed without replaying uncertain writes.
section: Reference
---
# Find the missing layer.

Start with the actual agent session and working repository. Authentication in another editor or browser does not authenticate this environment.

| Symptom | What to check / ask the agent |
| --- | --- |
| `cu-work` is missing | **Normal in default OAuth mode:** use the official ClickUp MCP and `gh` directly. Only `onboard --mode cli` installs the persistent local helper; that mode exposes `clickup_work` and the managed `npx --yes github:randrescastaneda/clickup-skills work` proxy. |
| The plugin installed but tasks cannot be read | OAuth mode: check **this agent's** `clickup_official` browser authorization and its Workspace/List read permission. Full-helper mode: check separate `cup` token authentication and project binding. |
| Skills are not discovered | Use the actual agent’s discovery path, reload the session, and add the project instruction; avoid duplicate copies |
| MCP config is rejected | Choose the correct renderer: VS Code, Copilot, Codex, Kilo and Posit use different shapes |
| GitHub cannot connect | Default setup uses `gh`: check `gh auth status` and repository access. GitHub MCP is optional and has separate authentication. In Kilo, the previous remote GitHub MCP may fail due to unsupported dynamic registration; the installer disables only an unchanged, installer-owned copy. |
| GitHub reads work but writes return 403 | Check the GitHub App on the repository owner’s account/organization and its selected repository permissions |
| “No binding” / origin mismatch | OAuth mode: verify the project's `.clickup/project.json` directly (or obtain approved exact task scope); the helper may not be installed. Full-helper mode: bind the **working project repository**, verify its origin and its local helper receipt state. Never bind the plugin checkout by accident. |
| Task is rejected as out of scope | Re-read native ID, Workspace, home List and ancestry; review cross-list moves before changing scope |
| Status change fails | Discover the List’s exact status names and update `github.status_map` deliberately |
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
