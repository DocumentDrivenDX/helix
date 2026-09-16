---
title: "Feature Specification: FEAT-018 — Deliverables"
slug: FEAT-018-deliverables
weight: 160
activity: "Frame"
source: "01-frame/features/FEAT-018-deliverables.md"
generated: true
collection: features
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `01-frame/features/FEAT-018-deliverables.md`):

```yaml
ddx:
  id: FEAT-018
  authoring:
    home: repo
  depends_on:
    - helix.prd
  status: draft
```

# Feature Specification: FEAT-018 — Deliverables

**Feature ID**: FEAT-018
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers
**Covered PRD Subsystem(s)**: Routing skill (present mode)
**Covered PRD Requirements**: R-12
**Cross-Subsystem Rationale**: None (single subsystem).

## Overview

PRD R-12 requires that governed artifacts come back out as documents people
outside the project read: a deck, a one-pager, or a brief. FEAT-018 is the
`present` mode (`workflows/modes/present.md`), the `deliverable` artifact
type (`workflows/activities/06-iterate/artifacts/deliverable/`), the
reference data under `workflows/deliverables/`, and the gate scripts beside
the skill (`skills/helix/scripts/check-deliverable.py`,
`corpus-inventory.py`, `render-deck.js`, `deck-qa.py`).

## Ideal Future State

A sponsor, client, or executive receives a deck built from the project's
own vision, PRD, and designs and can decide from it without a HELIX
glossary. Every title is a claim; the titles read in order form the
argument and end in the ask; every number traces to a governing section;
nothing on a slide contradicts the documents behind it. The Markdown script
is the document of record and is reviewed like any artifact; the rendered
files are evidence that the script survives a projector. A host with only
read, write, and search produces the script; a host with the render
toolchain also produces the `.pptx` and PDF and looks at every slide.

## Problem Statement

- **Current situation**: before this feature, HELIX had no output for
  readers outside the project. Governed artifacts were written in the
  `artifact-signal` voice (compressed, HELIX vocabulary, IDs in the body),
  and the only way to brief a sponsor was to rewrite them by hand.
- **Pain points**: hand-written decks drifted from the documents within a
  revision; numbers on slides had no source; titles were labels ("Results",
  "Architecture") rather than claims; and no check caught any of it.
- **Desired outcome**: one mode turns governed artifacts into a deliverable
  that passes a deterministic gate, on every host, with rendering as an
  optional extra.

## Functional Areas

| Area | User question or job | Feature responsibility |
|------|----------------------|------------------------|
| Intake and inventory | Who is this for, what should they decide, and what does the corpus hold? | Resolve audience, occasion, decision, budget, kind, and constraints; declare scope and breadth; inventory the scope before choosing content |
| Storyboard and script | What is the argument, and what proves each claim? | Takeaway, ranked messages with evidence, claim titles per beat, pattern per unit, script in the human-facing voice with notes and Sources |
| Gate | Is it done? | Deterministic script checks, title and shape rules, horizontal and vertical logic, fidelity, voice, coverage, flow checklist |
| Render and inspect | Does it survive a projector or a printer? | `.pptx` and PDF from the script, rasterized and inspected slide by slide; HTML, `.docx` for one-pagers and briefs when a host renders them |

## Requirements

### Functional Requirements by Area

#### Intake and inventory

- **INT-01**: The mode must resolve audience, occasion, decision or action
  sought, time slot or page budget, kind (`deck`, `one-pager`, `brief`),
  and constraints before writing; at `low` and `medium` autonomy it asks
  once for what is missing, at `high` it infers and records each inference
  under Assumptions and gaps.
- **INT-02**: A deliverable with no named audience and no decision sought
  must not be authored.
- **INT-03**: The Brief must record scope, breadth (`survey` or
  `deep-dive`), angle, must-cover, must-omit, and the message cap.
- **INT-04**: The mode must inventory the declared scope before choosing
  content, in three passes (recurring concepts weighted by authority,
  the corpus's own structure read from the catalog, and roles and
  hand-offs), plus the headings of the top-ranked documents as an
  authority floor; the result is a concept coverage table in which every
  group is covered by a named message or omitted with a reason.

#### Storyboard and script

- **STO-01**: The flow must be chosen by occasion from the catalog's flow
  definitions, and the takeaway, the ranked messages with their evidence
  sections, and the beat-to-title table must be written before any body.
- **STO-02**: Titles read in order must form the argument and end in the
  ask (horizontal logic) before bodies are written.
- **STO-03**: Each unit must carry one pattern from the beat's allowed
  set, honoring density rules and the time budget; a unit that overflows
  its pattern is two units.
- **STO-04**: The script must use the `deliverable` template and the
  `human-facing` voice: claim titles, bodies inside pattern limits, a
  visual specification per unit, speaker notes, and a Sources appendix
  mapping every figure and claim to a governing artifact section.
- **STO-05**: No HELIX vocabulary may appear in a body; artifact IDs,
  activity names, work-item terms, and acceptance-criterion codes live
  only in Sources and frontmatter.
- **STO-06**: Content no artifact holds must become a question or a
  recorded assumption, never an invented fact.

#### Gate

- **GATE-01**: The script must pass the deterministic gate: every unit
  has a claim title, a pattern, a visual, notes, and sources; no
  placeholder text; no HELIX vocabulary in bodies; word and bullet limits
  per pattern; density rules; every number in a body appears in Sources.
