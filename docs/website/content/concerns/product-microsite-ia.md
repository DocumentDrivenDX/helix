---
title: "Product Microsite IA"
slug: product-microsite-ia
generated: true
aliases:
  - /reference/glossary/concerns/product-microsite-ia
---

**Category:** Documentation & Demos · **Areas:** site, docs, frontend

## Description

## Category
microsite

## Areas
site, docs, frontend

## Components

- **Audience model**: evaluators, first-time users, active users, contributors
- **Information architecture**: top-level sections, section landing pages, sidebar hierarchy, page-local outline
- **Conversion path**: first answer, proof, first action, reference lookup
- **Trust path**: claims, examples, source artifacts, operational proof
- **Navigation state**: current section, current page, sibling context, page-local headings
- **Responsive behavior**: desktop sidebar, mobile drawer, page outline, touch targets

## Constraints

- The homepage must answer what the product is before explaining how it works.
- The first viewport must name the product or category, state the core value,
  and expose a clear next action.
- Navigation must reflect user intent, not internal implementation structure.
- Section landing pages must orient the reader before sending them deeper.
- Sidebars must expose the most important leaf pages without forcing readers
  through abstract categories.
- Page-local navigation must be visibly subordinate to section navigation.
- Reference pages must preserve context: the reader should know what section,
  activity, or category they are in after landing on any leaf page.
- Generated reference pages must have deterministic ordering, stable active
  state, and human-readable titles.
- Supporting material may be grouped or disclosed, but core decision-making
  material must be visible without drilldown.
- Custom layout and CSS are allowed only when the site framework cannot express
  the required hierarchy, state, or responsive behavior.

## Content Guidelines

Product microsites need to serve four reader modes:

| Reader mode | User question | Required path |
|-------------|---------------|---------------|
| Evaluate | What is this, and is it worth my time? | Home, Why, proof, examples |
| Start | How do I try it correctly? | Getting Started, recipes, platform notes |
| Decide | What concept or artifact should I use next? | Concepts, artifact types, workflow |
| Operate | How do I look up exact behavior? | Reference, artifacts, commands, concerns |

Top-level IA should usually separate:

- **Why**: problem, thesis, principles, audience
- **Use**: installation, workflows, recipes, platform guidance
- **Types or Concepts**: reusable flow, artifact types, conceptual model
- **Reference**: exact command, API, concern, and generated catalog material
- **Artifacts or Examples**: worked examples and source-of-truth project docs

These names are not mandatory. The distinction is mandatory: do not mix
persuasion, onboarding, flow, and exact reference into one flat tree.

## Artifact and Reference Navigation

Artifact-type catalogs must help a reader answer "what should I create or read
next?" before they answer "what files exist?"

- Order artifact types by the activity where a user needs them.
- Show core artifacts first for each activity.
- Keep supporting artifacts visibly secondary through lighter treatment,
  disclosure, or a divider.
- Avoid global buckets that hide leaf nodes behind labels users do not already
  understand.
- Keep activity pages, core artifact pages, and supporting artifact pages in
  the same navigation model.
- Left navigation represents site hierarchy and current location.
- Right navigation represents headings inside the current page only.
- The two navs must reinforce each other: selecting a left-nav leaf should not
  make the reader lose sibling or parent context.

## Testing

- Screenshot the homepage, each top-level section, and representative deep
  reference pages on desktop and mobile.
- Verify active left-nav state for every generated reference page type.
- Verify page-local right nav has only headings from the current page.
- Verify core reference pages are reachable without expanding supporting-only
  categories.
- Verify supporting pages remain discoverable through their parent activity.
- Verify mobile navigation reaches the same pages as desktop navigation.

## Quality Gates

- A first-time reader can identify the product, audience, value, and first
  action from the homepage without opening another page.
- A user landing on any generated reference page can identify its parent
  section and nearest sibling pages.
