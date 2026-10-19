# Validation and rollout

## Automated coverage

`python3 scripts/check.py` runs offline behavioral tests, bytecode compilation,
manifest/config validation, source-attribution checks, and skill-frontmatter checks.
The tests use fresh temporary Git repositories and mocked service data. Real
subprocess tests cover both the workflow MCP server and the REST MCP client
against an isolated protocol fixture. They do not measure real-world token cost
or server latency, and do not verify credentials or third-party service uptime.

Two independent skill scenarios were exercised with minimal task-local facts:

1. MCP-only execution with a merged PR and pending integration CI: the agent
   chose host tools, preserved reviewer text, and withheld completion.
2. A partial PR-link failure plus a proposed parent from a different workspace:
   the agent preserved the successful GitHub side, required complete remote
   reconciliation evidence, and rejected the out-of-scope subtask parent.

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

Live ClickUp access and real installed-client plugin loading were unavailable
during the initial implementation. Those remain acceptance steps, separate from
the passing offline suite and packaging checks.
