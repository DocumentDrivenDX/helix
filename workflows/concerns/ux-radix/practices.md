# Practices: UX Interaction Patterns (Radix)

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