- Core reference pages are visible in the primary section navigation.
- Supporting pages are differentiated without becoming undiscoverable.
- Right-nav styling is subordinate to left-nav styling and has no decorative
  treatment that competes with page content.
- Navigation screenshots show no clipped text, overlapping elements, cramped
  controls, or inconsistent active state.

## When to use

Any project with a public-facing product, flow, platform, or developer
tool microsite. This concern is especially important when the site includes
generated reference content, artifact catalogs, demos, or documentation that
serves both evaluators and active users.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: information-architecture model (reader modes, top-level sections, nav state) for the microsite

## ADR References

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements

- Define the primary reader modes before defining the navigation tree.
- State which top-level pages answer evaluation, onboarding, flow,
  reference, and proof questions.
- Identify the pages that must be reachable without opening an abstract
  grouping page.
- Specify the relationship between global navigation, section sidebar, and
  page-local outline.
- Define which content is core and which content is supporting.
- Define how generated pages inherit title, weight, parent, active state, and
  sibling context.

## Design

### Homepage

- Use one clear product/category headline.
- Put the product's durable value in the first supporting sentence.
- Keep the hero action path focused: one primary action and one secondary
  proof or explanation path.
- Make the first viewport expose a hint of the next section so the page does
  not feel like a sealed landing card.

### Section Landing Pages

- Start with the user question the section answers.
- Show the most important child pages as direct links.
- Use grouping only after the reader can see the core choices.
- Do not use generic category labels unless the page explains why they matter.

### Sidebar IA

- A sidebar is a map of where the reader is in the site.
- It must expose current page, parent page, important siblings, and nearby next
  choices.
- It must not be a second table of contents; the right nav already handles
  current-page headings.
- The active page must remain visible on every leaf page.
- Parent sections should remain expanded when a child is active.
- Core leaf pages should be visible by default.
- Supporting leaf pages may sit behind an inline expandable region when there
  are too many to show at once.

### Artifact Catalogs

- Activity order is usually the strongest ordering mechanism because it maps
  to when users need the artifact.
- Core artifacts appear before supporting artifacts inside each activity.
- Supporting artifacts should have lighter visual weight, smaller labels, or a
  divider. They should not be moved into a separate global hierarchy that hides
  them from activity context.
- Artifact pages should show role, activity, upstream/downstream relationships,
  and a concrete example when available.
- Catalog index pages should help the reader choose, not just enumerate.

### Right Navigation

- Right nav is page-local. It lists headings from the current page only.
- It should be visually quiet and should not use decorative gradients,
  oversized controls, or footer treatment that competes with content.
- "Scroll to top" affordances must have normal spacing and must not appear as
  broken nav content.

## Implementation

- Prefer framework-native navigation primitives when they can express the IA.
- Add custom generation only where deterministic page relationships are needed.
- Store navigation role in frontmatter when generation needs it:
  `activity`, `artifactRole`, `weight`, `prev`, `next`, and parent section.
- Keep generated URLs stable across reorganizations unless a redirect is added.
- Generate section index pages and leaf pages from the same source ordering.
- Treat CSS as a presentation layer over an explicit content model, not as the
  source of IA.

## Testing

- Desktop screenshot: homepage, section landing page, core leaf page,
  supporting leaf page.
- Mobile screenshot: same set with nav drawer opened where relevant.
- State assertions: active left-nav item, expanded parent, right-nav headings,
  absence of duplicate current-page nav.
- Link assertions: core pages reachable from landing page and sidebar;
  supporting pages reachable from parent activity.
- Visual assertions: no clipped nav labels, no overlapping scroll controls,
  no decorative nav treatment that looks like content.

## Quality Gates

- Site IA has a named reader mode for every top-level section.
- The primary sidebar and page-local outline have distinct jobs.
- Core pages are visible without unrelated drilldown.
- Supporting pages are secondary but discoverable.
- Generated reference pages preserve context and active state.
- Screenshot review passes on desktop and mobile before release.
