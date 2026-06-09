---
title: "Technical Design: TD-012 — Artifact Types Navigation"
slug: TD-012-artifact-types-navigation
weight: 810
activity: "Design"
source: "02-design/technical-designs/TD-012-artifact-types-navigation.md"
generated: true
collection: technical-designs
---

> **Source identity** (from `02-design/technical-designs/TD-012-artifact-types-navigation.md`):

```yaml
ddx:
  id: TD-012
  depends_on:
    - FEAT-012
    - FEAT-007
  review:
    self_hash: 495d26c473dd0f5ee6f11796f66f7c7ebb6d658b51ad7f6e725a5d037a57db47
    deps:
      FEAT-007: d7f507487425873506f2953e58566d946b06d2614a523ebeb9e1e0f68ff71231
      FEAT-012: fe5c93bc84074e71865b451779c665633aa980ae337dd9fce614fcfdb88d666d
    reviewed_at: "2026-05-15T04:11:24Z"
```

# Technical Design: TD-012 — Artifact Types Navigation

**Feature**: [[FEAT-012]]

## Scope

This design covers the generated Artifact Types section of the HELIX microsite:
routes, ordering, sidebar state, core/supporting artifact treatment, page-local
outline behavior, CSS boundaries, and tests. It does not redesign the whole
theme or change the artifact-type source model beyond metadata needed for
navigation.

## Acceptance Criteria

1. **Given** a user opens Artifact Types, **When** the page loads, **Then** the
   primary view is activity-first and core artifacts are visible within each
   activity.
2. **Given** a user opens a core artifact page, **When** the sidebar renders,
   **Then** the parent activity remains open and the active artifact is visible.
3. **Given** a user opens a supporting artifact page, **When** the sidebar
   renders, **Then** the page remains in its activity context and supporting
   artifacts are visually secondary to core artifacts.
4. **Given** a user reads any Artifact Type page, **When** they inspect the
   right navigation, **Then** it contains headings from the current page only
   and uses quiet styling.
5. **Given** the site is checked on mobile and desktop, **When** screenshots
   are reviewed, **Then** nav labels, scroll controls, and disclosure affordances
   do not overlap or appear broken.

## Technical Approach

**Strategy**: Generate an activity-first content tree from `workflows/activities/`.
Each activity gets a section page. Each artifact page lives under its activity
route and carries role metadata. Core artifacts render as visible first-level
activity children. Supporting artifacts stay under the same activity with
lighter treatment or inline disclosure.

**Key Decisions**:

- **Activity is the primary hierarchy**: Users choose artifacts by when they
  need them in the HELIX loop. A separate global "core" hierarchy makes deep
  pages lose activity context.
- **Role is metadata, not route hierarchy**: `artifactRole: core|supporting`
  controls visual treatment. It must not move supporting pages out of their
  activity.
- **Left nav and right nav have separate jobs**: Left nav is site hierarchy and
  location. Right nav is current-page headings. Styling must make that
  relationship obvious.
- **Generated content owns ordering**: Ordering comes from the activity and
  core/supporting lists in the generator, not from hand-edited sidebar files.
- **CSS follows the content model**: Custom CSS may differentiate supporting
  artifacts, but it cannot create hidden IA by itself.

**Trade-offs**:

- Activity-first URLs are clearer for users, but they change some existing
  Artifact Types URLs. Existing root-level pages should either remain as
  compatibility aliases or be replaced only when the project accepts the break.
- Inline supporting sections reduce sidebar noise, but require screenshot and
  keyboard checks so disclosure does not hide important pages on mobile.

## Component Changes

### Modified: `scripts/generate-reference.py`

- **Current State**: Generates Artifact Types pages from workflow artifact
  metadata. Recent IA changes mixed global categories with activity pages.
- **Changes**:
  - Emit `/artifact-types/<activity>/` section pages for all HELIX activities.
  - Emit artifact pages under `/artifact-types/<activity>/<artifact>/`.
  - Add frontmatter: `activity`, `activitySlug`, `artifactRole`, `weight`,
    `prev`, and `next` where Hextra can consume them.
  - Generate activity index content with core artifacts first and supporting
    artifacts second.
  - Remove global core/supporting category pages unless retained only as
    explicit compatibility pages.

### Modified: `website/content/artifact-types/`

- **Current State**: Generated pages exist, but the hierarchy and active state
  can diverge from the user's activity context.
- **Changes**:
  - Root `_index.md` introduces the activity-first model.
  - Activity `_index.md` files explain when that activity is used.
  - Artifact pages render role, purpose, template, examples, and relationships.

### Modified: `website/assets/css/custom.css`

- **Current State**: Contains site-level overrides, including nav styling.
- **Changes**:
  - Add minimal classes for supporting artifact treatment if Hextra frontmatter
    and content ordering are not enough.
  - Keep right-nav styling quiet: no gradient treatment, no cramped scroll
    control, no decorative footer appearance.
  - Avoid CSS-only hiding that changes information architecture.

### Modified: `website/e2e/microsite.spec.ts`

- **Current State**: Playwright coverage exists for page loads and navigation,
  but it does not fully assert Artifact Types active/open state.
