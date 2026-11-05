# PR #26: hosted ClickUp + GitHub CLI acceptance

User-approved direction: use official hosted ClickUp OAuth MCP and GitHub CLI
for the coding agent's direct GitHub actions. Native ClickUp–GitHub integration
continues to handle its configured activity linking. This task supersedes the
earlier all-hosted diagnostic task only for this new backend combination.

- Implementation repository: `randrescastaneda/clickup-skills`.
- Exact implementation commit: `1abd0a79439f4b1b980fb74234416202c87766cf`.
- Implementation branch/PR: `feat/explicit-remote-only-mode`, PR #26.
- Report branch: `handoff/pr26-validation`.
- Reports: `agent-reports/pr26/`; next filename `2026-11-05-kilo-hosted-gh-01.md`
  (choose a new unused dated filename if needed).
- Read root AGENTS.md on the implementation revision and this handoff README.
- Preserve the current checkout and uncommitted work; use a separate worktree
  for source validation and another clean checkout/worktree for publication.
- The handoff branch's source baseline is historical. Do not install/test its old
  source as if it were the implementation revision above.

## A. Update the current installation

This task authorizes updating this existing Kilo installation to the implementation
revision and selecting hosted ClickUp + GitHub CLI. It does not authorize installing
the ClickUp CLI/helper, changing organization grants, or deleting existing settings.

1. Record Kilo/editor/OS versions and a sanitized settings baseline. Preserve
   customized skills; if the installer reports an ownership conflict, stop and
   report the exact paths without overwriting them. If Vercel owns the skills,
   update those copies through that existing manager to the same revision and
   use `--skip-skills` for configuration; do not let two installers own the copies.
2. Check that Node 22+, Python 3.11+, Git and `gh` are available. If a prerequisite
   is missing, publish a BLOCKED report with the smallest user installation step.
   Do not run an unrequested package manager or create a GitHub PAT.
3. Run this pinned update command in the terminal:

   ```bash
   npx --yes github:randrescastaneda/clickup-skills#1abd0a79439f4b1b980fb74234416202c87766cf onboard --client kilo --mode hosted --github cli
   ```

   It should reuse `gh` sign-in, or offer GitHub's browser flow if needed. If the
   browser login needs the user, ask them to complete that flow privately. Never
   print/export the token with `gh auth token`, request it in chat, populate the
   earlier empty MCP-token file, or use that file to authenticate this test.
   If non-interactive execution cannot complete browser login, have the user run
   this same command in an interactive terminal; do not alter the global account
   selection or widen organization access on your own.
4. Verify no local ClickUp runtime or personal ClickUp token was newly requested,
   installed or authenticated. Existing `clickup_work` may remain configured;
   do not call it. Record intended configuration differences from the backup.
   A user-managed hosted GitHub MCP may remain enabled/disabled; it is not needed
   for the selected GitHub CLI backend. Do not delete it or change its credentials.
5. **Reload boundary:** ask Andres to run **Developer: Reload Window** in VS Code,
   then start a fresh Kilo task and continue at B using this same document.
   Kilo 7.8.18 previously retained old skill bodies in its shared backend, so
   a new task alone is insufficient evidence of refresh. Before this boundary,
   save a local sanitized progress note or publish a setup report if blocked.
   Do not claim live acceptance from installer output.

## B. Verify the installed combination with actual reads

- Load all six installed skills through Kilo's loader and compare returned bodies
  with installed files. Compare all six complete SKILL.md file hashes against
  the pinned implementation revision. Record any mismatches; receipts with a
  content digest alone are not proof of an installed source commit.
- Discover the actual official ClickUp schemas and verify authenticated identity,
  Workspace `37469623`, Space `61389751`, List `193304782`, and test parent
  `868mjzgzh`, including native parent/home-List scope. Inspect only relevant
  scoped data; prefer complete parent-child reads over scanning the Workspace.
