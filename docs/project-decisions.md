# ClickUp Agent Integration Decisions and Current State

Project reference  |  Updated 21 October 2026

We are building a shared ClickUp workflow for coding agents so the team can define a project objective once, work within its task scope, and keep GitHub work connected. PRs #1–#4 are merged into main: scoped workflows, documentation and Pages automation, latest-release ClickUp CLI installation, and the one-command npx installer. The bounded live host-MCP pilot passed. Team editor acceptance and full continuous synchronization remain separate work. The optional worker described below is a new implementation on feat/sync-worker-rollout, pending merge and live acceptance.

## Agreed decisions

| Decision | What we agreed and implemented |
| --- | --- |
| Shared repository | Use randrescastaneda/clickup-skills for portable skills, workflow tools, client adapters, and setup documentation. Reuse existing integrations instead of rebuilding the ClickUp API. |
| CLI and MCP routing | Prefer krodak’s cup CLI for routine ClickUp operations and gh for GitHub. Use a community or official MCP when it offers better coverage, richer context, or fewer calls. Routing priorities are configurable; efficiency still needs measurement. |
| Free integration software | Use MIT dependencies and preserve attribution and reviewed commits. Install/update Krodak’s ClickUp CLI with @latest; keep other executable MCP dependencies pinned. Include krodak/clickup-cli, hauptsacheNet/clickup-mcp, joelpt/clickup-mcp, and the official plugin as a packaging reference. Service plans and model charges still apply. |
| One project scope | Bind the objective, GitHub repository and base branch, ClickUp workspace, home list, root task IDs, and exact statuses in .clickup/project.json. Validate task identity and ancestry before writes. |
| GitHub target before a subtask | Every new subtask must have a verified repository, issue, or PR target before creation. Create or reuse an issue by default when no target was supplied. A repository-only target supports planning; discussion sync needs an issue or PR. |
| Portable team setup | Keep five shared skills for binding, routing, task work, GitHub linkage, and handoff. Provide separate Codex, Claude Code, Copilot, and Kilo adapters. Configure the actual agent running in VS Code or Positron; Posit Assistant has its own setup. |
| Preserve work and credentials | Preserve human issue and PR text, add managed crosslinks, and keep credentials and private runtime state out of Git. Each teammate authenticates with their own account. Install skills as copies by default for Windows compatibility. The npx setup command creates the private Python environment, installs Krodak’s latest CLI, copies five skills, and merges client settings; Python 3.11+, Node 22+, Git, and authenticated GitHub CLI remain prerequisites for local workflows. |

## Synchronization and completion rules

ClickUp owns the objective and acceptance criteria. GitHub owns code, reviews, CI results, and merge evidence. Linked copies of comments retain the original source URL and identity. These ownership rules guide reconciliation when the systems differ.

- Link tasks, issues, and PRs in both directions. Include ClickUp task references in relevant GitHub artifacts. Create a PR only after a meaningful branch change exists; a missing repository requires an explicit owner, name, visibility, and a new binding.

- Use stable operation keys for identical writes. After a partial failure, preserve the successful side and reconcile remote evidence before retrying. Never replay an uncertain write through another backend. Coordinate one writer per task; exact-once behavior across concurrent machines is not established. The worker change adds OS-held locks shared by linked worktrees in one local repository; receipts remain per worktree. Separate clones and machines still require coordinated ownership.

- Mirror progress to associated discussions. Reconcile comments on demand, including at session start and handoff. Skip generated mirrors to prevent loops. Source edits produce a new snapshot; deletions do not propagate.

- The helper reads GitHub issue comments, PR conversation comments, submitted reviews, and inline review comments. It exports ClickUp top-level comments. Default local ClickUp commands expose one page, so the helper stops at 25 comments. The new explicit routing.comment_reader=clickup-api override provides complete GET-only cursor pagination with private environment credentials. All task operations and writes stay on the selected upstream runtime; there is no automatic fallback.

- For implementation tasks, allow Done only with acceptance evidence, a linked merged non-draft PR targeting the bound base, and successful checks on its latest head. An explicit project policy can allow no checks. A closed issue or a PR link alone is insufficient.

## Three integration layers

| Layer | Role and current boundary |
| --- | --- |
| Agent workflow | cu-work CLI and clickup_work MCP expose the same scoped workflow. Host ClickUp and GitHub MCPs can follow the skills directly, using manual scope and recovery checks; those calls bypass the helper’s local journal. |
| Native ClickUp connection | Configure the GitHub repository and ClickUp Space mapping separately. Native activity links can continue while agents are offline. Authenticating an MCP does not enable this connection. |
| Automations and continuous sync | Optional GitHub Automations require ClickUp Business or above and administrator setup. Assign issue creation to either the agent or an automation. Avoid automatic Done on merge. The new optional sync-worker can poll an explicit task allowlist on an authenticated machine. Preview is read-only; --apply --watch starts polling. It preflights all tasks, caps new mirrors per pass, preserves receipts, and stops on changed bindings or uncertain writes. Default readers retain the 25-comment guard; the explicit complete-history reader supports longer discussions. Live worker acceptance remains unfinished. |

