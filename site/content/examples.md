---
title: Usage examples
description: Copy a prompt, replace the placeholders, and let your agent handle the workflow.
section: Work with your agent
---
# A prompt for the work in front of you.

These are **illustrative requests**, not actions performed by this website. Replace `<task-URL>`, `<PR-URL>` and other placeholders with real artifacts inside your bound project. Copy a prompt into your coding agent; it operates the tools.

<div class="example-filters" role="group" aria-label="Filter examples"><button class="filter active" data-filter="all" aria-pressed="true">All examples</button><button class="filter" data-filter="start" aria-pressed="false">Start & plan</button><button class="filter" data-filter="build" aria-pressed="false">Build & review</button><button class="filter" data-filter="team" aria-pressed="false">Sync & handoff</button><button class="filter" data-filter="recover" aria-pressed="false">Recover</button></div>

<div markdown="1" class="example" data-category="start">

## 01. Check readiness without changing tasks

```prompt
Check this project's ClickUp Skills setup. Read the binding, verify the actual
root task scope and repository origin, and discover the available tools.
Report missing installation, sign-in, permissions or status mapping. Read only;
do not create tasks or update statuses.
```

**Expect:** A short readiness report that distinguishes installed tools from verified remote access.

</div>
<div markdown="1" class="example" data-category="start">

## 02. Resume an existing task

```prompt
Resume <task-URL> using this project's binding. Read current subtasks,
associated GitHub issues/PRs and relevant discussions. Inspect pending operation
receipts before writing. Summarize the objective, completed work, blockers and
next useful action, then continue work already authorized by the task.
```

**Expect:** A current-state summary and continuation that preserves existing work.

</div>
<div markdown="1" class="example" data-category="start">

## 03. Turn an objective into useful subtasks

```prompt
Plan the deliverables for <task-URL>. Reuse existing children and create new
subtasks only for independently trackable work. Verify an existing GitHub target
before each child; create or reuse an issue first when none exists. Include clear
acceptance criteria and reciprocal links. Stay within the bound task tree.
```

**Expect:** A small task plan with real GitHub targets; no duplicate issue/child pairs.

</div>
<div markdown="1" class="example" data-category="build">

## 04. Build a data dashboard

```prompt
Implement the dashboard described in <task-URL>. Preserve the recorded objective.
Validate source data and transformations, check important totals and edge cases,
and verify the interface. Track useful subtasks with GitHub targets and post
milestone progress with evidence. Open and link the PR when ready for review.
```

**Expect:** Implementation, meaningful data/UI checks, linked deliverables and review readiness.

</div>
<div markdown="1" class="example" data-category="build">

## 05. Fix a reproducible bug

```prompt
Investigate the bug in <task-URL>. First reproduce it and identify the cause.
Implement a focused fix, verify the failing case and relevant surrounding
behavior, then link the PR. Record what failed before and what passes now.
Leave the task open until the completion gate is satisfied.
```

**Expect:** A focused fix with before/after evidence and an associated PR.

</div>
<div markdown="1" class="example" data-category="build">

## 06. Coordinate a research workflow

```prompt
Use <task-URL> to organize the approved research deliverable. Separate data
validation, analysis and writing only where each is independently trackable.
Associate every new child with a GitHub target, preserve source references,
and record results and limitations at milestones. Do not mark a research task
done under the helper's code-completion gate without its required PR evidence.
```

**Expect:** Traceable research work with explicit acceptance. The helper's done gate remains PR-based.

</div>
<div markdown="1" class="example" data-category="build">

## 07. Use an existing issue for a new subtask

```prompt
Create a scoped validation subtask under <task-URL> and associate it with
<issue-URL> in the bound repository. Verify that issue exists before creating
the child, preserve its body, and add reciprocal task links. Reuse a matching
existing child instead of duplicating it.
```

**Expect:** One child linked to the actual existing issue.

</div>
<div markdown="1" class="example" data-category="build">

## 08. Record a useful progress update

```prompt
Record this milestone on <task-URL>: the input validation is implemented,
the agreed edge cases pass, and the remaining blocker is the reviewer decision.
Verify those claims against the work, include the task and GitHub links, and
mirror the update to associated issue/PR discussions without duplicating an
existing identical update.
```

**Expect:** A concise evidence-based update on the connected artifacts.

</div>
<div markdown="1" class="example" data-category="build">

## 09. Prepare a PR for review

