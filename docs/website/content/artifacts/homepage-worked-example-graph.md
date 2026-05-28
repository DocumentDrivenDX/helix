---
title: "Homepage Worked Example Graph"
slug: homepage-worked-example-graph
weight: 300
activity: "Design"
source: "02-design/homepage-worked-example-graph.md"
generated: true
---
# Homepage Worked Example Graph

## Purpose

The homepage worked-example graph shows HELIX applied to itself. It is the
first concrete proof point after the hero: the methodology is not only
described, it is represented through HELIX's own governing artifacts.

The graph should make three ideas visible without requiring a long explanatory
paragraph:

- HELIX artifacts have an authority order from intent to execution.
- Human judgment and agent review are both part of artifact iteration.
- The reusable catalog and the worked example are related but not the same
  thing.

## Status

Accepted bones as of 2026-05-12.

The current visual is good enough to preserve as the baseline. It still has room
for refinement, but future work should improve the same graph concept rather
than replacing it with generic cards or a table.

## Current homepage placement

The graph appears immediately after the "How it works" cards, under:

```markdown
<div class="helix-section-kicker">Live artifact spine</div>

## HELIX's own artifacts, wired together
```

The explanatory paragraph above the graph was removed because the graph itself
should carry the explanation. If the section needs supporting copy later, keep it
to one short sentence and avoid repeating the node labels.

## Relationship to "How it works"

The homepage steps immediately above this graph are:

1. **Write the brief**
2. **Check alignment**
3. **Create the work plan**
4. **Run it in the factory**

The graph should make the middle of that workflow concrete. It shows the
artifact chain that alignment checks and the document spine that work plans are
derived from. It should not replace the four-step explanation; it should prove
that the steps are backed by real HELIX artifacts.

## Visual contract

The graph is a worked example, not the artifact-type catalog.

It should:

- Use the HELIX double-helix visual as the central organizing spine.
- Arrange artifact nodes around the helix in a readable authority sequence.
- Distinguish human judgment from AI execution with strand labels.
- Show the artifact catalog as the enclosing context, not as another peer node.
- Treat alignment review as an iteration mechanism, not as a primary artifact in
  the same order as Product Vision, PRD, architecture, or implementation plans.
- Keep nodes compact enough that the graph reads as a relationship visual, not a
  table.

It should not:

- Become a grid of equal cards.
- Present every artifact type as equal weight.
- Collapse the catalog, worked example, and alignment process into one list.
- Depend on DDx-specific language.

## Current graph shell

```html
<div class="helix-authority-graph helix-annotated-graph" aria-label="HELIX governing artifact relationship graph">
  <div class="helix-catalog-label">
    <span>Artifact catalog</span>
    <strong>Reusable document types in authority order</strong>
  </div>
  <div class="helix-strand-label helix-human-label">
    <strong>Human judgment</strong>
    <span>Manual edits + prompts</span>
  </div>
  <div class="helix-strand-label helix-ai-label">
    <strong>AI execution</strong>
    <span>Alignment reviews + updates</span>
  </div>
  <div class="helix-graph-visual" aria-hidden="true">
    {{< helix-hero >}}
  </div>
  <!-- Artifact nodes follow the authority sequence below. -->
  <div class="helix-collaboration-note">
    Humans provide judgement and quality, steering with edits and prompts.
    Agents review, propose updates to keep the artifact stack coherent,
    create implementation plans and execute them.
  </div>
</div>
```

## Current authority sequence

The current homepage graph uses these nodes:

| Order | Node | Role | Current destination |
| --- | --- | --- | --- |
| 01 | Product Vision | Intent | `artifacts/product-vision` |
| 02 | PRD | Requirements | `artifacts/prd` |
| 03 | Feature Specs | Scope | `artifact-types/feature-specification` |
| Constraint | Principles | Judgment constraint | `artifacts/principles` |
| 04 | Architecture | Structure | `artifacts/architecture` |
| 05 | Test Plans | Proof | `artifact-types/test-plan` |
| 06 | Implementation Plans | Execution handoff | `artifacts/implementation-plan` |

Principles are intentionally represented as a constraint rather than a numbered
linear step. They govern decisions across the sequence.

## Current collaboration note

```text
Humans provide judgement and quality, steering with edits and prompts. Agents
review, propose updates to keep the artifact stack coherent, create
implementation plans and execute them.
```

Keep this idea, but it may be shortened later if the visual labels make it
redundant.

## Improvement room

Future refinement should focus on:

- Tightening node spacing and connector rhythm.
- Making the authority sequence easier to scan at desktop width.
- Improving mobile behavior without flattening the concept into generic cards.
- Clarifying when a node links to a HELIX worked artifact versus an artifact type.
- Possibly moving the collaboration note into a smaller legend treatment.

The baseline to preserve is the relationship model: catalog context, central
double helix, ordered governing artifacts, human/agent iteration roles.

## Required sizing hints

The graph is an absolutely positioned stage. It must keep explicit dimensions so
the central helix and surrounding nodes do not collapse or reflow as ordinary
document content.

Required CSS contract:

```css
.helix-authority-graph {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.helix-annotated-graph {
  height: clamp(43rem, 58vw, 49rem);
  min-height: 43rem;
}

.helix-graph-visual {
  position: absolute;
  display: grid;
  width: 13rem;
  min-width: 13rem;
  height: 22.75rem;
  min-height: 22.75rem;
  place-items: center;
  overflow: visible;
}

.helix-graph-visual svg {
  display: block;
  width: 13rem;
  height: 22.75rem;
  max-width: none;
  overflow: visible;
}
```