No background worker, native connection, automation rule, merge, or deployment is installed automatically. The repository wiki contains setup instructions. The optional worker implementation is not a deployed service or proof of live acceptance. Full-history operation requires explicitly configured API-reader credentials and live acceptance; default command readers still stop at 25 comments.

## Verified results

PR #1 merged on 20 October 2026 at 10:06 a.m. Eastern. Its head commit passed GitHub Actions on Linux, macOS, and Windows. The recorded suite contains 45 offline behavior tests, plus skill, client configuration, manifest, and attribution checks.

The live host MCP pilot used PIP-Technical-Team/wbpip with PROD as its base and the supplied test task 868mjzgzh. It reused child 868mjzvmu, created issue #269 and draft PR #270, preserved the original PR description, and verified reciprocal links and controlled PR comment transfers in both directions. A second pass reused one mirror per source key. The parent task was preserved and no R behavior changed.

GitHub initially allowed reads but rejected issue creation with 403. Installing the GitHub App for PIP-Technical-Team resolved the write permission. Account-level repository access did not prove that the app installation could write.

At this snapshot, pilot issue #269 is open and pilot PR #270 remains draft and unmerged. The pilot child was last recorded in backlog. Merging the tooling PR #1 did not complete the pilot task.

## Repository and installation state — 21 October 2026

- All four original PRs are merged. The three old implementation/documentation/installer branches have been removed; no unique changes remained on them.
- Main is dc0e4e4b646061528323bdc42f269f937f896ed7. Its Linux/macOS/Windows offline checks and documentation deployment passed.
- The GitHub npx installer is available from main without publishing to the npm registry. Updates refresh Krodak’s latest release explicitly between task writes.
- The worker change repairs stale feature-branch documentation links and a receipt collision when multiple ClickUp tasks share one PR. Canonical source provenance is unchanged and old receipts remain recoverable.
- The full 96-test offline suite and the 26-page HTML documentation/link/source checks pass locally. New coverage exercises worker scope/write limits, preview isolation, restarts, edits, response loss on both services, shared-PR tasks, process-death lock release, exact issue-comment writes, malformed pagination, inline replies and pending-review exclusion. These are automated fixtures, not live account or editor acceptance.

## Remaining validation gaps

Live local `cup`, REST MCP and worker execution, plain issue-comment writes, inline review or threaded discussion transfers, native integration and automation behavior, and skill and tool loading in installed team clients remain unverified. Offline configuration checks do not establish installed-client behavior. Complete-history reader behavior is offline-tested; live API-reader authentication, worker hosting and native repository-to-Space mapping remain unconfigured/unverified here.

## Reference sources

- [Optional worker implementation branch](https://github.com/randrescastaneda/clickup-skills/tree/feat/sync-worker-rollout)

- [Merged documentation and Pages automation — PR 2](https://github.com/randrescastaneda/clickup-skills/pull/2)

- [Merged latest-release installation policy — PR 3](https://github.com/randrescastaneda/clickup-skills/pull/3)

- [Merged one-command installer — PR 4](https://github.com/randrescastaneda/clickup-skills/pull/4)

- [Merged implementation and scope — clickup-skills PR 1](https://github.com/randrescastaneda/clickup-skills/pull/1)

- [Team setup wiki and synchronization limits](https://github.com/randrescastaneda/clickup-skills/blob/main/docs/wiki/github-clickup.md)

- [Client setup and acceptance status](https://github.com/randrescastaneda/clickup-skills/blob/main/docs/clients.md)

- [Pilot record and exact evidence](https://github.com/randrescastaneda/clickup-skills/blob/main/docs/pilots/wbpip.md)

- [Pilot artifacts — issue 269](https://github.com/PIP-Technical-Team/wbpip/issues/269)

- [Pilot artifacts — draft PR 270](https://github.com/PIP-Technical-Team/wbpip/pull/270)

- [ClickUp GitHub integration instructions](https://help.clickup.com/hc/en-us/articles/6305771568791-GitHub-integration)

- [ClickUp GitHub Automations instructions](https://help.clickup.com/hc/en-us/articles/6305836061463-Use-GitHub-Automations)

Use this document to resume the project. Recheck live task and repository state before new writes; update this reference when decisions or acceptance results change.
