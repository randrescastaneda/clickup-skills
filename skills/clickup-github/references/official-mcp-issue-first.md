# Official ClickUp MCP + GitHub: guarded host-agent workflow

This is the **agent-executed** protocol for browser-OAuth installations. It applies
when ClickUp is accessed through the host's official MCP and GitHub through
\`gh\` or a separately authenticated GitHub MCP. It is not the local \`clickup_work\`
helper. The host does not get the helper's binding enforcement, OS locks or
durable receipts; never say that passing these steps provides those guarantees.
Do not access \`cup\`, import its private token store, or silently switch to the
helper when an official-MCP operation fails.

## 0. Obtain exact authorization and establish a session boundary

Require an explicit user-approved objective, **native** ClickUp Workspace ID,
home List ID, allowed root task(s), and GitHub \`OWNER/REPO\`/base branch. Reuse a
verified \`.clickup/project.json\` if present, but never infer a binding from
the current directory, a task title or a Git remote alone. Without these
values, request the missing scope and make **no writes**.

The agent must have an explicit budget for each write type (task, issue, body
edit, comment, status). Do not turn a read-only request into a write. Do not
grant permissions or start workers/automations. Agree on **one writer** per
task/issue before any mutation.

Check which MCP servers the actual client loaded, discover their **current
schemas**, and verify the official ClickUp OAuth identity and Workspace access.
Using \`gh\` additionally requires \`gh auth status\`; a GitHub hosted MCP has its
**own** OAuth and repository permissions. A connected local \`clickup_work\` MCP
is *not* proof of its ClickUp CLI authentication.

## 1. Read-only scope and duplicate preflight

All checks must pass before writing:

1. **ClickUp** — exact root/parent ID and task identity; Workspace membership
   through the official hierarchy; matching Space and **home List**; native
   parent chain ending inside an approved root. Compact MCP task results
   sometimes omit \`team_id\`; do not treat its absence as approval. Fetch exact
   statuses from the List, including the intended initial status.
2. **GitHub** — exact repository owner/name; confirm issue/PR target exists in
   that repository, has suitable scope and the expected PR base if relevant.
   Repository-only targets may support planning but cannot hold discussion
   backlinks. Never invent a numbered issue. If no target exists, obtain
   permission to create an issue **before** creating the ClickUp subtask.
3. **Search for duplicates** — load **all direct children** of the parent, plus
   the relevant task descriptions and comments, and the complete issue/PR
   backlink body. Respect each tool's pagination and truncation rules.
   Search for the intended stable operation marker and intended target URL.
   Use the official task's **\`text_content\`** for literal markers: ClickUp's
   \`markdown_description\` may escape brackets, wrap URLs, or reformat links.
   A search returning only the newest page is *not* proof of absence.

Use a stable, non-secret operation key chosen once per logical attempt:
\`[host-op:KEY]\`. **Do not manufacture \`[cu-work:...]\` receipts**; those
markers are reserved for the helper's binding-hashed protocol. The previous
OAuth pilot used \`[pilot-op:official-mcp-868mjzgzh-20261022-v1]\` and may be
reused *as evidence*, not as a new operation key.

| Preflight evidence | Mandatory decision |
| --- | --- |
| Exactly one matching child and a valid matching backlink | **REUSE** both; zero writes |
| Exactly one matching child, GitHub backlink missing, both snapshots complete | **RESUME** only the missing backlink after task read-back |
| No matching child, complete reads, verified target, user-approved creation | **CREATE** one child |
| Multiple/conflicting matches, wrong scope/target, incomplete reads or uncertain previous write | **STOP**; do not guess or retry |

## 2. GitHub first, ClickUp second

If a new issue is explicitly approved and needed, create it in the **bound**
repository, with the approved title and stable operation marker. Re-read the
returned canonical URL and issue body before creating a child. An existing
issue/PR must be re-read and reused instead of recreated.

Create **one** child under the exact authorized parent and List using the
official MCP's discovered \`create_task\` schema. Its *initial* description must
contain these literal strings (the human text may be longer):

\`\`\`text
GitHub: https://github.com/OWNER/REPO/issues/N
[cu-work-github:https://github.com/OWNER/REPO/issues/N]
[host-op:KEY]
\`\`\`

No unapproved assignees, custom fields, status transitions, or comments.
Immediately re-read the child by its returned ID. Verify **same parent, home
List, operation marker, target URL and association marker** in \`text_content\`.
If the write timed out or the read disagrees, stop and reconcile remotely;
do not create a replacement or make the next write.

## 3. Link back without clobbering GitHub

Re-fetch the latest issue or PR body immediately before editing. The backlink
block is bounded by exactly:

\`\`\`text
<!-- clickup-skills:TASK_ID -->
ClickUp: https://app.clickup.com/t/TASK_ID
CU-TASK_ID

Objective: APPROVED_OBJECTIVE
<!-- /clickup-skills:TASK_ID -->
\`\`\`

If the same block already exists correctly, **skip**. If it exists but
conflicts, is malformed or duplicated, **stop**. Otherwise append **only**
this one block; preserve the previous body exactly, except the required
separator newline. A body-only update must not change issue/PR title, state,
labels, review status, or branch. GitHub updates are **not atomic** with a
preceding read; another editor may race. Coordinate a single writer, and
verify the original portion and new block on read-back.

Do not use an issue-body rewrite to update a task's own description; add
subsequent activity as a comment. Link a new PR only when meaningful changes
exist and user/project scope permits it. Keep approved titles, human issue/PR
text, base branch and checks intact.

## 4. Recovery and guarded repeat

Persist successful IDs and the fixed operation key **in the current session**
or a user-approved private handoff. Never add fabricated receipts to the
helper's journal. A cross-service failure is **partial progress**, not a
transaction: preserve whichever side succeeded. To resume, re-fetch both
services, validate the existing marker/object identity and issue body, then
perform **only the remaining approved write**.

On a subsequent invocation, repeat the *read-only* preflight and expect REUSE
with **zero writes**. Do not call \`create_task\` a second time to test
idempotence. No inference of exactly-once behavior across separate clients,
machines, or simultaneous writers is justified.

If any remote write times out, returns an ambiguous result, or hits a rate
limit, **STOP**. Missing evidence is not proof of non-execution. Do not blindly
retry or change backend; escalate with source URLs, last known operation
state, and a request for human reconciliation when needed.

## 5. Comment and completion safety

For comment mirrors, paginate task comments, fetch threaded replies, and read
all GitHub issue/PR discussion pages and submitted reviews. Preserve source
identity, author, URL and revision; use the shared canonical
\`[cu-work-sync:EVENT_KEY]\` definition in \`synchronization.md\` so the helper
can recognize copies. Skip generated mirrors and do not propagate deletions.
Host tools do not automatically create a background worker.

Never move a task to Done unless acceptance, merged non-draft PR into the
bound base, latest PR-head successful checks, and recorded evidence all pass;
an explicit no-checks project policy is required for an empty rollup.
The official OAuth grant may include write access even when the **current
test** is read-only: honor the user-approved scope and write budget.

## Report

Report verified identities/scope, source URLs, target issue-before-child
evidence, exact read/write count (when observed), child ID, matching markers,
body preservation, guarded repeat result, and any unverified protections.
Use precise labels: **agent-guarded** (OAuth path) versus **helper-enforced**
(local \`clickup_work\` with valid project binding and personal token).
