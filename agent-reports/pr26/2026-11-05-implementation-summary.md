# PR26 independent-backend implementation — 5 November 2026

Implementation commit: `1abd0a79439f4b1b980fb74234416202c87766cf`.
PR: https://github.com/randrescastaneda/clickup-skills/pull/26 (draft).

Default onboarding configures hosted ClickUp OAuth MCP and reuses/checks GitHub
CLI browser sign-in. Explicit `--github hosted` retains existing hosted access;
strict remote-only / legacy oauth still never invokes GitHub CLI. Invalid
combinations fail before setup. Local ClickUp runtime behavior is unchanged.

Native ClickUp–GitHub activity links and coding-agent GitHub tools are separately
documented. Existing user-managed settings are preserved. Hosted GitHub selection
does not disable an installer-owned remote entry; CLI selection retains the bounded
legacy migration. No per-repository GitHub PAT is needed for the CLI backend.

Local validation: 135 offline tests passed; Markdown 3.9 documentation build and
checks passed for 28 HTML pages; package dry-run, JavaScript syntax, relative skill
links, documentation-impact decision and diff whitespace checks passed.

A read-only independent instruction evaluation exercised default CLI routing,
strict remote-only refusal, uncertain-write reconciliation and native automation
ownership. It is not live acceptance. Its preservation finding was fixed with a
regression test. CI and live client evidence must be assessed on their actual
revisions; the new Kilo test has not yet run.

Current instructions: [TEST_HOSTED_CLICKUP_GH.md](TEST_HOSTED_CLICKUP_GH.md).
