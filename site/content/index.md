---
title: Overview
description: Project-bound ClickUp and GitHub workflows for coding agents.
section: Start here
---
<div class="home-intro">
<div class="hero">
<h1>Connect ClickUp and GitHub <em>in your coding agent.</em></h1>
<p class="hero-description">Give your agent a task. It checks project scope, links the work to GitHub, and records progress in ClickUp.</p>
<div class="hero-actions"><a class="button primary" href="installation.html">Install with your agent</a><a class="button secondary" href="examples.html">Explore examples</a></div>
<p class="home-install-note">Choose from <a href="installation.html#choose-an-installation-route">five installation methods</a>. We recommend starting with your own agent.</p>
</div>

<div class="workflow-demo" aria-label="Illustrative agent workflow">
<div class="demo-top"><span class="demo-label">Example task</span></div>
<div class="demo-prompt"><span class="micro-label">You</span><p>Work on the dashboard task. Keep ClickUp updated and link the PR when it’s ready.</p></div>
<div class="demo-result"><span class="micro-label">Your agent</span><ul><li>Verify the ClickUp task and repository.</li><li>Link a GitHub issue before creating a subtask.</li><li>Record progress and link the pull request.</li><li>Check the merge, CI results, and acceptance criteria before marking the task done.</li></ul></div>
</div>
</div>

## You describe the work. Your agent coordinates it.

ClickUp Skills is a workflow plugin for coding agents. Its default setup installs {{skill_count}} shared skills and connects ClickUp's official MCP through browser OAuth. It needs no Node: an agent can install it by following a [runbook](install-runbook.html). An **optional** local scoped helper exposes {{tool_count}} MCP tools for teams that want durable operation receipts and a separate token-backed CLI. **After setup, use natural language. Your agent operates the tools.**

<div class="feature-grid"><a class="feature" href="project-setup.html"><h3>Bind a project</h3><p>Connect the repository to its ClickUp workspace, list, and task tree.</p></a><a class="feature" href="using-the-plugin.html"><h3>Delegate work</h3><p>Ask your agent to link subtasks and GitHub issues, and record progress.</p></a><a class="feature" href="synchronization.html"><h3>Verify completion</h3><p>Preserve discussions and verify the merged PR, checks, and acceptance.</p></a></div>

## A clear division of responsibility

| You and your team | Your agent |
| --- | --- |
| Ask each coding agent you use to install the skills, then approve account access | Install and verify the skills and access for that agent |
| Choose the objective, repository, and ClickUp task | Verify scope before making task changes |
| Define acceptance criteria and review the result | Link subtasks, report progress, and provide evidence |
| Configure optional native integrations | Reconcile discussions when asked or at session boundaries |

<div class="callout"><strong>Start with your role.</strong> A workspace admin connects shared services. Each teammate installs and signs in on their own machine. A project lead supplies the task scope. <a href="installation.html#who-does-what">See the setup responsibilities →</a></div>

## Choose your next step

- **Setting up a team?** Follow [installation and responsibilities](installation.html).
- **No Node on the machine?** Have your agent follow the [install runbook](install-runbook.html).
- **Already installed?** [Bind your first project](project-setup.html), then copy a prompt from [usage examples](examples.html).
- **Evaluating the integration?** Read [how synchronization works](synchronization.html) and [validation status](validation.html).
- **Maintaining the plugin?** Explore the [generated agent reference](reference.html) and [documentation pipeline](maintenance.html).
