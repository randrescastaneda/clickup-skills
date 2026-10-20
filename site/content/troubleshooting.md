---
title: Troubleshooting
description: Diagnose the layer that failed without replaying uncertain writes.
section: Reference
---
# Find the missing layer.

Start with the actual agent session and working repository. Authentication in another editor or browser does not authenticate this environment.

| Symptom | What to check / ask the agent |
| --- | --- |
| `cu-work` is missing | Install the Python package in the agent’s environment; activate its venv or set the absolute executable path |
| The plugin installed but tasks cannot be read | Verify personal ClickUp sign-in, the actual Workspace/List access and available runtime |
| Skills are not discovered | Use the actual agent’s discovery path, reload the session, and add the project instruction; avoid duplicate copies |
| MCP config is rejected | Choose the correct renderer: VS Code, Copilot, Codex, Kilo and Posit use different shapes |
| GitHub MCP works but helper GitHub calls fail | Authenticate `gh` in the helper’s environment; hosted MCP OAuth is separate |
| GitHub reads work but writes return 403 | Check the GitHub App on the repository owner’s account/organization and its selected repository permissions |
| “No binding” / origin mismatch | Bind the working project repository and verify its actual origin; do not bind the plugin checkout by accident |
| Task is rejected as out of scope | Re-read native ID, Workspace, home List and ancestry; review cross-list moves before changing scope |
| Status change fails | Discover the List’s exact status names and update `github.status_map` deliberately |
| A task write timed out | Inspect receipts and complete remote evidence before retrying; do not switch providers to replay |
| Comment reconciliation stops at 25 | Use explicit paginated host reads for complete ClickUp history; fetch threaded replies there |
| PR merged but task is still open | Verify acceptance, current linked PR/base and latest PR-head CI; merge alone is insufficient |
| No GitHub activity appears in ClickUp | Verify native integration, repo/Space mapping, access and actual `CU-TASK_ID` references |
| Comments stop copying when the agent closes | Expected: the helper runs when invoked; continuous comments require a separate worker |

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
