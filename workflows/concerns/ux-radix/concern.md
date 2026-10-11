# Concern: UX Interaction Patterns (Radix)

## Category
quality-attribute

## Areas
ui, frontend

## Boundary

This concern owns the Radix/shadcn implementation choice per ADR-011. It
composes ux-interaction-patterns for framework-neutral behavior; the resolver
and context-digest loader include that baseline for existing ux-radix selections.
No selection migration or new exclusive slot is required.

## Components

- Radix accessible primitives, wrapped by copied shadcn/ui components
- WAI-ARIA patterns appropriate to the actual widget
- **Boundary**: `ux-radix` owns the widgets; `a11y-wcag-aa` owns the accessibility checks.

## Constraints

- Copy shadcn components into components/ui/ and theme them with project tokens;
  shadcn is not installed as an npm dependency. Keep Radix semantics intact.
- Ordinary nav uses semantic nav/links; NavigationMenu is optional when its
  interaction fits. Plain text filtering is not automatically a combobox.
- Dialog/AlertDialog implement modal decisions. Popover may be non-modal;
  focus trapping follows modality, not an unconditional overlay rule.
- Match tabs, selects, menus, tooltips and disclosure to their actual patterns.
  Tooltips contain no interactive content; use a popover for interactive detail.
- packaged-design-system and databricks-appkit-ui have competing component ownership;
  resolve any composition in project overrides with governing ADR before build.

## When to use

A project choosing Radix/shadcn as its UI implementation. For another component
library select ux-interaction-patterns and its library concern instead. Existing
ux-radix selections retain the neutral baseline automatically.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- DESIGN_SYSTEM: component mappings and app conventions per ux-interaction-patterns
- TEST_PLAN: baseline UX Coverage plus applicable Radix keyboard/focus tests

## ADR References

Selecting this concern needs no ADR; `concerns.md` records it. Write an ADR only
when the project deviates from the Radix/shadcn prescription. Neutral interaction
behavior composes separately.
