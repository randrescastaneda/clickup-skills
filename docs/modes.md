# Choose ClickUp and GitHub independently

| Selection | ClickUp | Direct agent GitHub actions | Setup |
| --- | --- | --- | --- |
| Hosted (default) | Official OAuth MCP | Reusable GitHub CLI browser login | `onboard --mode hosted --github cli` |
| Hosted + hosted GitHub | Official OAuth MCP | Existing approved hosted GitHub connection | `onboard --mode hosted --github hosted` |
| Strict remote-only | Official OAuth MCP | Approved hosted GitHub only; no `gh` | `onboard --mode remote-only` |
| Local-helper | Separate `cup`/`cu-work` runtime and ClickUp token | Authenticated `gh` | `onboard --mode local-helper` |

Omitting flags selects hosted ClickUp + GitHub CLI. Legacy `oauth` still aliases
strict remote-only and never authenticates `gh`; legacy `cli` aliases local-helper.
Contradictory selections, such as `--mode remote-only --github cli`, are rejected
before settings, package installation or authentication. The existing local
helper requires GitHub CLI; selecting hosted GitHub with it is rejected.

## Default daily workflow

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --mode hosted --github cli
```

The convenience installer runs Node 22+, Python 3.11+ and Git. It copies skills,
configures `https://mcp.clickup.com/mcp`, then checks/reuses `gh` sign-in or
starts GitHub's browser flow when needed. Install GitHub CLI separately if it is
missing and allowed; the installer never silently installs it. Reuse one account
across its authorized repositories, subject to organization policies. Verify each
project's owner/repository and scope. No manually created per-repository token is
required for this path.

No ClickUp desktop app, ClickUp CLI, `cu-work`, local helper token or bridge is
required. The **ClickUp desktop app** is a UI; `cup` is a CLI; official MCP is a
hosted service. ClickUp also provides a [REST API](https://developer.clickup.com/docs/authentication),
whose credentials remain separate from hosted OAuth.

The terminal does not authenticate ClickUp OAuth or prove repository access from
GitHub sign-in alone. Reload the agent and verify actual authenticated reads.
The private installer receipt records mode and GitHub backend. Existing local
helpers and user-managed MCP entries are preserved; their presence does not
authorize their use for the selected workflow.

## Native ClickUp–GitHub integration versus agent access

| Connection | Responsibility |
| --- | --- |
| ClickUp's native GitHub connection | Configured task/activity links, UI commands and optional automations |
| Agent → ClickUp MCP | Manage ClickUp tasks, scope and progress |
| Agent → selected GitHub backend | Direct issue/PR edits, code/diff review and CI checks |

The native integration associates commits/branches/PRs containing ClickUp IDs and
offers GitHub commands in ClickUp. Those UI capabilities do not automatically
become tools in the documented ClickUp MCP catalog. Reuse native integration for
its actual coverage; verify configuration and choose one owner for issue creation
or mirroring. Do not run agent and automation writers for the same action. This
installer does not enable native connections or rules.

Sources: [ClickUp GitHub integration](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration),
[GitHub Automations](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations),
[ClickUp MCP tools](https://developer.clickup.com/docs/mcp-tools),
[GitHub CLI login](https://cli.github.com/manual/gh_auth_login).

## Strict manual route with no extra local tools

Use an existing approved host supporting skill files and direct remote HTTP/OAuth.
Import six `skills/` directories with references and MIT notices, preserving
customized/externally managed copies. Configure official ClickUp MCP in its native
UI and reuse an approved hosted GitHub connection. Verify skills, actual schemas,
identity, Workspace/List/root ancestry and exact GitHub target before writing.
There is no universal import format.

Missing/banned selected tools mean **STOP**. Never install `cup`, `cu-work`,
`npx mcp-remote`, Docker or another bridge as fallback for hosted ClickUp.
Strict remote-only and selected hosted GitHub also forbid falling back to `gh`.
Change modes only explicitly before a new operation; never replay a failed or
uncertain mutation through a different backend.

## Host constraints and acceptance

| Host | Evidence and remaining limit |
| --- | --- |
| Kilo VS Code | The 5 November test passed for hosted ClickUp + `gh` on 7.8.18. It verified current skill loading after reload, one child and backlink, and a repeat pass with zero writes. See [validation](validation.md). |
| Kilo hosted GitHub | Earlier OAuth DCR attempt failed; later prepared token file was empty. No full hosted GitHub acceptance. |
| Codex / Claude Code / Copilot CLI / VS Code Copilot Chat | Offline configuration contracts; verify installed skills, ClickUp OAuth and selected GitHub backend separately. |
| Other / manual hosts | Verify portable skill loading and direct OAuth first. A local bridge does not qualify as no-extra-local-tools. |

Kilo's observed 7.8.18 backend cached full skill bodies. Use **Developer: Reload
Window** after updating, then a fresh task and loader-versus-file comparison.
A new task alone did not reliably refresh that observed backend. This is dated
local evidence, not a guarantee about every version.

GitHub remote OAuth needs host-specific registration; DCR alone is insufficient.
Other hosted authentication methods depend on host support and approval.
[GitHub authentication guidance](https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md).
No mode bypasses organizational service restrictions.

## Compatibility and guarantees

Rerun the same `onboard` command/flags to update hosted installs. `setup`/`update`
remain local-helper commands. Existing `default`, `context` and `rest` profiles
keep local behavior; `official`/`remote-only` manifests contain only hosted
ClickUp. `configure.py` prints that configuration without editing settings or
authenticating GitHub. Explicit local-helper + official profile still works.
GitHub is not auto-added as an MCP.

Hosted calls, including hosted ClickUp + `gh`, follow agent-directed scope,
duplicate, readback and completion checks. They do not acquire helper receipts,
OS locks or completion gates. Offline tests do not establish live client/OAuth
or mutation acceptance. Worker defects/live acceptance remain separate under
[#12](https://github.com/randrescastaneda/clickup-skills/issues/12) and
[#23](https://github.com/randrescastaneda/clickup-skills/issues/23).