- **Changes**:
  - Add checks for Artifact Types overview, one activity page, one core artifact
    page, and one supporting artifact page.
  - Assert active left-nav item and expanded activity context.
  - Assert right-nav headings come from the current page.
  - Capture desktop and mobile screenshots for these representative pages.

## API/Interface Design

No runtime API changes.

Generated frontmatter interface:

```yaml
title: "PRD"
weight: 120
generated: true
activity: "Frame"
activitySlug: "frame"
artifactRole: "core"
source: "workflows/activities/01-frame/artifacts/prd"
prev: "/artifact-types/frame/feature-specification/"
next: "/artifact-types/frame/principles/"
```

Generated route interface:

```text
/artifact-types/
/artifact-types/discover/
/artifact-types/discover/product-vision/
/artifact-types/discover/business-case/
/artifact-types/frame/
/artifact-types/frame/prd/
```

## Data Model Changes

No persisted data model changes.

Generator in-memory artifact record gains:

```yaml
phase_key: "01-frame"
activity_slug: "frame"
activity_label: "Frame"
artifact_slug: "prd"
artifact_title: "PRD"
artifact_role: "core"
weight: 120
```

## Integration Points

| From | To | Method | Data |
|------|----|--------|------|
| `workflows/activities/*/artifacts/*` | `scripts/generate-reference.py` | filesystem read | metadata, prompt, template, example |
| `scripts/generate-reference.py` | `website/content/artifact-types/` | generated markdown | frontmatter and page body |
| Hextra | generated content | Hugo render | sidebar, breadcrumbs, right nav |
| Playwright | local Hugo server | browser tests | screenshots and nav assertions |

### External Dependencies

- **Hugo + Hextra**: Provides static rendering, sidebar, right nav, responsive
  shell. Fallback: small custom layout or shortcode for the Artifact Types
  section if Hextra cannot express the active/open state.
- **Playwright**: Provides browser-state proof. Fallback: Hugo build plus manual
  screenshots is not sufficient for final acceptance.

## Security

- **Authentication**: None; public static site.
- **Authorization**: None; generated content is public documentation.
- **Data Protection**: Do not publish private project data in generated
  examples. Existing public-example alignment rules still apply.
- **Threats**: Broken links, stale generated content, or misleading examples can
  cause users to follow wrong methodology guidance. Mitigation is deterministic
  generation plus browser tests.

## Performance

- **Expected Load**: Static pages only.
- **Response Target**: Preserve current static-site behavior. Artifact Types
  pages should require no custom client-side JavaScript.
- **Optimizations**: Use build-time generation and Hextra native navigation
  where possible.

## Testing

- [ ] **Generation**: `python3 scripts/generate-reference.py` creates activity
  pages and artifact pages with role metadata.
- [ ] **Build**: `cd website && hugo --gc --minify` succeeds without warnings.
- [ ] **Browser**: Playwright verifies desktop and mobile nav state for overview,
  activity, core artifact, and supporting artifact pages.
- [ ] **Accessibility**: Keyboard can reach supporting disclosure controls and
  generated links.
- [ ] **Visual**: Screenshot review confirms no broken right-nav gradient,
  cramped scroll-to-top control, clipped labels, or active-state loss.

## Migration & Rollback

- **Backward Compatibility**: Prefer compatibility aliases for existing
  `/artifact-types/<artifact>/` URLs until the site can tolerate breaking old
  links.
- **Data Migration**: None.
- **Feature Toggle**: None; generation is deterministic.
- **Rollback**: Revert generator and generated content changes together. Do not
  leave generated pages from a newer hierarchy with an older generator.

## Implementation Sequence

1. Add or repair generator record fields for activity slug, artifact role,
   weight, and route. Files: `scripts/generate-reference.py`. Tests:
   generation diff inspection.
2. Generate activity-first content and remove misleading global category pages.
   Files: `website/content/artifact-types/`. Tests: Hugo build.
3. Add minimal supporting-artifact and right-nav CSS only where needed. Files:
   `website/assets/css/custom.css`. Tests: screenshots.
4. Add Playwright assertions for nav state and representative screenshots.
   Files: `website/e2e/microsite.spec.ts`. Tests: Playwright.
5. Re-run generation, Hugo build, prose check for changed docs, and whitespace
   check.

**Prerequisites**: FEAT-012 and the `product-microsite-ia` concern must be in
place before implementation proceeds.

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Hextra cannot express desired active/open state | M | H | Use a small custom layout for Artifact Types rather than weakening IA |
| URL changes break existing links | M | M | Add compatibility aliases or defer URL break to an explicit migration |
| Supporting artifacts become hidden | M | H | Screenshot and link assertions for representative supporting pages |
| CSS fixes mask a weak content model | M | M | Require role metadata and generated activity pages before styling |
| Generated pages drift from source artifacts | L | H | Keep generator deterministic and run it in validation |

## Review Checklist

- [ ] Activity-first hierarchy is the only primary hierarchy
- [ ] Core artifacts are visible within each activity
- [ ] Supporting artifacts remain in activity context
- [ ] Left navigation and right navigation have distinct responsibilities
- [ ] Generated frontmatter carries enough metadata for state and ordering
- [ ] Tests cover overview, activity, core leaf, supporting leaf, desktop, and mobile
- [ ] Design is consistent with FEAT-012, `hugo-hextra`, and `product-microsite-ia`
