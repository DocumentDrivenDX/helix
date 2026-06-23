# Practices: UX Interaction Patterns (Radix)

## Requirements (Frame activity)

- User stories involving interactive UI must specify which interaction
  patterns apply (search, edit, navigate, select, disclose)
- Acceptance criteria must include keyboard-only completion for every
  interactive flow
- Destructive actions must be identified and require confirmation in the spec

## Design

### Search and filtering
- Command palette (`Cmd+K` / `Ctrl+K`) for global search across entities
- Combobox for scoped filtering within a page section (e.g., table column
  filters, entity pickers)
- Search results grouped by category with keyboard section navigation
- Debounced remote search (200-300ms); instant local filtering
- Recent searches and suggested queries in empty state

### Editing
- Inline edit: display → edit → confirm/cancel cycle; Enter saves, Escape
  reverts
- Form edit: full form with sectioned fields, validation on blur + submit,
  sticky save bar for long forms
- Optimistic update for toggles and reordering; pessimistic for deletions
  and financial mutations
- Autosave with status indicator for content authoring (draft / saving /
  saved)

### Navigation
- Persistent sidebar or top nav with Radix NavigationMenu semantics
- Breadcrumb trail for hierarchical depth beyond two levels
- Tabs for same-page content switching (Radix Tabs, not route changes)
- Pagination or infinite scroll for long lists — prefer pagination for data
  tables, infinite scroll for feeds
- Back navigation must preserve scroll position and filter state
- **Current-location feedback (required).** When the user is on a navigable
  destination, the active nav item MUST show a visible active state **and**
  carry `aria-current="page"`. The active visual style should be *derived from*
  that state (or bound to a stable token/class contract) so the cue is both
  semantic and visible — never a style with no semantic anchor. `aria-current`
  is also an accessibility signal; this composes with `a11y-wcag-aa`. "No
  feedback when I click a nav item" is a defect, not a style preference.

### Interaction states (where applicable)

Express interaction states only where the state actually exists for that
element — this is a where-applicable rule, not a demand that every element
carry every state:

- **Enabled interactive controls** (buttons, links, toggles, inputs): hover
  **and** `:focus-visible` styles so keyboard and pointer users both see focus.
- **Disabled controls** (only where disablement is a real condition): a clear
  disabled affordance distinct from enabled, with the disabled state conveyed
  semantically (e.g. `disabled` / `aria-disabled`), not by color alone.
- **Async actions** (save, submit, fetch-triggering controls): a loading state
  that blocks double-submission and signals progress.
- **Data / form / content surfaces**: explicit empty and error states (see
  Implementation → Empty and loading states), never a blank or silent failure.

### Selection
- Checkbox column + header select-all for table multi-select
- Shift+click range selection in lists and tables
- Bulk action toolbar appears contextually when items are selected
- Selection count badge visible at all times during multi-select

### Overlays
- Dialog for blocking decisions (confirmations, forms that need full
  attention)
- Popover for contextual detail (quick view, inline help, settings)
- Tooltip for label augmentation only — never for essential information
- DropdownMenu for action lists — right-click context menus where
  appropriate
- Sheet/drawer for supplementary content that should not replace the page

## Implementation

### Component library (canonical owner)

This concern is the canonical owner of the Radix and shadcn/ui prescription.
Framework concerns (e.g. `react-nextjs`) MUST reference this concern for UI
primitives instead of re-prescribing shadcn or Radix themselves.

- Use **shadcn/ui** as the component library, built on Radix primitives.
- shadcn components are **copied into the project** (e.g. via
  `npx shadcn@latest add <component>`) and customized in `components/ui/` —
  shadcn is NOT installed as an npm dependency.
- Customize copied shadcn components to match the project's design tokens;
  keep the Radix-based accessibility behavior intact (do not override keyboard
  or focus handlers with custom logic that breaks the WAI-ARIA contract).
- For headless behavior not covered by shadcn, use the underlying Radix
  primitive directly.

### Radix component mapping

| Pattern | Radix Primitive | Notes |
|---------|----------------|-------|
| Command palette | Dialog + custom Combobox | cmdk or similar; Dialog wraps the search UI |
| Filterable list | Combobox | WAI-ARIA combobox with listbox |
| Primary nav | NavigationMenu | Arrow-key traversal, roving tabindex |
| Tabs | Tabs | Arrow keys switch, `aria-selected` |
| Single select | Select | Typeahead, arrow keys, portal for overflow |
| Confirmation | AlertDialog | Focus trapped, requires explicit action |
| Quick actions | DropdownMenu | Keyboard nav, submenus, checkable items |
| Contextual info | Popover | Click-triggered, focus trapped |
| Label hint | Tooltip | Hover + focus, non-interactive content only |
| Expandable section | Accordion | Arrow keys between headers |
| Side panel | Dialog (as sheet) | Focus trap, scroll lock, returns focus |

### Keyboard contracts

Every interactive widget must support:

| Key | Behavior |
|-----|----------|
| `Tab` | Move focus to next focusable element |
| `Shift+Tab` | Move focus to previous focusable element |
| `Enter` / `Space` | Activate focused element (button, link, toggle) |
| `Escape` | Close overlay, cancel edit, clear search |
| `Arrow keys` | Navigate within composite widgets (menus, tabs, selects) |
| `Home` / `End` | Jump to first/last item in composite widgets |
| `Typeahead` | Jump to matching item in lists and menus |

### Focus management rules

- Opening an overlay → focus moves to first focusable element inside (or
  Dialog title if no interactive element)
- Closing an overlay → focus returns to the trigger element
- Deleting an item → focus moves to next item (or previous if last)
- Completing inline edit → focus stays on the edited element
- Error on form submit → focus moves to first invalid field
- Toast/notification → do not steal focus; use `aria-live="polite"`

### Empty and loading states

- Skeleton loaders for initial page/section load — match content shape
- Spinner only for actions (save, submit) — not for content loading
- Empty state: icon + message + primary action (e.g., "No invoices yet.
  Create your first invoice.")
- Error state: message + retry action; do not show raw error codes to users

## Testing

- Keyboard-only walkthrough for every interactive flow before PR
- Test Escape key closes every overlay and cancels every inline edit
- Test focus return: open overlay → close → verify focus is back on trigger
- Test typeahead in selects, menus, and comboboxes
- Test empty states render with helpful content, not blank containers
- Test destructive actions require confirmation (click delete → dialog
  appears → must confirm)
- **Mechanized current-location cue.** For a UI web app, the browser e2e MUST
  assert `aria-current="page"` on the active nav item for ≥1 route (navigate →
  assert the active item carries `aria-current="page"`). This is **required,
  non-optional**. An active class/style may be asserted *additionally* but is
  **never a substitute** for the `aria-current` assertion. No pixel/screenshot
  assertions for this gate — assert the semantic state (and, if checked, a
  stable class/token), not a rendered image. This is the same assertion the
  `e2e-playwright` concern requires; it feeds the `verification` gate
  (`workflows/concerns/verification/practices.md`), turning
  "does it show me where I am?" into a checkable test.

## Quality Gates

- No interactive element without keyboard access
- No overlay without focus trap and focus return
- No search without empty-state handling
- No destructive action without confirmation
- No form without visible validation errors on submit
- No navigable destination without a visible active state **and**
  `aria-current="page"` on the active nav item
- No enabled interactive control without hover **and** `:focus-visible` styles
- For a UI web app: the browser e2e asserts `aria-current="page"` on the active
  nav for ≥1 route (required; an active class/style only as an additional
  assertion, never a substitute; no screenshot assertions)
