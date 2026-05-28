---
title: "Feature Specification: FEAT-012 — Public Microsite IA"
slug: FEAT-012-public-microsite-ia
weight: 110
activity: "Frame"
source: "01-frame/features/FEAT-012-public-microsite-ia.md"
generated: true
collection: features
---

> **Source identity** (from `01-frame/features/FEAT-012-public-microsite-ia.md`):

```yaml
ddx:
  id: FEAT-012
  depends_on:
    - helix.prd
    - FEAT-006
    - FEAT-007
  review:
    self_hash: fe5c93bc84074e71865b451779c665633aa980ae337dd9fce614fcfdb88d666d
    deps:
      FEAT-006: a44d0a40e5cb883e31c5f6b150a77070fa427bb8f834345908aefaf1cffb38ce
      FEAT-007: d7f507487425873506f2953e58566d946b06d2614a523ebeb9e1e0f68ff71231
      helix.prd: 703d5ebaa378d037fd5ff6cbdf43e015ee014ca6a29b5df0b4c67ba9b117a510
    reviewed_at: "2026-05-15T04:11:24Z"
```

# Feature Specification: FEAT-012 — Public Microsite IA

**Feature ID**: FEAT-012
**Status**: Draft
**Priority**: P1
**Owner**: HELIX maintainers

## Overview

The HELIX microsite is the public product surface for the HELIX methodology.
It should help a reader understand why shared memory matters for agentic work,
adopt the method in a real project, choose the right artifact type at the right
time, and inspect HELIX's own artifacts as proof.

FEAT-007 establishes that the microsite exists. FEAT-012 defines the target
information architecture and functional requirements for the site as a product
experience.

## Ideal Future State

A first-time reader can arrive at any page and quickly answer four questions:

1. **What is HELIX?** A methodology for turning project intent and evidence
   into shared memory that agents can trust.
2. **Why should I care?** Agents do better work with context they can trust,
   and HELIX keeps that context durable as work changes.
3. **What should I do next?** The site offers clear paths for evaluation,
   adoption, artifact selection, exact lookup, and proof.
4. **Where am I?** Navigation always shows the current section, page, parent
   context, and nearby related pages.

The site should feel like a product microsite for a methodology: clear enough
for evaluators, practical enough for users, and precise enough for contributors.
It should not require readers to know the repository layout, Hugo generation
mechanics, or historical HELIX implementation details.

## Functional Areas

| Area | Primary reader question | Site responsibility |
|------|--------------------------|---------------------|
| Home | What is HELIX? | State the product category, value, audience, and first action |
| Why | Why does this method exist? | Explain the problem, thesis, principles, and autonomy model |
| Use | How do I adopt it? | Provide getting-started flows, recipes, platforms, and workflows |
| Artifact Types | What kind of artifact should I create or read? | Explain reusable HELIX artifact types by activity and role |
| Artifacts | What does this look like in a real project? | Publish HELIX's own governing artifacts as proof and examples |
| Concerns | Which cross-cutting practices apply? | Describe reusable concern packages and their practices |
| Reference | What is the exact behavior? | Provide commands, skills, glossary, demos, and generated lookup |
| Navigation | Where am I, and what is nearby? | Keep top nav, sidebar, right nav, breadcrumbs, and search coherent |
| Quality Proof | Can I trust the site? | Build, screenshot, link, and accessibility checks prevent regressions |

## Requirements

### Home

HOME-01. The homepage must state the product category and value in plain
language before introducing internal methodology terms.

HOME-02. The homepage must present the core thesis: agents do better work with
context they can trust, and HELIX creates shared memory that stays current as
the work changes.

HOME-03. The homepage must provide one primary adoption path and one secondary
evaluation or proof path.

HOME-04. The first viewport must include a visual or structural hint that more
substantive content follows below the hero.

### Why

WHY-01. The Why section must explain the product thesis, not repeat setup
instructions or reference material.

WHY-02. The Why section must connect the problem, thesis, principles, context
quality, and AI autonomy slider into one evaluation path.

WHY-03. The autonomy slider must be framed as controlled delegation, not as an
escape hatch for the agent to defer every decision to a human.

WHY-04. Principle pages must connect back to concrete site areas where the
principle becomes operational: Artifact Types, Concerns, Use, Reference, and
Artifacts.

