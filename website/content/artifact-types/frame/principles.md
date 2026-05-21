---
title: "Project Principles"
linkTitle: "Project Principles"
slug: principles
activity: "Frame"
artifactRole: "core"
weight: 11
generated: true
---

## Purpose

Project Principles define the project's durable judgment model. Their unique
job is to help agents and humans choose between two plausible options when the
Product Vision, PRD, feature specs, concerns, ADRs, tests, and implementation
plans do not prescribe an exact answer.

They are not a second requirements document. They are not a concern catalog.
They are not ADRs. They are not workflow rules. A good principle changes a
real decision without pretending to settle every future case.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.principles.depositmatch
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
  review:
    self_hash: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
    deps:
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Project Principles

These principles guide DepositMatch decisions when the Product Vision and PRD
do not prescribe an exact answer. They are not product requirements, concerns,
ADRs, workflow rules, or process enforcement.

## Principles

1. **Trust beats automation.** Prefer reviewable suggestions over invisible
   automation when the two conflict. This changes decisions when a faster match
   flow would hide evidence from the reviewer.

2. **Exceptions are first-class work.** Prefer an owned exception over an
   unresolved deposit that sits outside the product. This changes decisions
   when an edge case could be deferred to a spreadsheet or email thread.

3. **Reviewer speed comes from preserved context.** Prefer workflows that keep
   deposits, invoices, evidence, and decisions together over workflows that
   minimize screen count. This changes decisions when a shorter path would make
   the reviewer rebuild context later.

4. **Start with CSV reality.** Prefer robust import and column-mapping behavior
   over early accounting-platform integrations. This changes decisions when
   integration work competes with making pilot firms successful on exported
   data.

5. **Auditability is part of usability.** Prefer visible history and correction
   paths over destructive edits. This changes decisions when a direct edit would
   be simpler but would weaken month-end review.

## Tension Resolution

| When these pull against each other | Resolve by |
|---|---|
| **Trust beats automation** vs. **Reviewer speed comes from preserved context** | Show enough evidence for confident review before optimizing batch speed. Speed that reduces trust will not survive pilot use. |
| **Start with CSV reality** vs. **Reviewer speed comes from preserved context** | Make CSV import dependable first, then improve the review surface with the context those imports provide. |
| **Exceptions are first-class work** vs. **Auditability is part of usability** | Treat exception assignment, status changes, and follow-up notes as auditable decisions, not lightweight comments. |

## Size Guidance

Keep this file focused on choices the team expects to make repeatedly. If a
principle becomes a product behavior, move it into the PRD or a feature spec. If
it becomes a technology decision, move it into Concerns or an ADR.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/principles.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Principles Generation Prompt

Help the user create a project principles document that guides judgment calls
across all HELIX activities.

## Purpose

Project Principles define the project&#x27;s durable judgment model. Their unique
job is to help agents and humans choose between two plausible options when the
Product Vision, PRD, feature specs, concerns, ADRs, tests, and implementation
plans do not prescribe an exact answer.