- Check `gh auth status --hostname github.com` without exposing credentials.
  Through `gh`, read:
  1. `PIP-Technical-Team/wbpip`, branch `PROD`, and issue `#269`.
  2. `randrescastaneda/clickup-skills` and PR `#26`.
  These different owners demonstrate reuse of the same selected GitHub account,
  without new per-repository tokens. Lack of access to either is BLOCKED, not
  permission to switch accounts, create credentials or broaden access.
- Distinguish native integration evidence from direct agent access. Record any
  actually observed native mapping/link behavior, but do not configure it or
  claim it passed from the existence of an OAuth connection. Check for known
  issue-creation/mirroring automation conflicts before writes.
- If any required check fails, make zero acceptance content writes and publish a
  report now. Never use a different service backend to hide a failure.

## C. One bounded workflow, only after B passes

Andres authorizes this session as the only test writer, with a lifetime maximum
of ONE ClickUp child creation and ONE body-only edit of existing GitHub issue
`PIP-Technical-Team/wbpip#269`. Reusing existing correct objects needs zero writes.

Do not create another issue/PR, change task/issue status, edit code, add comments,
merge, delete, enable automations/workers or alter the ClickUp parent. Existing
bindings must not be rewritten; this explicit test scope does not broaden them.

- Objective: Validate PR26 hosted ClickUp + GitHub CLI in Kilo.
- Child title: `[clickup-skills PR26] Hosted ClickUp + gh acceptance`.
- Fixed new-test marker: `[host-op:pr26-hosted-gh-kilo-v1]`.
- Target: `https://github.com/PIP-Technical-Team/wbpip/issues/269`.
- This is a new test for a different backend combination. The earlier
  `[host-op:pr26-remote-only-kilo-v1]` marker remains historical; do not reuse it
  for a changed payload. If unexpected partial work from it conflicts with the
  new test, stop and report before adding anything.

Follow the installed guarded issue-first protocol. Read the existing GitHub issue
before child creation. Fully paginate the parent's direct children and relevant
marker/comment/body evidence; use literal ClickUp `text_content` markers.
A truncated read, duplicate/conflicting match, observed automation conflict or
uncertain previous mutation means STOP, not proof of absence.

Create at most one child under the exact approved parent/home List, with the
target URL, `[cu-work-github:TARGET_URL]` association and fixed marker present
initially. Immediately read back ID, parent, List and literal markers. Only then
re-fetch the latest GitHub issue body and append exactly one protocol-managed
backlink block through a body-only `gh` update. Use a temporary body file with
`--body-file` to preserve newlines; preserve the entire original text and all
other fields. Do not overwrite a conflicting/malformed block. Read back the issue.

If any write times out or has an ambiguous response, stop and reconcile via fresh
reads on the selected backend. Do not blindly retry or switch to GitHub MCP/the
ClickUp helper. Preserve successful IDs and the fixed marker.

Repeat the complete read-only preflight. Verify exactly one matching child and
one valid backlink, then perform ZERO writes on that second pass. Do not call
create again to test duplicate prevention. Never mark the test Done.

## D. Publish the report for ChatGPT

Use REPORT_TEMPLATE.md and record installer/reload/hash evidence, actual service
tools and `gh` commands, both repository read results, scope, exact write counts,
returned child/issue URLs, original issue-body preservation, second-pass result
and remaining gaps. Separate live evidence from mocked/offline tests and prior
reports. Passing this combination does not establish all-hosted acceptance.

Run repository checks against the pinned implementation source and record its
commit, not just the older exchange source. Do not broaden testing by installing
new tools or making extra live writes. If a required check is blocked, say so.

Using existing Git authentication, publish only the sanitized report to the handoff
branch. The report commit is separately authorized and excluded from acceptance
content-write counts. Fetch before normal push, preserve existing reports, stage
only explicit report files, and verify the remote URL/commit. No force push or PR.
Never commit tokens, credential files, raw settings/backups, private task/comment
bodies or unredacted logs. If publication itself is blocked, retain the report
locally and state the exact path and blocker.

Return only the report URL, commit SHA, overall PASS/FAIL/BLOCKED, and the smallest
remaining user action. ChatGPT will review after Andres says “Review the latest
report”; there is no watcher or background polling.
