---
title: Workflow Modes
weight: 2
generated: true
---

The HELIX skill routes every request to one **workflow mode**: a bounded document or workflow action with its own contract. The table below maps user intent to the mode the skill selects; each linked mode opens the full contract the skill follows.

Generated from [`skills/helix/SKILL.md`](https://github.com/DocumentDrivenDX/helix/blob/main/skills/helix/SKILL.md), the HELIX skill. Edit the skill, not these pages.

| User intent | Workflow mode |
|---|---|
| Convert rough intent into governed HELIX work | [input](input) |
| Grill / interview / stress-test a plan or design until shared understanding (one question at a time) | [grill](grill) |
| Create or refine product vision, PRD, feature specs, or user stories | [frame](frame) |
| Reconcile relevant documents, check traceability, find drift, or place content in the right artifact | [align](align) |
| Check an artifact instance against its template and prompt; edit resolvable findings in place | [validate](validate) |
| Bring every artifact instance up to date with the current templates and prompts | [refresh](refresh) |
| Thread a new, changed, removed, or incident-driven requirement through existing artifacts | [evolve](evolve) |
| Create a technical design before implementation | [design](design) |
| Reconstruct missing or incomplete docs from evidence | [backfill](backfill) |
| Fresh-eyes review of recent work, PRs, plans, or implementation | [review](review) |
| Refine work items for execution readiness | [polish](polish) |
| Plan or report a human iteration — sequence a roadmap, define workstreams, cut an iteration/sprint plan, write a status report | [iterate](iterate) |
| Decide the next safe HELIX action | [check](check) |
| Run an optimization experiment | [experiment](experiment) |
| Bootstrap a brand-new project from bare intent (name, research, vision, scaffold) | [genesis](genesis) |
| Drive a plan or completed work to convergence: review adversarially, fix, re-review until clean | [converge](converge) |
| Explicitly audit a named scope across specs, implementation, and tests | [project-audit](project-audit) |
| Decompose an oversized code module/file into encapsulated units behind a verify gate | [decompose-module](decompose-module) |
| Build up end-to-end coverage as a ladder of increasingly complex real-client scenarios | [e2e-ladder](e2e-ladder) |
| Turn governed artifacts into a deck, one-pager, or brief for clients, sponsors, or executives | [present](present) |
| Hand governed work to the runtime for execution, source control, or packaging | [runtime-handoff](runtime-handoff) |

## Contracts

{{< cards >}}
  {{< card link="align" title="Align" subtitle="Use `align` to reconcile related HELIX documents, check traceability, or place content in the right artifact. The default scope is the requested document and t…" >}}
  {{< card link="backfill" title="Backfill" subtitle="Use to reconstruct missing or incomplete HELIX artifacts from evidence." >}}
  {{< card link="check" title="Check And Next" subtitle="Use when the safe next action is ambiguous, when the user asks &quot;what's next&quot; / &quot;what's blocked&quot; / &quot;plan the change&quot;, or when a single ask straddles two or more…" >}}
  {{< card link="converge" title="Converge" subtitle="Use when the user asks to review a target, resolve blocking findings, and repeat the review within a stated or agreed limit." >}}
  {{< card link="decompose-module" title="Decompose Module" subtitle="Use to decompose an oversized, poorly encapsulated code module into focused units, iteratively, behind a per-iteration verification gate. This is code-structur…" >}}
  {{< card link="design" title="Design" subtitle="Use when the requested change needs design authority before implementation." >}}
  {{< card link="e2e-ladder" title="E2E Ladder" subtitle="Use to build end-to-end coverage as a ladder of scenarios of increasing complexity, each rung a durable automated test that drives the real runtime boundary an…" >}}
  {{< card link="evolve" title="Evolve" subtitle="Use when the user asks to add, amend, remove, or thread a requirement through existing artifacts." >}}
  {{< card link="experiment" title="Experiment" subtitle="Use for metric-driven optimization loops." >}}
  {{< card link="frame" title="Frame" subtitle="Use for creating or refining product vision, PRD, feature specs, and user stories." >}}
  {{< card link="genesis" title="Genesis" subtitle="Use to bootstrap a brand-new project from bare intent: name it, research the prior art, draft a vision shaped by that research, and scaffold the HELIX structur…" >}}
  {{< card link="grill" title="Grill" subtitle="Use to stress-test a plan, design, or change via a decision-tree interview until shared understanding. Distills the grilling technique (one question at a time,…" >}}
  {{< card link="input" title="Input" subtitle="Use for sparse user intent that needs to become governed HELIX work." >}}
  {{< card link="iterate" title="Iterate" subtitle="Use to plan or report a human iteration: sequence a roadmap, define workstreams, cut an iteration plan from the backlog and roadmap, or record status against t…" >}}
  {{< card link="polish" title="Polish" subtitle="Use when the user asks to decompose or refine work items for a named scope. Infer the scope from the task; ask when it is unclear. Do not select all open work…" >}}
  {{< card link="present" title="Present" subtitle="Use to turn governed artifacts into a deck, brief, or one-pager a client, sponsor, or executive can read or watch on the first try. Output: a `deliverable` art…" >}}
  {{< card link="project-audit" title="Project Audit" subtitle="Use only when the user explicitly asks for an implementation audit. Confirm the requested project, component, feature, or other scope; ask for scope when the t…" >}}
  {{< card link="refresh" title="Refresh" subtitle="Use to bring every artifact instance under a project HELIX tree up to date with the current canonical templates and prompts. Refresh is `modes/validate.md` (fi…" >}}
  {{< card link="review" title="Review" subtitle="Use for an explicitly requested fresh-eyes review of a plan, artifact, change, or implementation." >}}
  {{< card link="runtime-handoff" title="Runtime Handoff" subtitle="Use when a workflow mode concludes that the next step is execution, source control, packaging, or a long-lived operator loop. HELIX does not own those surfaces…" >}}
  {{< card link="validate" title="Validate" subtitle="Use to check a single artifact instance against its governing template and prompt, then edit resolvable findings in place." >}}
{{< /cards >}}
