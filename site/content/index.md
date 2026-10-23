---
title: Overview
description: Project-bound ClickUp and GitHub workflows for coding agents.
section: Start here
---
<div class="hero">
<div class="eyebrow"><span class="status-dot"></span> BUILT FOR AGENTS. GUIDED BY YOU.</div>
<h1>Give your agent<br>a clear path <em>to done.</em></h1>
<p class="hero-description">One objective. Connected tasks. Work you can verify.<br>Bring ClickUp and GitHub into your agent’s everyday workflow.</p>
<div class="hero-actions"><a class="button primary" href="installation.html">Set up your team <span>↗</span></a><a class="button secondary" href="examples.html">Explore examples <span>→</span></a></div>
<div class="compatibility">WORKS WITH <span>Claude Code</span><span>Codex</span><span>Copilot</span><span>Kilo</span><span>+ more</span></div>
</div>

<div class="workflow-demo" aria-label="Illustrative agent workflow">
<div class="demo-top"><span class="demo-label"><span class="status-dot"></span> A CONNECTED WORKFLOW</span><span class="subtle">Illustrative example</span></div>
<div class="demo-prompt"><div class="avatar">Y</div><div><span class="micro-label">YOU SET THE DIRECTION</span><p>Work on the dashboard task. Keep ClickUp updated and link the PR when it’s ready.</p></div></div>
<div class="demo-result"><div class="avatar agent">↗</div><div><span class="micro-label">YOUR AGENT HANDLES THE WORKFLOW</span><div class="task-line"><span class="tick">✓</span> Verify project and task scope <span class="tag">ClickUp</span></div><div class="task-line"><span class="tick">✓</span> Link an issue before creating a subtask <span class="tag">GitHub</span></div><div class="task-line"><span class="tick">✓</span> Record progress and connect the PR <span class="tag">Both</span></div><div class="task-line"><span class="pending">◷</span> Wait for merge, checks, and acceptance <span class="tag neutral">In review</span></div></div></div>
<div class="demo-bottom">A linked PR is progress. Verified acceptance is completion.</div>
</div>

## You describe the work. Your agent coordinates it.

ClickUp Skills is a workflow plugin for coding agents. Its default setup installs {{skill_count}} shared skills and connects ClickUp's official MCP through browser OAuth. An **optional** local scoped helper exposes {{tool_count}} MCP tools for teams that want durable operation receipts and a separate token-backed CLI. **After setup, use natural language. Your agent operates the tools.**

<div class="feature-grid"><a class="feature" href="project-setup.html"><span class="feature-number">01 / DEFINE</span><h3>Start with a real objective</h3><p>Bind the repository to the right workspace, list, and task tree. Keep the work inside that scope.</p><span class="text-link">Bind a project →</span></a><a class="feature" href="using-the-plugin.html"><span class="feature-number">02 / DELEGATE</span><h3>Keep the work connected</h3><p>Your agent creates useful subtasks, associates GitHub targets, and records meaningful progress.</p><span class="text-link">See the daily workflow →</span></a><a class="feature" href="synchronization.html"><span class="feature-number">03 / VERIFY</span><h3>Make “done” mean done</h3><p>Link evidence, preserve discussions, and verify the merged PR, latest-head checks, and acceptance.</p><span class="text-link">Understand the rules →</span></a></div>

## A clear division of responsibility

| You and your team | Your agent |
| --- | --- |
| Install skills and runtime once per teammate; approve account access | Discover installed skills and available tools |
| Choose the objective, repository, and ClickUp task | Verify scope before making task changes |
| Define acceptance criteria and review the result | Link subtasks, report progress, and provide evidence |
| Configure optional native integrations | Reconcile discussions when asked or at session boundaries |

<div class="callout"><strong>Start with your role.</strong> A workspace admin connects shared services. Each teammate installs and signs in on their own machine. A project lead supplies the task scope. <a href="installation.html#who-does-what">See the setup responsibilities →</a></div>

## Choose your next step

- **Setting up a team?** Follow [installation and responsibilities](installation.html).
- **Already installed?** [Bind your first project](project-setup.html), then copy a prompt from [usage examples](examples.html).
- **Evaluating the integration?** Read [how synchronization works](synchronization.html) and [validation status](validation.html).
- **Maintaining the plugin?** Explore the [generated agent reference](reference.html) and [documentation pipeline](maintenance.html).
