---
title: "UX Interaction Patterns (Radix)"
slug: ux-radix
generated: true
aliases:
  - /reference/glossary/concerns/ux-radix
---

**Category:** Quality Attributes · **Areas:** ui, frontend

## Description

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

## Constraints

- Copy shadcn components into components/ui/ and theme them with project tokens;
  shadcn is not installed as an npm dependency. Keep Radix semantics intact.
- Ordinary nav uses semantic nav/links; NavigationMenu is optional when its
  interaction fits. Plain text filtering is not automatically a combobox.
- Dialog/AlertDialog implement modal decisions. Popover may be non-modal;
  focus trapping follows modality, not an unconditional overlay rule.
- Match tabs, selects, menus, tooltips and disclosure to their actual patterns.
  Tooltips contain no interactive content; use a popover for interactive detail.
- ai-design-system and databricks-appkit-ui have competing component ownership;
  resolve any composition in project overrides with governing ADR before build.

## When to use

A project choosing Radix/shadcn as its UI implementation. For another component
library select ux-interaction-patterns and its library concern instead. Existing
ux-radix selections retain the neutral baseline automatically.

## Artifact Impact

- ADR: deviations or conflicts affecting the Radix/shadcn prescription
- DESIGN_SYSTEM: component mappings and app conventions per ux-interaction-patterns
- TEST_PLAN: baseline UX Coverage plus applicable Radix keyboard/focus tests

## ADR References

- ADR-011: ux-radix retains ownership of Radix/shadcn; neutral behavior composes separately

## Practices by activity

Agents working in any of these activities inherit the practices below through runtime work context, such as a DDx bead context digest.

## Requirements

- Apply ux-interaction-patterns and its STP UX Coverage map to affected UI work; existing ux-radix selections load that baseline automatically.
- Use copied shadcn/ui components on Radix; preserve pattern-appropriate keyboard behavior, visible focus and modal focus return.

## Design and Implementation

- ux-radix remains the canonical owner of the Radix/shadcn prescription per
  ADR-011. Framework concerns reference the selected component owner.
- Customize copied components to project tokens without breaking Radix handlers.
- Use Dialog/AlertDialog for modal decisions; Popover defaults can be non-modal.
  Trap focus only for modal behavior; name overlays and restore focus logically.
- Use native anchors/landmarks for ordinary navigation. NavigationMenu is a
  choice, not a requirement for every nav. Use Tabs for same-page panels and
  Select/RadioGroup for matching choices. Combobox applies to selectable search
  suggestions, not every text filter. Tooltips are non-interactive hints.
- Library-specific convenience patterns (command palettes, autosave, range
  selection) require product scope; do not introduce them as baseline obligations.
- Resolve AppKit or SDK component ownership before implementation. No silently
  installed second library or duplicated token system.

## Testing and Quality Gates

- Apply the neutral baseline's actual runtime interaction evidence, including
  visible active nav with aria-current="page" where page navigation exists.
- Verify applicable Radix Escape, keyboard movement and modal focus-return
  behavior; a component import or screenshot alone does not prove behavior.
