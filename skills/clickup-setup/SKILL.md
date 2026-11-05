---
name: clickup-setup
description: Install, authenticate, validate, or update ClickUp Skills. Choose hosted ClickUp with independent GitHub CLI or hosted access, strict remote-only, or the optional local helper. Use for onboarding, safe configuration and diagnosing setup.
---

# Guided ClickUp Skills setup

Select ClickUp and GitHub backends independently. Preserve existing settings,
customized skills and sessions. Keep credentials outside chat and Git. Native
ClickUp–GitHub integration is separate from the coding agent's GitHub access.

## Hosted ClickUp + GitHub CLI (default)

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --mode hosted --github cli
```

The convenience installer requires Node 22+, Python 3.11+, Git and an already
allowed GitHub CLI. It copies six skills and configures official hosted ClickUp
MCP at `https://mcp.clickup.com/mcp`. It never installs/authenticates `cup`,
`cu-work`, a ClickUp app or a bridge, and never requests a ClickUp token.
It checks existing `gh` sign-in and offers GitHub's browser login when needed.
Reuse that account across authorized repositories; verify each exact target.
Do not create a GitHub token for each repository. If `gh` is missing, report
the prerequisite; do not silently install it or change the selected backend.

Omitting mode/backend flags selects this combination. Rerun the same command to
update it. `setup`/`update` still select the separate local ClickUp helper.
Use `--skip-skills` when another installer such as Vercel owns those copies.

After updating Kilo VS Code, use **Developer: Reload Window** and a fresh task.
Compare skill-loader bodies with installed files: the observed 7.8.18 backend
cached old bodies despite a new task. Do not delete caches/copies speculatively.

Only the running agent can verify ClickUp OAuth. Discover the six skills and real
MCP schemas, then read authenticated Workspace/List/root ancestry and GitHub
repository identity. A connected/configured server alone is insufficient.

## Hosted GitHub or strict remote-only

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --mode hosted --github hosted
# Strict no-local-service-tools variant; legacy --mode oauth is its alias:
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --mode remote-only
```

These variants never invoke `gh` authentication. Verify an approved existing
hosted GitHub connection with actual repository/issue/PR/check tools. Kilo's
earlier GitHub OAuth DCR attempt failed; this does not establish incompatibility
with every supported authentication method. Do not create credentials/apps or
broaden organization access without explicit authorization.

For no extra local tools, import the six skill directories and references from a
reviewed repository copy into an existing compatible host. Preserve MIT notices
and configure direct ClickUp HTTP/OAuth and approved hosted GitHub in that host.
There is no universal manifest/import format. `npx mcp-remote` is a local bridge.
Missing/banned selected connections mean STOP; strict remote-only forbids `gh`.

## Local-helper (explicit)

```bash
npx --yes github:randrescastaneda/clickup-skills onboard --client kilo --mode local-helper
```

Legacy `--mode cli` and software-only `setup`/`update` remain supported. They
install the private Python runtime, Krodak CLI and `clickup_work`, using `gh`
for GitHub. ClickUp CLI token authentication is separate from hosted OAuth.
Helper receipts, OS locks and completion checks require a valid project binding;
they do not protect direct hosted calls. Do not use preserved local helpers as
a hosted ClickUp fallback or replay an uncertain write through another backend.

## Native integration and first writes

Prefer configured native ClickUp–GitHub activity linking and approved automations
for their actual coverage. They do not automatically expose GitHub operations to
Kilo through ClickUp MCP, or synchronize every comment. Use the selected GitHub
backend for direct issue/PR edits, code review and CI verification. Establish one
owner for issue creation/comment mirroring to avoid duplicates.

Load the [guarded issue-first host protocol](../clickup-github/references/official-mcp-issue-first.md)
before any hosted write. Verify exact scope, GitHub target, complete duplicates,
bounded writes, readback and uncertain outcomes. These are agent safeguards,
outside helper journals/locks/gates. Do not update tools during task writes.
Native connections, automations and permanent workers require separate setup.
