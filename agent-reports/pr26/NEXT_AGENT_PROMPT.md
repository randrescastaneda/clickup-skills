# Next local Kilo task: publish readiness evidence

Use this prompt in Andres's existing Kilo session. The user requested a shared report folder because copying long responses into ChatGPT is unavailable.

## Authorized scope

Publish sanitized diagnostic reports to `randrescastaneda/clickup-skills`, branch `handoff/pr26-validation`, folder `agent-reports/pr26/`.

This authorizes ordinary Git operations needed to publish reports using existing repository authentication. It does not turn Git/gh into an alternative backend for the remote-only service test. Preserve the user's current work using a separate worktree or clean checkout. Do not broaden the organization-scoped test token to access this report repository.

Read the folder README, root AGENTS.md and current summary before proceeding. Preserve earlier reports. Do not merge, force-push, open a PR, modify product code/skills, reinstall tools, or alter workers/automations.

## Diagnostic task

1. Confirm Kilo's actual version/runtime and whether all six skill-loader results still match their current installed files. Record source paths with personal components redacted. Do not clear caches or replace skill copies speculatively.
2. Check credential readiness without reading, printing, copying, or committing the token value. The existing private token file may still be empty.
3. If the approved token is missing, write and publish a BLOCKED report now, with the exact private user action. Do not wait to publish until authentication succeeds. Do not create credentials, request tokens in chat, or change repository permissions.
4. Once Andres has supplied the credential privately and reloaded the backend, use only the official hosted GitHub MCP to verify repository `PIP-Technical-Team/wbpip`, branch `PROD`, and issue `#269`. Report actual discovered tool names, authenticated read results, and sanitized errors.
5. Preserve the current read-only GitHub restriction. Make zero ClickUp/GitHub content writes during this diagnostic stage. Do not create the test child, edit issue #269, or rerun the full acceptance workflow.
6. Clearly state that the read-only token and MCP setting cannot perform the later backlink write. Report what would need separate authorization, without changing it now.

## Reporting and push

- Create a new dated Markdown report using REPORT_TEMPLATE.md. Summaries and small sanitized log excerpts are enough; never upload credential files, raw settings, backups, private task/comment bodies or unsanitized screenshots.
- Record observations with timezone, tested source commit when known, installed source evidence, actual tool calls, local changes, and remaining blockers. Do not infer an installed Git commit from content digests alone.
- Review the exact report and staged diff for secrets or unrelated files; stage only the explicit report path.
- Run repository-required checks before committing; report failures accurately.
- Fetch before pushing, integrate others' report commits without overwriting their work, and use a normal push to the dedicated exchange branch.
- Verify the report exists remotely. Return the report URL and commit SHA.
- If existing Git authentication cannot publish it, retain the sanitized local report and state the publishing blocker. Do not use or broaden another account's credentials.

The reviewing ChatGPT agent will read the pushed file when Andres requests review. Publishing a report is not evidence that hosted GitHub MCP authentication passed.
