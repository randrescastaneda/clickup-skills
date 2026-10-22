# Optional comment-sync worker

The worker polls an explicit set of already linked ClickUp tasks while an agent
is offline. It calls the same scoped reconciliation used by the CLI/MCP. It
copies discussion snapshots only; it cannot create tasks/issues, edit artifact
bodies, change status, merge, or judge acceptance.

Setup does not start a worker or install a service. A setup agent can prepare
and start it on one authenticated, always-on machine. Use one worker owner for
each task across machines. A polling process is not a webhook or a deployed
service, and this feature is not evidence that the native integration is enabled.

## Prepare and preview

The machine needs the installed helper, `gh`, the selected local ClickUp runtime,
and each service's own authentication. An editor's hosted MCP OAuth session is
not local CLI authentication. Keep credentials out of tracked files and service
arguments. Use an existing project binding and linked tasks; the worker never
chooses a task from local focus, discovers an entire workspace, or changes scope.

Have the setup agent run a read-only preview:

```bash
cu-work --project-dir /absolute/project sync-worker --task 86native
```

Repeat `--task` for each task in the worker's allowlist. Use `--direction
to-clickup` or `--direction to-github` to restrict copying. The JSON report shows
counts and task IDs without source comment bodies. Preview creates no operation
receipts, health record, or remote writes. It still needs authenticated reads.

For a managed npx installation, use the installed runtime's persistent Python
and `scripts/run_work.py` paths shown in the client's `clickup_work` command;
replace its final `mcp` argument with the command above. The Python invocation
keeps `-I`. `npx --yes github:randrescastaneda/clickup-skills work --project-dir
/absolute/project sync-worker --task 86native` also supports a manual preview.
Use persistent paths for the running service so it does not fetch new code when
restarted. No dependency installs or updates run inside the polling loop.

## Run a bounded pass or keep polling

```bash
# One pass. At most 20 new destination comments across all supplied tasks.
cu-work --project-dir /absolute/project sync-worker --task 86native --apply

# Continuous polling, five minutes after each completed pass.
cu-work --project-dir /absolute/project sync-worker --task 86native \
  --apply --watch --interval 300 --max-writes 20
```

`--apply` explicitly enables writes. Without `--watch`, the command exits after
one pass. Intervals must be at least 60 seconds; the per-pass limit is 1–100.
All tasks and associated discussions are read before the first write. A scope
failure, incomplete history, malformed identity, or excess backlog blocks that
pass. The write limit counts new mirrors; existing verified mirrors and completed
receipts do not consume it. Partial writes cannot be rolled back across services.

For a large initial backlog, preview it and set the intended explicit limit or
use directional passes. Do not raise the limit to bypass an incomplete history.
The process rechecks the binding each pass and exits if it changes. The task list
and direction stay fixed until restart.

## Ownership, health and recovery

Only one worker can own a local Git repository, including its linked worktrees.
Foreground CLI/MCP writes use the same repository-wide OS lock during a pass;
the worker releases that lock while waiting. Locks release when the process
exits or is killed, so a crash does not leave a new-version lock stuck. The lock
files remain on disk; their existence does not indicate an active owner. A legacy
`write.lock` still requires inspection before removal. Stop old helper processes
before upgrading; old versions do not participate in the new shared OS lock.

Receipts remain in private per-worktree Git state. Matching remote provenance
also prevents repeated mirrors after a restart or receipt loss. Multiple tasks
can share a PR without sharing a receipt key. Locks are local to one clone;
they do not prevent a second machine or separate clone from racing. Coordinate
one writer per task and preserve the state directory on the worker machine.

Each applied pass updates `worker-status.json` beside the workflow receipts,
with a timestamp, binding digest, task IDs, counts, and `healthy`, `blocked`, or
`stopped` status. JSON lines are flushed to stdout during watch mode. A stale
timestamp signals that the process may have stopped; `healthy` describes the
last completed pass, not ongoing availability. The report stores no source
bodies, credentials, or arbitrary subprocess errors.

Any exception exits the loop with a nonzero status. The worker does not retry
uncertain mutations, switch backends, or mark them not-applied. Inspect the
pending receipt and complete remote history. On restart, a matching remote marker
can recover the successful side; absent evidence blocks replay. Start the same
command after resolving the underlying failure. Avoid automatic restart loops
that hide a blocked worker. Ctrl+C stops polling normally. A killed process may
leave its last health report unchanged; remote receipts govern recovery.

## Complete comment histories

The reviewed `cup comments` and REST MCP `list_comments` expose one page. The
default helper therefore refuses histories of 25 comments; the worker also
refuses a pass that would reach that boundary. For longer discussions, explicitly
select the narrow, GET-only ClickUp API comment reader in the binding:

```json
{"routing": {"comment_reader": "clickup-api"}}
```

Add this property to the existing `routing` object without removing its other
settings. New bindings also support `init --comment-reader clickup-api`. Give
that process a private `CLICKUP_API_KEY` or `CLICKUP_API_KEY_FILE` for the intended
account. Do not set both, put the key in the binding, or paste it into chat. The
reader does not inspect cup's credential store or reuse a hosted MCP session.
Its credential must have access to the same bound tasks. Authentication and
live account acceptance remain separate from offline behavior checks.

Only comment reads use this explicit override. Task scope checks and all writes
continue through the selected `cup`/REST runtime; there is no automatic fallback.
The reader uses the [documented comment endpoint](https://developer.clickup.com/reference/gettaskcomments)
with both timestamp and comment ID cursors. It deduplicates overlapping pages,
handles equal timestamps, and stops on malformed, changing, stalled or oversized
histories. It follows no redirects with credentials, permits no configurable API
host, and makes no writes. Each history is bounded to 1,000 pages; reaching that
bound is a failure, not proof of complete history. ClickUp rate limits still apply.
Preview a full pass before starting the worker. Existing non-sync pending writes
must be resolved before changing the binding/reader; their operation keys bind
to the original binding digest.

This fills a missing read capability while reusing the upstream integrations
for all task operations and writes. No upstream private imports or dependency
updates are needed. The default remains `upstream` for existing installations.

## Current boundaries

ClickUp threaded replies are not exported. GitHub submitted reviews and inline
review replies are imported as source-linked snapshots. Edited source text
creates a new snapshot; deletion and arbitrary fields do not propagate.

Offline tests cover preview isolation, scope/budget preflight, repeated passes,
source edits, lost responses on both services, legacy receipt recovery, multiple
tasks sharing a PR, binding changes, and OS lock release after process death.
The packaged installer includes the worker after its downloaded source is deleted.
Pagination fixtures exercise more than one page, inclusive overlap, equal
timestamps, malformed cursors, stalled pages, and credential/error isolation.
Live authenticated worker operation and installed-editor loading remain rollout
acceptance checks. No worker is deployed by this repository's CI.