### Use

USE-01. The Use section must help a new user adopt HELIX without first reading
the full artifact catalog.

USE-02. Getting Started must provide the shortest safe path from no HELIX setup
to a first useful workflow.

USE-03. Recipe and platform pages must separate runtime-specific instructions
from methodology concepts.

USE-04. Workflow pages must explain how planning and execution interact without
requiring readers to understand legacy CLI wrappers.

### Artifact Types

TYPE-01. Artifact Types must describe reusable artifact definitions: purpose,
when to create the artifact, template shape, prompt guidance, example, and
relationships to other artifact types.

TYPE-02. Artifact Types must be ordered by HELIX activity because activity
answers when the user needs the artifact.

TYPE-03. Each activity must show core artifacts before supporting artifacts.
Core artifacts must be visible without opening a supporting-only category.

TYPE-04. Supporting artifacts must remain inside their activity context and
must be visually differentiated from core artifacts through lighter treatment,
a divider, or inline disclosure.

TYPE-05. Artifact Type pages must expose role, activity, upstream/downstream
relationships, template, prompt guidance, and example availability in a
consistent structure.

TYPE-06. Artifact Type navigation must keep activity pages, core artifact
pages, and supporting artifact pages in the same hierarchy.

TYPE-07. Generated Artifact Type pages must carry metadata for activity, role,
stable order, source path, and active/open navigation state.

### Artifacts

ART-01. Artifacts must publish HELIX's actual governing documents, not the
generic artifact-type definitions.

ART-02. Artifact pages must preserve source identity so readers can trace the
published page back to the canonical document in `docs/helix/`.

ART-03. Artifact indexes must help readers inspect HELIX as a worked example of
the methodology, grouped by activity and collection where useful.

ART-04. Artifact pages must not be used as the primary way to teach artifact
types; they are proof and examples, not the catalog itself.

ART-05. Public artifacts must exclude or clearly quarantine internal-only,
experimental, stale, or retired material when publishing it would confuse the
product story.

### Concerns

CONCERN-01. Concerns must be presented as reusable cross-cutting practice
packages.

CONCERN-02. Concern pages must explain both the concern definition and the
practices it injects into requirements, design, implementation, and testing.

CONCERN-03. Concern navigation must support lookup by category and by concrete
technology or quality attribute.

CONCERN-04. Project-specific concern activation belongs in Artifacts; reusable
concern definitions belong in Concerns.

### Reference

REF-01. Reference pages must provide exact lookup for commands, skills,
glossary terms, demos, and generated catalogs.

REF-02. Reference content must be terse, complete, and stable. It should not be
the primary persuasion or onboarding path.

REF-03. Runtime and CLI reference pages must clearly distinguish current
surfaces from transitional or legacy compatibility surfaces.

### Navigation and Search

NAV-01. Top navigation must expose the main reader paths: Why, Use, Types,
Artifacts, Concerns, Reference, and platform/runtime material where applicable.

NAV-02. Left navigation must show section hierarchy, current page, parent
context, and nearby sibling pages.

NAV-03. Right navigation must show headings from the current page only and must
be visually subordinate to the left navigation.

NAV-04. Search must help readers recover when they know a term but not the
site's section model.

NAV-05. Deep-linked pages must render enough surrounding context that a reader
does not need to return to the section landing page to understand where they
are.

### Quality Proof

PROOF-01. Generated pages must be deterministic: the same source artifacts must
produce the same routes, titles, weights, and frontmatter.

PROOF-02. Site validation must include Hugo build, link-sensitive checks where
available, prose checks for changed authored docs, and whitespace checks.

PROOF-03. Browser or screenshot checks must cover the homepage, top-level
section pages, Artifact Types overview, one activity page, one core artifact
type page, one supporting artifact type page, one Artifact page, and one
Concern page.

PROOF-04. Desktop and mobile navigation must be checked for active state,
expanded parent context, clipped text, overlapping controls, and broken
scroll-to-top treatment.

### Non-Functional Requirements

- **Performance**: IA changes must preserve static-site performance; no
  client-side routing or heavy JavaScript may be introduced for navigation.
