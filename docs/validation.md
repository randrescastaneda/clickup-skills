# Validation and rollout

## Automated coverage

`python3 scripts/check.py` runs offline behavioral tests, bytecode compilation,
manifest/config validation, source-attribution checks, and skill-frontmatter checks.
The tests use fresh temporary Git repositories and mocked service data. Real
subprocess tests cover both the workflow MCP server and the REST MCP client
against an isolated protocol fixture. They do not measure real-world token cost
or server latency, and do not verify credentials or third-party service uptime.

Three independent skill scenarios were exercised with minimal task-local facts:

1. MCP-only execution with a merged PR and pending integration CI: the agent
   chose host tools, preserved reviewer text, and withheld completion.
2. A partial PR-link failure plus a proposed parent from a different workspace:
   the agent preserved the successful GitHub side, required complete remote
   reconciliation evidence, and rejected the out-of-scope subtask parent.
3. MCP-only issue-before-child creation, a timed-out child write, compact task
   identity, 40 comments/replies, and pending PR CI: the agent preserved the
   successful issue, required complete remote recovery evidence, skipped mirror
   echoes, and withheld completion. Ambiguities around host identity fallback,
   reply export policy, host receipts, and shared provenance were clarified.

New behavior tests cover GitHub-first creation, lost issue responses, resumed
child/backlink writes, explicit repository targets, changed-input rejection,
issue body preservation, two-way comment snapshots, edits, host provenance,
GitHub pagination/review types, and incomplete ClickUp-history rejection.

## Packaged installer validation — 20 October 2026

The suite now includes isolated installation and update checks with a fixture npm
CLI. These verify preservation of JSONC comments, unrelated settings and servers,
managed TOML updates, legacy default-config migration, skill conflicts, failed
dependency installs, repeated setup, and subprocess arguments containing spaces.
An actual npm archive is unpacked and installed, then its downloaded source is
deleted before the persistent MCP initializes and lists all nine workflow tools.
No API accounts are used by these offline tests.

A separate Linux smoke install fetched `@krodak/clickup-cli@latest` from npm,
verified its installed version (1.46.2 at test time), created the Python environment,
copied five skills, and wrote project-scoped Kilo configuration in an isolated
directory. This version is observed evidence, not an installation pin. No real
ClickUp/GitHub account authentication or task writes were performed in this test.
Installed editor discovery and authenticated client behavior remain live team
acceptance steps. The CI matrix runs Python 3.12 and Node 22 on Linux/macOS/Windows.

## Worker and rollout preparation — 21 October 2026

The offline suite now contains 96 passing tests. The optional polling worker has checks for explicit task scope, a
read-only preview, preflight across every task/target before writing, per-pass
write limits, binding changes, echo suppression and repeat runs. Tests lose
responses after successful writes on each service and verify marker-based
recovery without duplicates; absent remote evidence blocks replay. Old sync
receipts remain recoverable. Two ClickUp tasks sharing a PR have separate new
receipt keys while preserving the canonical source provenance.

OS-lock tests use an actual competing process, kill it, and verify the lock is
released. Linked worktrees share the same writer lock; separate clones and
machines still need one agreed owner per task. The packaged installer test
deletes the downloaded source, initializes the persistent MCP, and loads the
worker's command help. No editor or live account is involved in these checks.

Additional fixtures cover exact plain issue-comment endpoints and literal
multiline file inputs, malformed paginated records, inline review replies, and
excluding pending/unsubmitted reviews. These establish offline behavior only.

The reviewed upstream sources were rechecked: `cup comments` and REST MCP
`list_comments` still expose one page. The worker refuses a pass that would
reach 25 ClickUp comments with those default readers. The explicit
clickup-api comment-reader override adds GET-only cursor pagination, with
fixtures for multiple pages, inclusive overlap, equal timestamps, malformed or
stalled cursors, redirect rejection, and credential/error isolation. Task reads
and all writes still use the configured upstream runtime. No live worker service,
credentials, native connection, or automation was installed.
See [the worker guide](sync-worker.md) for its current boundaries and recovery.

## Kilo official OAuth pilot — 22 October 2026

A user-run Kilo session authenticated `clickup_official` via its existing
browser OAuth session and read the approved Workspace, test task, statuses
and official tool catalog. The token-backed `cup` backend was not used.
The pilot then performed **two reported remote writes** on the approved
`PIP-Technical-Team/wbpip` fixture:

1. Created one child `868mmcp85` below `868mjzgzh`, after verifying the
   existing GitHub issue #269. The child contained the issue URL,
   `[cu-work-github:...]` association and unique `[pilot-op:...]` marker.
2. Updated **only the body** of issue #269 to append the child backlink,
   preserving the original content.

The Kilo agent reported a guarded second pass with zero additional writes,
correct parent/list/status, and unchanged draft PR #270. Independent
read-back later confirmed the new child and the single issue-backlink
block. ClickUp's `markdown_description` escaped/reformatted the markers,
while `text_content` preserved them literally. This distinction is now
mandatory in the host workflow guidance.

**Limits:** This proves a successful agent-controlled existing-issue reuse
sequence, not a local-helper transaction or guaranteed exact-once write.
It does not validate new-issue creation, induced network timeouts,
simultaneous writers, production comment threading, MCP quota accounting
or host OAuth behavior in every supported client. No permanent worker,
native integration, or OAuth-backed bridge to `clickup_work` was installed.

## Live rollout acceptance

Choose a disposable or team-approved test task before broad rollout. Each
teammate authenticates their own tools. Configure the real workspace/list/root
and exact statuses; do not put tokens into the binding.

Run one task read, one small subtask, one progress comment, and a link to a draft
test PR. Repeat with identical operation keys and verify no duplicates. Verify
the PR's original body stays intact. Confirm the helper refuses an unrelated
task and refuses done while the PR is draft/open or CI is pending.

Run the same read/update on the free REST MCP runtime. For host official/context
and GitHub MCP, discover current schemas and verify the skills' manual scope and
recovery sequence. Verify every teammate gets only their own account's access.

Record elapsed time, calls, and returned bytes for equivalent tasks if tuning
routing priorities. Change project overrides based on those measurements.
Do not claim a faster/cheaper backend merely from the default ordering.

Live ClickUp access was verified through the official host MCP on 2026-10-19:
one scoped repository-associated child, one linked progress comment, repeat-read
reuse, and an in-progress/backlog status round trip. Initial GitHub issue creation
returned HTTP 403. On 2026-10-20 the user installed the GitHub App for the actual
repository owner organization, resolving the missing installation. The follow-up
created issue #269 and draft PR #270 in wbpip, verified reciprocal task links and
PR body preservation, transferred labeled conversation fixtures in both
directions, and reused exactly one mirror per canonical source-event key on a
second pass. The child and parent remain open; the original parent is unchanged.

See [the pilot record](pilots/wbpip.md) for source/destination IDs and exact scope.
These are live **host-MCP/skill** checks. Local CLI/REST runtime credentials,
plain issue-comment writes, live inline review/thread transfers, native
integration/automation behavior, and real installed-client plugin loading remain
separate acceptance steps from the passing offline suite. No always-on comment
worker, merge, or deployment was installed.
