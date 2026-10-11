---
ddx:
  id: example.design-system.packaged
  authoring:
    home: repo
---
# DESIGN.md — Records

Illustrative consumer of a fictional npm design system. The package, tokens
and component names below demonstrate a project-owned contract; they are not
real installation instructions or universal APIs. Uses ux-interaction-patterns
and packaged-design-system; no Radix adapter is selected.

## Navigation and Active State

Native links in a labeled nav lead to Records and Settings. Current page uses
aria-current="page" with a bolder label and border bound to that attribute on
app-owned links. Ordinary links do not require menu arrow-key behavior.

## Visual Hierarchy

Page heading, primary action, then records table; metadata uses subdued text.
The illustrative package defines --ds-space-section for section spacing.
Component metrics follow the selected theme through documented customization.

## Interaction States

- Actions show keyboard focus and progress while pending; the app prevents
  duplicate saves and shows success/failure feedback.
- Fields have labels and actionable errors; failed save preserves input.
- Records show loading, empty/create and error/retry states.
- No modal or destructive operation exists in this slice. Adding one requires
  a documented component mapping and focus/recovery convention.

## Tokens

**Source**: fictional npm package design-kit 1.0.0, pinned in the example's
lockfile; actual projects record their own installed package/version.
**Theme**: default; **Appearances**: light only, as supported in this example.
**Color**: --ds-color-text, a documented semantic text role in the example contract.
**Spacing**: --ds-space-section, its documented section gap role.
**Type**: documented body/heading typography roles from the package.
**Component mappings**: actions → package Button; input → package Field;
records → package Table; feedback → package Notice. Verify real exports and
props in the adopting package's installed-version documentation. Missing
components are recorded gaps with reviewed alternatives.

## Non-Goals

Runtime architecture/data flow belong in Architecture; component wiring in
TDs; significant deviations in ADRs. The package owns presentation values;
this app owns its UX conventions and layout. This example claims no actual
consumer test run or package audit.
