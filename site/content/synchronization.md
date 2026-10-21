---
title: GitHub, ClickUp & sync
description: What is linked, what is copied, and which parts keep running after an agent session ends.
section: Work with your agent
---
# Connected work, explicit synchronization.

Three layers do different jobs: the plugin coordinates scoped work during an agent session; ClickUp’s native GitHub integration associates activity; optional native automations react to configured events. Installing or authenticating an MCP does not enable the other layers.

## What the plugin keeps connected

| Operation | Behavior |
| --- | --- |
| Create a subtask | Verify a bound repo/issue/PR first; create or reuse an issue by default; include the target in the initial child description |
| Link an implementation PR | Preserve unrelated PR text; add the ClickUp URL, `CU-TASK_ID` and objective in a managed block; record the PR on ClickUp |
| Record progress | Include links and mirror to associated issue/PR discussions |
| Reconcile comments | Copy source-linked discussion snapshots with deduplication and echo suppression |
| Mark done | Require the linked merged non-draft PR, correct base, successful latest PR-head checks and verification summary |

An explicit repository target works for planning, but it has no issue/PR discussion thread for comment reconciliation. A nonexistent issue/PR URL is an error; the agent must create a real issue instead of guessing its number.

## What discussion reconciliation includes

GitHub issue comments, PR conversation comments, submitted reviews, and inline review comments can be imported into ClickUp. The local helper exports **top-level ClickUp comments** to GitHub. Source URLs, event identities, and content revisions travel with the snapshots. Edited source text produces a new revision; deletions are not propagated.

The default local ClickUp commands expose one page. At 25 comments, the helper stops rather than assume a complete history. An explicit `routing.comment_reader = clickup-api` override provides GET-only cursor pagination using private environment credentials; writes remain on the selected upstream runtime. See the [worker guide](sync-worker.html) for setup. Use host tools for threaded replies. Pending/unsubmitted GitHub reviews are not available until GitHub exposes them.

**Arbitrary fields, assignees, labels and status are not synchronized in both directions.** The task objective and acceptance remain authoritative in ClickUp; code, reviews, CI and merge state remain authoritative in GitHub. Mirrored discussion keeps the source comment authoritative.

## When synchronization runs

Session tools run when called. Skills ask agents to reconcile at session start and handoff; you can also request it explicitly. An optional [sync worker](sync-worker.html) can poll an explicit set of tasks on an authenticated machine. It defaults to a read-only preview; setup does not start a service. Native activity links can continue when agents are offline; native automations handle only the events and rules an admin configured.

The worker uses the existing receipts, scope checks, and echo suppression, with a per-pass write limit and one local repository owner. It stops on uncertain outcomes or a changed binding. The 25-comment boundary remains for default readers; the explicit complete-history reader supports longer discussions. Live worker acceptance and deployment remain unfinished; separate machines still require one agreed writer per task. Arbitrary fields and statuses are not synchronized.

## Completion is an evidence gate

The helper checks the linked PR’s expected repository/base, managed task link, merged non-draft state and latest PR-head check rollup. An empty check rollup passes only with the explicit project policy `require_checks=false`. It also requires a nonempty verification summary. The agent must assess acceptance and the truth of the evidence itself.

Avoid a native “PR merged → Done” automation; merge alone does not prove task acceptance. A reminder to verify acceptance is appropriate.

## Host MCP-only environments

With no local shell, agents may load the shared skills and use available ClickUp and GitHub host MCPs directly. They must discover current schemas, freshly verify Workspace/List/ancestry and repository/base, create GitHub targets first, preserve body text and provenance, and enforce the same completion gate.

These calls are outside `cu-work` and are **not** captured by its local journal. Record operation IDs and remote evidence separately. If the task response omits Workspace identity, establish it using the explicit Workspace hierarchy and matching Space/List; do not infer it from a task URL.

## Recovery after partial failure

A GitHub issue, ClickUp subtask, backlink or mirror may succeed before another step fails. Preserve the successful side. Reuse an operation key only with identical inputs and reconcile remote markers before retrying an uncertain write. A missing marker alone does not prove failure. Never switch backends to replay an uncertain mutation.

See the [full execution contract](contract.html), [native integration guide](github-integration.html), and [troubleshooting](troubleshooting.html).