- **Accessibility**: Sidebar hierarchy, disclosure controls, and page-local
  outline must remain keyboard reachable and screen-reader understandable.
- **Maintainability**: Generated pages must derive ordering and role from
  workflow source data, not from hand-maintained duplicate nav lists.
- **Stability**: Existing public URLs should remain stable unless a redirect or
  compatibility page is added.

## User Stories

- US-025: As an evaluator, I want the homepage and Why section to explain
  HELIX's thesis so I can decide whether the methodology applies to my team.
- US-026: As a new user, I want Use pages to get me productive without first
  understanding every artifact type.
- US-027: As an active HELIX user, I want Artifact Types organized by activity
  so I can decide what to create or read next.
- US-028: As a user landing on a deep Artifact Type page, I want the sidebar to
  show where that page sits so I can inspect related artifacts.
- US-029: As a user evaluating HELIX, I want to inspect HELIX's own artifacts
  so I can see whether the methodology produces coherent shared memory.
- US-030: As a contributor, I want generated navigation rules and screenshots
  so site changes do not regress IA or visual state.

## Edge Cases and Error Handling

- **Many supporting artifacts in one activity**: Keep core artifacts visible and
  place supporting artifacts behind a lightweight inline disclosure or divider.
- **Direct deep-link landing**: The active page and parent activity must be
  visible without requiring the reader to backtrack to the section index.
- **Mobile navigation**: The mobile drawer must expose the same activity and
  artifact relationships as desktop.
- **Generated page without example**: Show purpose, template, and relationships;
  do not leave an empty example container.
- **Stale or retired HELIX artifact**: Keep it out of the primary proof path or
  label it clearly enough that readers do not treat it as current direction.
- **Overlapping section intent**: Prefer moving content to its strongest reader
  mode over duplicating the same explanation across Why, Use, Types, and
  Reference.
- **Theme limitation**: If Hextra cannot express required active/open state,
  use a small custom layout or shortcode rather than weakening the IA.

## Success Metrics

- Artifact Types overview shows every activity and all core artifacts in the
  first navigation level below that activity.
- A representative core artifact page and supporting artifact page both show
  active parent activity and sibling context in the left navigation.
- Right navigation contains only current-page headings and has quiet styling.
- Artifact pages and Artifact Type pages are visibly distinct in purpose,
  title, structure, and navigation context.
- The Why, Use, Types, Artifacts, Concerns, and Reference sections each have a
  clear reader job and do not rely on the same generic page-list structure.
- Mobile and desktop screenshots show no clipped sidebar labels, overlapping
  controls, or broken scroll-to-top treatment.
- FEAT-012 requirements are linked from the Artifact Types navigation technical
  design and from follow-on implementation beads.

## Constraints and Assumptions

- HELIX continues to use Hugo and Hextra under the `hugo-hextra` concern.
- Product microsite IA is governed by the reusable `product-microsite-ia`
  concern.
- Artifact Type pages continue to be generated from `workflows/activities/`.
- The Artifact Types section must serve active users first; marketing-style
  explanation belongs in Home and Why.
- The Artifacts section publishes HELIX's own document stack and is allowed to
  be narrower than the full repository if publishing stale or retired artifacts
  would weaken the product story.

## Dependencies

- **Other features**: FEAT-006 Concerns, FEAT-007 Microsite and Demo Reels
- **Cross-cutting concerns**: `hugo-hextra`, `product-microsite-ia`,
  `e2e-playwright`, `a11y-wcag-aa`
- **PRD requirements**: Durable shared memory, optimal context for agent work,
  and operator control over AI autonomy

## Out of Scope

- Replacing Hugo or Hextra
- Full site redesign unrelated to IA and navigation state
- New branding system or logo work
- New interactive product demos
- Runtime changes to HELIX, DDx, or agent skills

## Review Checklist

- [ ] Requirements describe user decisions, not just page lists
- [ ] Functional areas have distinct jobs
- [ ] Artifact requirements and Artifact Type requirements are separate
- [ ] Artifact Types requirements preserve activity context
- [ ] Core and supporting artifact treatment is explicit within Artifact Types
- [ ] Left-nav and right-nav responsibilities are distinct
- [ ] Generated-page metadata requirements are testable
- [ ] Screenshot or browser proof is required before implementation closes
