---
ddx:
  id: example.design-system.sdk
  authoring:
    home: repo
---
# DESIGN.md — SDK Records

An illustrative standalone SDK consumer; this example is a design contract,
not evidence that a consumer audit ran. Uses ux-interaction-patterns and
ai-design-system; no Radix adapter is selected.

## Navigation and Active State

Native links in a labeled nav lead to Records and Settings. Current page uses
aria-current="page" with a bolder label and border derived from that attribute
on app-owned links. No menu arrow-key behavior is imposed.

## Visual Hierarchy

Page heading, primary action, then records table; metadata uses subdued text.
App layout separates sections with var(--piq-space-4). Widget metrics come
from the SDK theme; app code does not restyle SDK classes.

## Interaction States

- Buttons show keyboard focus; save uses SDK Button busy while pending and
  blocks duplicate requests. Success/failure feedback uses Notice or toast.
- Fields have labels and actionable errors; failed save preserves input.
- Records show loading, empty/create and error/retry states.
- No modal or destructive operation exists in this bounded example. A future
  one needs an approved component mapping and focus/recovery convention.

## Tokens

**Source**: @skadden/tokens 1.4.0 and @skadden/ui 0.6.0, illustrative exact pins
from SDK CONTRACT-004; adopting projects record their installed lockfile versions.
**Theme**: databricks; **Appearances**: light and dark. Theme/font CSS precedes ui.css.
**Color**: app text uses var(--piq-color-text); no copied palette values.
**Spacing**: section gaps use var(--piq-space-4).
**Type**: bundled theme fonts and SDK type roles from the installed catalogue.
**Component mappings**: actions → Button; input → TextField; records → DataTable;
feedback → Notice/useToast; loading → Skeleton. Names come from installed
catalogue.json; a missing widget is a reviewed SDK gap, not a second kit.

## Non-Goals

Runtime architecture and data flow belong in Architecture; component props,
state and file layout in TDs; significant deviations in ADRs. The SDK owns
presentation values; this app owns its UX conventions and layout.