- **GATE-02**: Titles must pass the ported headline rules (contrastive
  reversal, colon list, imperative chain, listicle, stacked negation,
  forced triplet, flattery, aphorism, universal claim, mannered phrase,
  inventory count, hedge, over-length), and no two consecutive titles may
  fail horizontal logic.
- **GATE-03**: Shapes (bullets, card labels, captions, verdicts) must pass
  the ported slide rules, and no slide may carry two shapes that say the
  same thing (restatement).
- **GATE-04**: The gate must read the Brief and the coverage table and
  fail when a concept group is neither covered nor omitted with a reason,
  when a must-cover concept has no message, when a must-omit concept
  appears in a title or body, or when a survey covers fewer than five
  groups.
- **GATE-05**: The ported title and shape rules must stay in sync with
  their upstream fixture; a release check fails when they diverge.
- **GATE-06**: Vertical logic, fidelity, voice, and the flow checklist are
  checked by the model and recorded under Render; a failure loops back to
  the storyboard, the script, or the render, never to "good enough".

#### Render and inspect

- **REN-01**: On a host with the render toolchain, the mode must render
  the script to `.pptx` and export a PDF, record each path in the
  script's export list and under Render, and rasterize every slide for
  inspection; a deck nobody looked at is not finished.
- **REN-02**: On a host without the render toolchain, the mode must stop
  after the script and name a host that can render it; the script alone
  is a valid outcome.
- **REN-03**: The rendered file must open and validate with the host's
  checker, and the geometry check must report zero blocking findings.
- **REN-04**: The look (`editorial`, `technical`, `bold`, `classic`) must
  be chosen by room, recorded in the Brief, and rendered from the same
  script.

### Non-Functional Requirements

- **NFR-1 (portability)**: the mode contract and the deliverable type
  contain zero runtime-specific commands; the release portability check in
  the test suite passes (PRD R-4).
- **NFR-2 (determinism)**: the gate script gives the same findings for the
  same script on every host; the catalog example passes it with zero
  blocking findings, and the broken fixture fails on the named check ids.
- **NFR-3 (budget)**: a deck holds at most twelve content slides without a
  recorded exception; a one-pager holds three to six sections; a brief
  two to four pages.

## User Stories

- [TODO: create story] Sponsor deck from a vision and PRD.
- [TODO: create story] Evaluation deck from the full artifact set.

## Edge Cases and Error Handling

- **Corpus holds no number for a stat beat**: the beat becomes a question
  or a recorded assumption; the mode never invents a figure.
- **Required beat with no source**: recorded under Assumptions and gaps;
  the flow's checklist still runs.
- **Title passes the rules but the body cannot prove it**: the title is
  rewritten to what the body proves, or the unit is cut.
- **Gate finds a defect after render**: the loop returns to the script;
  the render is redone from the corrected script, never patched by hand.
- **Deck reveals a gap in a governing artifact**: route to `evolve` or
  `align` with the gap as evidence, then re-present; the deliverable never
  edits its sources.
- **Client edits the deck live in a shared tool**: the deliverable stays
  `authoring.home: external-tool`; `present` drafts the script they start
  from.

## Success Metrics

- Every committed deliverable script passes the gate with zero blocking
  findings and records its render inspection.
- The present briefs in the eval keep their deterministic checks green
  across runs, and their rubric totals do not fall.
- A reader outside the project can state the argument from the titles
  alone (the horizontal-logic read), checked on each deck review.

## Constraints and Assumptions

- The Markdown script is the document of record; renders are evidence and
  are regenerated from the script, never edited directly.
- Rendering and inspection depend on host tooling (node with a
  presentation library, LibreOffice, a PDF rasterizer, an SVG rasterizer);
  the install guide lists them as optional.
- The headline and slide rules are a port of Sloptimizer's; the port is
  kept in sync by a test, not by hand.
- The catalog ships its own theme; a project with a `design-system`
  artifact overrides it.

## Dependencies

- **Other features**: FEAT-017 (iteration documentation: the human-cadence
  artifacts a status deck projects); FEAT-016 (artifact honesty: sourced
  claims).
- **External services**: none required. Optional host tooling for
  rendering and inspection, named in `docs/install/README.md`.
- **PRD requirements**: R-12 (human-facing outputs), R-4 (runtime-neutral
  content), R-1 (the `deliverable` type joins the catalog).

## Out of Scope

- A document flow, section patterns, renderer, or kind-aware checks for
  one-pagers and briefs; the kinds are named and share the template, but
  today only decks have a flow, patterns, a renderer, and a gate tuned to
  them (tracked in the improvement backlog).
- A self-contained HTML render target; the mode names it, no renderer
  produces it.
- Marketing copy with no governing artifact behind it; frame first.
- A design system; HELIX ships a theme, not brand governance.
- Live editing of the rendered file; changes go through the script.

## Review Checklist

- [x] Covered PRD Subsystem(s) and Requirements are listed; single subsystem
- [x] Functional areas are subordinate stages of one capability
- [x] Overview connects this feature to PRD R-12
- [x] Ideal future state describes the reader's outcome
- [x] Problem statement describes what existed and what was broken
- [x] Requirements are grouped by functional area
- [x] Every functional requirement is testable
- [x] Acceptance criteria are left to user stories (ADR-009)
- [x] Non-functional requirements carry numeric or binary targets
- [x] Edge cases cover realistic failure scenarios
- [x] Success metrics are feature-specific
- [x] Dependencies reference real artifact IDs
- [x] Out of scope excludes plausible assumptions
- [x] No exact CLI or schema surface is defined inline
- [x] Consistent with PRD R-4 and R-12
