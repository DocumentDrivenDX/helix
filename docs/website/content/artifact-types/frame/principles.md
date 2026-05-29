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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/principles.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Principles Generation Prompt&#10;&#10;Help the user create a project principles document that guides judgment calls&#10;across all HELIX activities.&#10;&#10;## Purpose&#10;&#10;Project Principles define the project&#x27;s durable judgment model. Their unique&#10;job is to help agents and humans choose between two plausible options when the&#10;Product Vision, PRD, feature specs, concerns, ADRs, tests, and implementation&#10;plans do not prescribe an exact answer.&#10;&#10;They are not a second requirements document. They are not a concern catalog.&#10;They are not ADRs. They are not workflow rules. A good principle changes a&#10;real decision without pretending to settle every future case.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/agile-manifesto-principles.md` frames principles as durable&#10;  tradeoff preferences that guide many decisions without becoming procedure.&#10;- `docs/resources/govuk-design-principles.md` models compact, memorable,&#10;  decision-changing principles that stay distinct from a rulebook.&#10;&#10;## Bootstrap Flow&#10;&#10;1. **Check for existing principles**: If `docs/helix/01-frame/principles.md`&#10;   already exists, load it and offer to refine rather than replace.&#10;&#10;2. **Load HELIX defaults**: Read `workflows/principles.md` for the baseline&#10;   design principles. Present them to the user as the starting point.&#10;&#10;3. **Discovery conversation**: Ask the user three questions to surface&#10;   project-specific values:&#10;   - &quot;What does your project value most?&quot;&#10;   - &quot;What trade-offs do you consistently lean toward?&quot;&#10;   - &quot;What past mistakes should these principles help you avoid?&quot;&#10;&#10;4. **Synthesize**: Combine the user&#x27;s input with the HELIX defaults to&#10;   produce a project principles document. The user may keep, modify, or&#10;   remove any HELIX default. Removed defaults stay removed — HELIX does&#10;   not re-add them.&#10;&#10;5. **Tension detection**: For each pair of principles in the result, evaluate&#10;   whether they could pull in opposite directions for a realistic decision.&#10;   Flag any unresolved tensions and ask the user for a resolution strategy.&#10;&#10;6. **Write the file**: Output to `docs/helix/01-frame/principles.md` using&#10;   the template from `template.md`. The user owns the file from this point.&#10;&#10;## Principles Quality Criteria&#10;&#10;Each principle must be:&#10;&#10;- **Decision-changing**: It must change at least one real choice. If removing&#10;  the principle would not change any decision, it is not a principle.&#10;- **Actionable**: An agent or developer reading it should know which option&#10;  to prefer in a concrete scenario.&#10;- **Tradeoff-shaped**: It should say what to prefer when two valid options&#10;  compete. &quot;Always do X&quot; is usually a rule, not a principle.&#10;- **Concise**: One sentence for the principle, one sentence for the&#10;  rationale. If it needs a paragraph, it may be a policy, not a principle.&#10;&#10;Reject or flag:&#10;&#10;- Workflow rules (belong in enforcers or ratchets, not principles)&#10;- Aspirational statements that do not change decisions&#10;- Principles so broad they apply to every project (&quot;write good code&quot;)&#10;- Requirements that define product behavior (belong in PRD or feature specs)&#10;- Technology or quality domains (belong in Concerns)&#10;- Specific decisions already made (belong in ADRs)&#10;&#10;## Boundary Test&#10;&#10;For every candidate principle, ask:&#10;&#10;| Question | If yes |&#10;|---|---|&#10;| Does it define what the product must do? | Move it to the PRD or a feature spec. |&#10;| Does it name an active quality area, technology stack, or operating concern? | Move it to Concerns. |&#10;| Does it record a specific decision and alternatives? | Move it to an ADR. |&#10;| Does it require a mandatory process step? | Move it to workflow rules, enforcers, or ratchets. |&#10;| Does it only sound virtuous? | Delete it or rewrite it around a real tradeoff. |&#10;&#10;## Size Thresholds&#10;&#10;Monitor the number of principles and provide guidance:&#10;&#10;- **At 8 principles**: &quot;Consider whether all of these are decision-changing.&#10;  Can any be consolidated?&quot;&#10;- **At 12 principles**: &quot;The Agile Manifesto has 12 and most teams can name&#10;  maybe 4-5. Consider consolidating.&quot;&#10;- **At 15+ principles**: &quot;This has grown beyond a decision framework into a&#10;  wish list. Strongly recommend pruning to the principles that actually&#10;  change decisions.&quot;&#10;&#10;## Tension Detection&#10;&#10;When evaluating a set of principles for tensions:&#10;&#10;1. Parse each principle into a short semantic summary.&#10;2. For each pair, ask: &quot;Is there a realistic decision where these two&#10;   principles pull in opposite directions?&quot;&#10;3. For each detected tension, check whether the tension resolution section&#10;   already addresses it.&#10;4. Flag unresolved tensions with a concrete example scenario.&#10;5. Accept the user&#x27;s resolution strategy and add it to the tension&#10;   resolution section of the document.&#10;&#10;## Completion Criteria&#10;&#10;- The principles document contains only decision-changing principles.&#10;- No workflow rules are included (those belong in enforcers/ratchets).&#10;- All identified tensions have resolution strategies.&#10;- The document is within the size ceiling (ideally 5-8 principles).&#10;- The user has reviewed and approved the final set.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: principles&#10;---&#10;&#10;# Project Principles&#10;&#10;These principles guide judgment calls across all HELIX activities. They are not&#10;requirements, concerns, ADRs, workflow rules, or process enforcement. They are&#10;lenses applied when choosing between two valid options.&#10;&#10;This document was bootstrapped from HELIX defaults. You own it now — add,&#10;modify, reorder, or remove any principle. The only constraint: principles&#10;cannot negate HELIX mechanics (artifact hierarchy, activity gates, tracker&#10;semantics).&#10;&#10;## Principles&#10;&#10;1. **Design for change** — Prefer structures that are easy to modify over&#10;   structures that are easy to describe today. This changes decisions when a&#10;   tidy short-term model would make likely product changes expensive.&#10;&#10;2. **Design for simplicity** — Start with the minimal viable approach.&#10;   Additional complexity requires justification. This changes decisions when a&#10;   generalized solution has no current requirement behind it.&#10;&#10;3. **Validate your work** — Every change should be verified through the most&#10;   appropriate means available (tests, type checks, manual verification). This&#10;   changes decisions when speed and evidence pull against each other.&#10;&#10;4. **Make intent explicit** — Code, configuration, and documentation should&#10;   make the *why* visible, not just the *what*. This changes decisions when an&#10;   implicit convention would save words but hide rationale.&#10;&#10;5. **Prefer reversible decisions** — When uncertain, choose the option that&#10;   is easiest to undo or change later. This changes decisions when confidence&#10;   is low and both options satisfy current requirements.&#10;&#10;6. **Spec is the contract** — The governing artifact stack is the source of&#10;   truth; code is a projection of it. Compare and reproduce from the spec, and&#10;   keep traceability bidirectional (no material code surface without a governing&#10;   artifact; no acceptance criterion without an exercising test). This changes&#10;   decisions when code and spec diverge — fix the projection or update the&#10;   contract in the same change, rather than letting them drift.&#10;&#10;## Tension Resolution&#10;&#10;When principles pull in opposite directions, document the resolution strategy&#10;here. Each entry should name the two principles, describe when they conflict,&#10;and state how to decide.&#10;&#10;*No tensions identified yet. As you add project-specific principles, use this&#10;section to resolve any conflicts with existing principles.*</code></pre></details></td></tr>
</tbody>
</table>
