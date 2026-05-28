---
title: Research Foundations
weight: 6
---

HELIX is not a new runtime, a new tracker, or a replacement for the software
practices teams already trust. It is a methodology layer that turns those
practices into durable artifacts an AI-assisted team can read, reconcile, and
act on.

This section collects the research foundations behind that shape: when to do
research, which existing software-development practices HELIX borrows from,
and which HELIX artifacts already came from research work.

## Start with the research method

HELIX uses research when uncertainty is high enough that moving directly into
requirements, design, or implementation would bake in unsupported assumptions.
The internal [research methodology](https://github.com/DocumentDrivenDX/helix/blob/main/docs/research-methodology.md) defines the trigger: high uncertainty,
high stakes, novel domains, assumption-heavy decisions, or stakeholder
disagreement.

The method is deliberately bounded. Research should be evidence-based,
time-boxed, actionable, risk-reducing, and integrated back into Frame and Design
artifacts. The point is not to create a parallel analysis process. The point is
to answer enough of the right questions that the artifact stack can govern the
next decision.

{{< cards >}}
  {{< card link="/artifact-types/research-plan/" title="Research Plan" subtitle="Plan user, market, or problem-space investigation before committing to requirements." icon="academic-cap" >}}
  {{< card link="/artifact-types/feasibility-study/" title="Feasibility Study" subtitle="Evaluate viability across technical, business, operational, and resource constraints." icon="scale" >}}
  {{< card link="/artifact-types/tech-spike/" title="Technical Spike" subtitle="Time-box a specific technical unknown before locking an architecture decision." icon="beaker" >}}
  {{< card link="/artifact-types/proof-of-concept/" title="Proof of Concept" subtitle="Validate a high-risk technical approach end to end before full implementation." icon="cube-transparent" >}}
{{< /cards >}}

## What HELIX borrows from

HELIX treats established engineering practices as source material, not as
brands to repackage. The recurring pattern across the bibliography is simple:
make intent explicit, keep feedback loops short, build quality in early, and
reduce the cognitive load of teams doing complex work.

| Research source | HELIX connection |
|---|---|
| [Agile Manifesto](/research/agile-manifesto/) and [Agile principles](/research/agile-manifesto-principles/) | HELIX preserves change-friendly iteration, working-software feedback, simplicity, and regular reflection, but makes the supporting intent durable for agent sessions. |
| [Amazon / AWS Working Backwards PR-FAQ](/research/amazon-working-backwards-prfaq/) | HELIX uses the PR-FAQ as a Frame artifact that turns a future customer outcome, FAQ objections, risks, and validation questions into a durable product argument before requirements harden. |
| [Working Backwards PR-FAQ template guidance](/research/working-backwards-prfaq-template/) | HELIX keeps PR-FAQ authoring customer-backward, plain-language, reviewable, and tied to downstream artifacts rather than treating it as launch copy. |
| [Product Vision Board](/research/product-vision-board/) | HELIX uses target group, needs, product direction, and business goals to keep Product Vision focused before PRD work begins. |
| [Geoffrey Moore positioning](/research/geoffrey-moore-positioning/) | HELIX uses the positioning sentence to force concrete target customer, need, category, benefit, alternative, and differentiator language. |
| [Atlassian Vision Creation](/research/atlassian-vision-creation/) | HELIX uses vision as a shared future-state picture that aligns stakeholders before strategy and execution. |
| [Twelve-Factor App](/research/12-factor-app/) and [methodology notes](/research/twelve-factor-app-methodology/) | HELIX's runtime-neutral boundary follows the same portability instinct: config, execution, and deployment concerns should be explicit rather than hidden in one environment. |
| [DevSecOps best practices](/research/devsecops-best-practices-2025/) | Security and quality belong throughout the lifecycle, not as late gates. HELIX models them as cross-cutting concerns and first-class artifacts. |
| [SAFe 6.0 enterprise patterns](/research/safe-framework-2025/) | HELIX keeps alignment, built-in quality, transparency, and objective evaluation, while staying smaller and repository-native rather than enterprise-process-heavy. |
| [Team Topologies and platform engineering](/research/team-topologies-platform-engineering-2025/) | HELIX reduces cognitive load by separating methodology from platform runtime and by giving agents a self-service artifact graph. |
| [HELIX 2025 evaluation](/research/helix-evaluation-2025/) | The evaluation identified strengths to preserve, including test-first discipline, phase gates, human-AI responsibility boundaries, documentation templates, and iterative learning. It also drove the current collapse toward a smaller methodology-plus-skill surface. |

## Research-derived HELIX artifacts

Research is valuable only when it changes the artifact stack. HELIX therefore
publishes research-derived artifacts alongside its governing artifacts, so the
reasoning chain is inspectable.

{{< cards >}}
  {{< card link="/artifacts/research-principles-injection-2026-04-05/" title="Principles Injection Study" subtitle="Measured how prompt context changes agent alignment, auditability, and token cost." icon="chart-bar" >}}
  {{< card link="/artifacts/prompt-iteration-protocol/" title="Prompt Iteration Protocol" subtitle="Defines how HELIX evaluates prompt changes and records evidence during iteration." icon="refresh" >}}
  {{< card link="/artifacts/metrics-dashboard/" title="Metrics Dashboard" subtitle="Shows how iteration evidence is made visible after release work." icon="presentation-chart-line" >}}
{{< /cards >}}

The principles-injection study is the clearest example. It compared baseline,
full-document, and selective principle injection and found that full-context
injection made project values explicit in agent reasoning. That finding supports
HELIX's bias toward visible authority, explicit principles, and auditable
alignment plans.

## How to use this section

Read the [thesis](/why/the-thesis/) first if you want the product argument.
Use this page when you want to inspect the support behind that argument. Then
move into the [artifact-type catalog](/artifact-types/) to see how research
becomes reusable document shapes, or into [HELIX's own artifacts](/artifacts/)
to see the method applied to itself.
