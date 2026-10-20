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

## First live pilot

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
