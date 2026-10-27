# Choose an authorized mode

| | Remote-only | Local-helper |
| --- | --- | --- |
| ClickUp | Official hosted MCP at `https://mcp.clickup.com/mcp`, OAuth in the approved host | Krodak `cup` and `cu-work`, separate personal-token sign-in; optional local MCPs |
| GitHub | Approved hosted GitHub connection with the required repository/tools | Authenticated `gh`; optional host MCP |
| Local additions | Portable skill files only; no ClickUp desktop app, CLI, helper, Node/Python runtime or bridge needed for manual setup | Python 3.11+, Node 22+, Git and `gh` for the bundled installer |
| Safeguards | Agent instructions for scope/ancestry, GitHub target first, duplicates, readback, uncertain outcomes and Done evidence | Helper code enforces its scoped operations, journal, local OS locks and completion checks; direct host calls remain outside it |

The **ClickUp desktop app** is a user interface, **`cup`** is a local CLI, and the **official MCP** is a hosted service. None requires installing the ClickUp desktop app. ClickUp also exposes a [REST API](https://developer.clickup.com/docs/authentication); MCP is not the only integration route. REST credentials and hosted MCP OAuth are separate. No mode authorizes bypassing an organizational ban on ClickUp, GitHub or external connections.

## Manual route with no extra local tools

Use an existing approved agent that can load portable skill files **and** connect directly to remote HTTP MCP with OAuth. Installation means adding skill files to that host's supported skill location or import UI, not installing a new executable.

1. Download the repository ZIP from GitHub in a browser, or use an administrator-provided reviewed copy. Copy/import the six directories under `skills/`, including their `references/` and MIT notices (`LICENSE` and `third_party/` when distributing the repository). Preserve the directory structure. Do not run `npx`, Python, `setup`, `cup` or a bridge. Do not overwrite skills owned by another installer or locally customized copies.
2. In the host's supported connection UI, add the official ClickUp endpoint `https://mcp.clickup.com/mcp` as direct HTTP/Streamable HTTP with OAuth. Reuse an existing validated connection. Confirm administrator approval and authorize only through the host. No personal API token is used by this endpoint.
3. Use an approved existing **hosted GitHub connection** with the required repository and issue/PR/check tools. Add GitHub's official remote endpoint `https://api.githubcopilot.com/mcp/` only if that host supports its authentication and the organization approves it. Its OAuth requires host-specific registration; DCR support alone is insufficient. Do not create OAuth apps/credentials to make it work without separate authorization.
4. Reload the host, discover the six skills and actual tool schemas, and perform authenticated read-only identity, Workspace/List/root ancestry and GitHub repository reads. Connection status alone is insufficient. The agent must load the guarded issue-first protocol before a write.
5. If skill loading, direct remote OAuth, GitHub tools or service approval is missing, **STOP and report the missing approved connection/capability**. Do not install `gh`, `cup`, `cu-work`, `npx mcp-remote`, Docker or another bridge as fallback. Select local-helper only when the user and organization explicitly allow local tools.

These are instructions for compatible hosts, not a universal import format. `mcp.json` follows the repository's existing agent-plugins schema; `.mcp.json` uses Claude-style JSON; Codex needs TOML, VS Code uses `servers`, and Kilo uses its own `mcp` structure. A manifest parse/render test does not prove the host accepts the server or completes OAuth. Do not paste a generic manifest into an unsupported host.

## Host constraints checked against official documentation (27 October 2026)

| Existing host | Direct ClickUp route | GitHub / acceptance limit |
| --- | --- | --- |
| Claude Code | Official ClickUp instructions describe native HTTP and `/mcp` OAuth | Use the host's supported approved GitHub connection; this change did not live-test it |
| Codex | Native Streamable HTTP/OAuth and `[mcp_servers.clickup_official]` with `url` are documented | Host-specific GitHub authentication must be verified; no new client/OAuth test here |
| VS Code Copilot Chat | Native HTTP MCP in `.vscode/mcp.json`, trusted project and Agent mode | GitHub documents remote OAuth for VS Code 1.101+; organization MCP policies must permit it |
| Kilo | Earlier macOS pilot established hosted ClickUp reads and a bounded agent workflow | Earlier GitHub remote DCR attempt failed. That pilot used local `gh`, so it **does not establish complete remote-only acceptance**. Without another approved hosted GitHub connection, stop |
| Claude web / Desktop | ClickUp documents connector UI for eligible plans; skill import/discovery is a separate host capability to verify | A connector alone does not install this repository's skills |
| Other / legacy hosts | Verify direct HTTP/OAuth and skill loading first | ClickUp's `npx mcp-remote` examples run a local bridge and **do not qualify as remote-only/no-install**, even though the destination is hosted |

Sources: [ClickUp endpoint/authentication](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server), [ClickUp client setup](https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server-1), [Codex MCP](https://developers.openai.com/codex/mcp), [GitHub remote server and host authentication](https://github.com/github/github-mcp-server#remote-github-mcp-server), [GitHub VS Code setup](https://docs.github.com/en/copilot/how-tos/provide-context/use-mcp/set-up-the-github-mcp-server).

## Optional automated configuration

The convenience command `npx --yes github:randrescastaneda/clickup-skills onboard --mode remote-only --client CLIENT` still runs local Node/Python code and Git-based package retrieval. Use it only where those existing tools are allowed. It configures the hosted ClickUp endpoint and copies skills; it does not install/authenticate ClickUp CLI/helper or `gh`, verify hosted OAuth, or provision GitHub connections. `--mode oauth` is a legacy alias for remote-only; it no longer triggers `gh auth`. Existing `gh` sign-ins and local MCP settings are preserved, but must not be used for remote-only work.

`onboard --mode local-helper` (legacy alias `--mode cli`) installs the supported local runtime and verifies separate CLI sign-ins. Existing `setup`/`update` keep their local-helper semantics. `profiles/default.json` remains the legacy local-helper profile; `profiles/local-helper.json` names it explicitly. `profiles/official.json` and `profiles/remote-only.json` contain only hosted ClickUp. For compatibility, explicit local-helper setup with `--profile official` still combines the local helper with official MCP. `configure.py` prints remote-only by default and never edits settings. GitHub is deliberately not auto-added to remote-only manifests because its authentication depends on the host.

Local-helper worker functionality and its PR #6 write-budget defect remain separate work tracked by [#12](https://github.com/randrescastaneda/clickup-skills/issues/12) and [#23](https://github.com/randrescastaneda/clickup-skills/issues/23). This mode alignment does not repair it or establish new helper/host safety parity; [#13](https://github.com/randrescastaneda/clickup-skills/issues/13) owns the bridge feasibility question.
