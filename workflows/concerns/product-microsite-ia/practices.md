# Practices: Product Microsite IA

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