```prompt
Prepare the changes for <task-URL> for review. Run the appropriate checks,
create or reuse the implementation PR, and link it in both systems. Preserve
all unrelated PR description text. Set the exact mapped review status only
when ready; do not mark the task done.
```

**Expect:** Linked PR, check evidence and the configured review state.

</div>
<div markdown="1" class="example" data-category="build">

## 10. Verify completion after merge

```prompt
Assess whether <task-URL> can be completed. Read the current linked PR and
latest PR-head checks, confirm it is merged and non-draft into the bound base,
and verify every acceptance criterion against actual evidence. Record the PR
URL, head SHA and verification summary. Mark done only if all gates pass;
otherwise report the exact gap and leave it open.
```

**Expect:** Completion with evidence, or a precise reason the task remains open.

</div>
<div markdown="1" class="example" data-category="team">

## 11. Reconcile the two conversations

```prompt
Reconcile discussion snapshots between <task-URL> and its linked issue/PR.
Preserve source links, IDs and content revisions, skip generated mirrors,
and avoid duplicates. Fetch the complete relevant history. If local ClickUp
reads hit the 25-comment boundary, stop and use a paginated host read path;
do not assume the first page is complete. Do not change statuses.
```

**Expect:** Source-linked discussion snapshots, not a claim of continuous synchronization.

</div>
<div markdown="1" class="example" data-category="team">

## 12. Import GitHub feedback in one direction

```prompt
For <task-URL>, reconcile available GitHub conversation comments, submitted
reviews and inline review comments into ClickUp only. Preserve provenance and
skip echoes. Do not export ClickUp comments or change any task status.
```

**Expect:** Directional reconciliation that respects the selected audience.

</div>
<div markdown="1" class="example" data-category="team">

## 13. Hand off to a teammate or another agent

```prompt
Prepare a concise handoff for <task-URL>. Reconcile the linked discussion where
possible and report objective, task URL, branch/PR and head SHA, completed work,
checks actually run, blockers, pending operations and next action. Preserve
successful writes and identify anything the next agent must inspect before retry.
```

**Expect:** Enough verified state to continue without repeating work.

</div>
<div markdown="1" class="example" data-category="team">

## 14. Coordinate two agents

```prompt
Plan parallel implementation for <task-URL>. Propose separate worktrees and
explicit task IDs for each independently trackable deliverable. Resolve GitHub
targets before creating children, reuse existing ones, and assign one writer
per task. Explain any shared state before implementation starts.
```

**Expect:** A bounded plan that avoids shared focus and cross-machine receipt assumptions.

</div>
<div markdown="1" class="example" data-category="recover">

## 15. Recover from a timed-out task write

```prompt
The last write on <task-URL> timed out. Inspect pending receipts and the complete
relevant remote markers/history before any retry. Determine which side applied.
Preserve successful writes, reuse identical operation inputs only for verified
recovery, and do not replay through another backend. If the outcome cannot be
established, stop that mutation and explain the missing evidence.
```

**Expect:** Recovery based on remote evidence, without duplicate task creation.

</div>
<div markdown="1" class="example" data-category="recover">

## 16. Diagnose missing GitHub write permission

```prompt
GitHub reads work but an issue write returned 403. Check the actual repository
owner organization/account and the GitHub App's installation/repository access.
Distinguish my personal repository role from the integration's permissions.
Do not retry the write until its outcome and authorization are clear.
```

**Expect:** A specific permission diagnosis rather than a blind repeat.

</div>
<div markdown="1" class="example" data-category="start">

## 17. Work through host MCPs with no local shell

```prompt
Use the shared ClickUp Skills through this session's existing host ClickUp and
GitHub MCPs. Discover actual schemas, read the project binding, verify Workspace,
List, ancestry and repository/base before writes, and preserve operation IDs
and provenance. Enforce the same GitHub-first and completion rules. Do not claim
these host calls are journaled by the local helper.
```

**Expect:** Equivalent agent-enforced rules with an explicit host-only evidence trail.

</div>
<div markdown="1" class="example" data-category="team">

## 18. Review optional native integration setup

```prompt
Check what this team still needs for native GitHub activity links in ClickUp.
Distinguish MCP sign-in, repository/Space mapping and optional automation rules.
Give the admin a concrete checklist and a small verification case. Do not claim
a webhook, background worker or automation is installed merely because the
plugin is available. Do not enable automatic Done on merge.
```

**Expect:** Admin setup guidance and a separate verification of native behavior.

</div>