They are not a second requirements document. They are not a concern catalog.
They are not ADRs. They are not workflow rules. A good principle changes a
real decision without pretending to settle every future case.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/agile-manifesto-principles.md` frames principles as durable
  tradeoff preferences that guide many decisions without becoming procedure.
- `docs/resources/govuk-design-principles.md` models compact, memorable,
  decision-changing principles that stay distinct from a rulebook.

## Bootstrap Flow

1. **Check for existing principles**: If `docs/helix/01-frame/principles.md`
   already exists, load it and offer to refine rather than replace.

2. **Load HELIX defaults**: Read `.ddx/plugins/helix/workflows/principles.md` for the baseline
   design principles. Present them to the user as the starting point.

3. **Discovery conversation**: Ask the user three questions to surface
   project-specific values:
   - &quot;What does your project value most?&quot;
   - &quot;What trade-offs do you consistently lean toward?&quot;
   - &quot;What past mistakes should these principles help you avoid?&quot;

4. **Synthesize**: Combine the user&#x27;s input with the HELIX defaults to
   produce a project principles document. The user may keep, modify, or
   remove any HELIX default. Removed defaults stay removed — HELIX does
   not re-add them.

5. **Tension detection**: For each pair of principles in the result, evaluate
   whether they could pull in opposite directions for a realistic decision.
   Flag any unresolved tensions and ask the user for a resolution strategy.

6. **Write the file**: Output to `docs/helix/01-frame/principles.md` using
   the template from `template.md`. The user owns the file from this point.

## Principles Quality Criteria

Each principle must be:

- **Decision-changing**: It must change at least one real choice. If removing
  the principle would not change any decision, it is not a principle.
- **Actionable**: An agent or developer reading it should know which option
  to prefer in a concrete scenario.
- **Tradeoff-shaped**: It should say what to prefer when two valid options
  compete. &quot;Always do X&quot; is usually a rule, not a principle.
- **Concise**: One sentence for the principle, one sentence for the
  rationale. If it needs a paragraph, it may be a policy, not a principle.

Reject or flag:

- Workflow rules (belong in enforcers or ratchets, not principles)
- Aspirational statements that do not change decisions
- Principles so broad they apply to every project (&quot;write good code&quot;)
- Requirements that define product behavior (belong in PRD or feature specs)
- Technology or quality domains (belong in Concerns)
- Specific decisions already made (belong in ADRs)

## Boundary Test

For every candidate principle, ask:

| Question | If yes |
|---|---|
| Does it define what the product must do? | Move it to the PRD or a feature spec. |
| Does it name an active quality area, technology stack, or operating concern? | Move it to Concerns. |
| Does it record a specific decision and alternatives? | Move it to an ADR. |
| Does it require a mandatory process step? | Move it to workflow rules, enforcers, or ratchets. |
| Does it only sound virtuous? | Delete it or rewrite it around a real tradeoff. |

## Size Thresholds

Monitor the number of principles and provide guidance:

- **At 8 principles**: &quot;Consider whether all of these are decision-changing.
  Can any be consolidated?&quot;
- **At 12 principles**: &quot;The Agile Manifesto has 12 and most teams can name
  maybe 4-5. Consider consolidating.&quot;
- **At 15+ principles**: &quot;This has grown beyond a decision framework into a
  wish list. Strongly recommend pruning to the principles that actually
  change decisions.&quot;

## Tension Detection

When evaluating a set of principles for tensions:

1. Parse each principle into a short semantic summary.
2. For each pair, ask: &quot;Is there a realistic decision where these two
   principles pull in opposite directions?&quot;
3. For each detected tension, check whether the tension resolution section
   already addresses it.
4. Flag unresolved tensions with a concrete example scenario.
5. Accept the user&#x27;s resolution strategy and add it to the tension
   resolution section of the document.

## Completion Criteria

- The principles document contains only decision-changing principles.
- No workflow rules are included (those belong in enforcers/ratchets).
- All identified tensions have resolution strategies.
- The document is within the size ceiling (ideally 5-8 principles).
- The user has reviewed and approved the final set.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: principles
---

# Project Principles

These principles guide judgment calls across all HELIX activities. They are not
requirements, concerns, ADRs, workflow rules, or process enforcement. They are
lenses applied when choosing between two valid options.

This document was bootstrapped from HELIX defaults. You own it now — add,
modify, reorder, or remove any principle. The only constraint: principles
cannot negate HELIX mechanics (artifact hierarchy, activity gates, tracker
semantics).

## Principles

1. **Design for change** — Prefer structures that are easy to modify over
   structures that are easy to describe today. This changes decisions when a
   tidy short-term model would make likely product changes expensive.

2. **Design for simplicity** — Start with the minimal viable approach.
   Additional complexity requires justification. This changes decisions when a
   generalized solution has no current requirement behind it.

3. **Validate your work** — Every change should be verified through the most
   appropriate means available (tests, type checks, manual verification). This
   changes decisions when speed and evidence pull against each other.

4. **Make intent explicit** — Code, configuration, and documentation should
   make the *why* visible, not just the *what*. This changes decisions when an
   implicit convention would save words but hide rationale.

5. **Prefer reversible decisions** — When uncertain, choose the option that
   is easiest to undo or change later. This changes decisions when confidence
   is low and both options satisfy current requirements.

## Tension Resolution

When principles pull in opposite directions, document the resolution strategy
here. Each entry should name the two principles, describe when they conflict,
and state how to decide.

*No tensions identified yet. As you add project-specific principles, use this
section to resolve any conflicts with existing principles.*</code></pre></details></td></tr>
</tbody>
</table>
