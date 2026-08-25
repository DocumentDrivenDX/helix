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
| Reconcile artifacts, check traceability, find drift, align documents, or move content between artifact layers | [align](align) |
| Check an artifact instance against its template and prompt; edit resolvable findings in place | [validate](validate) |
| Bring every artifact instance up to date with the current templates and prompts | [refresh](refresh) |
| Thread a new, changed, removed, or incident-driven requirement through existing artifacts | [evolve](evolve) |
| Create a technical design before implementation | [design](design) |
| Reconstruct missing or incomplete docs from evidence | [backfill](backfill) |
| Fresh-eyes review of recent work, PRs, plans, or implementation | [review](review) |
| Refine work items for execution readiness | [polish](polish) |
| Plan or report a human iteration — sequence a roadmap, define workstreams, cut an iteration/sprint plan, write a status report | [iterate](iterate) |
| Decide the next safe HELIX action | [check or next](check-and-next) |
| Run an optimization experiment | [experiment](experiment) |
| Bootstrap a brand-new project from bare intent (name, research, vision, scaffold) | genesis |
| Drive a plan or completed work to convergence: review adversarially, fix, re-review until clean | converge |
| Audit where a project stands (specs↔impl↔tests↔ACs aligned? complete? next action?) | project-audit |
| Decompose an oversized code module/file into encapsulated units behind a verify gate | decompose-module |
| Build up end-to-end coverage as a ladder of increasingly complex real-client scenarios | e2e-ladder |

## Contracts

{{< cards >}}
  {{< card link="input" title="Input" subtitle="Use for sparse user intent that needs to become governed HELIX work." >}}
  {{< card link="grill" title="Grill" subtitle="Use to stress-test a plan, design, or change via a decision-tree interview until shared understanding. Distills the grilling technique (one question at a time,…" >}}
  {{< card link="frame" title="Frame" subtitle="Use for creating or refining product vision, PRD, feature specs, and user stories." >}}
  {{< card link="align" title="Align" subtitle="Use for reconciliation, traceability audits, drift checks, and artifact content placement reviews." >}}
  {{< card link="validate" title="Validate" subtitle="Use to check a single artifact instance against its governing template and prompt, then edit resolvable findings in place." >}}
  {{< card link="refresh" title="Refresh" subtitle="Use to bring every artifact instance under a project HELIX tree up to date with the current canonical templates and prompts. §Refresh is §Validate (fix-mode) a…" >}}
  {{< card link="evolve" title="Evolve" subtitle="Use when the user wants to add, remove, amend, or thread a requirement through the HELIX artifact stack." >}}
  {{< card link="design" title="Design" subtitle="Use when implementation needs design authority before build work." >}}
  {{< card link="backfill" title="Backfill" subtitle="Use to reconstruct missing or incomplete HELIX artifacts from evidence." >}}
  {{< card link="review" title="Review" subtitle="Use for fresh-eyes review of plans, PRs, implementation, or recent work." >}}
  {{< card link="polish" title="Polish" subtitle="Use to refine work items before execution." >}}
  {{< card link="iterate" title="Iterate" subtitle="Use to plan or report a human iteration: sequence a roadmap, define workstreams, cut an iteration plan from the backlog and roadmap, or record status against t…" >}}
  {{< card link="check-and-next" title="Check And Next" subtitle="Use when the safe next action is ambiguous, when the user asks &quot;what's next&quot; / &quot;what's blocked&quot; / &quot;plan the change&quot;, or when a single ask straddles two or more…" >}}
  {{< card link="runtime-handoff" title="Runtime Handoff" subtitle="Use when a workflow mode concludes that the next step is execution, source control, packaging, or a long-lived operator loop. HELIX does not own those surfaces…" >}}
  {{< card link="experiment" title="Experiment" subtitle="Use for metric-driven optimization loops." >}}
{{< /cards >}}
