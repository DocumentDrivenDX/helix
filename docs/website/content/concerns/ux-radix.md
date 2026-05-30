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

## Components

- **Primitives**: Radix UI (headless, accessible by default) — this concern is
  the canonical owner of the Radix prescription; other concerns reference here
- **Component library**: shadcn/ui (copied components, not an npm dependency)
  built on top of Radix — this concern is the canonical owner of the shadcn
  prescription; framework concerns (e.g. `react-nextjs`) reference here rather
  than re-prescribing
- **Patterns**: WAI-ARIA design patterns for all interactive widgets
- **Scope**: Searching, editing, navigation, selection, and disclosure

## Constraints

### Searching

- Filterable lists use the combobox pattern (WAI-ARIA Combobox): text input
  with an associated listbox, arrow-key navigation, typeahead, and
  `aria-activedescendant` tracking
- Global search uses a command palette (Dialog + Combobox): `Cmd+K` /
  `Ctrl+K` opens a modal with instant filtering, grouped results, and
  keyboard-only completion
- Search inputs must have a visible label or `aria-label`; placeholder text
  alone is not a label
- Filtering must update results live without requiring a submit action;
  debounce network requests (200-300ms) but show local filtering instantly
- Empty states must be explicit: "No results for X" with a suggestion or
  action, not a blank container
- Clear/reset must be a single action (Escape in combobox, clear button in
  filter bars)

### Editing

- Inline editing uses the edit pattern: display value → click/Enter to
  activate → input with current value → Enter to confirm, Escape to cancel
- Form editing uses react-hook-form with Zod validation: errors appear on
  blur or submit, not on every keystroke
- Destructive actions require confirmation: Dialog with explicit
  confirm/cancel, destructive button visually distinct (red/danger variant)
- Optimistic updates for low-risk edits (toggling, reordering); pessimistic
  updates for high-risk edits (deletion, financial data)
- Undo support for reversible actions where feasible (toast with undo
  action, not just a confirmation dialog)
- Autosave for long-form content with visible save status indicator
  (saved / saving / unsaved changes)

### Navigation

- Primary navigation uses NavigationMenu (Radix): keyboard arrow-key
  traversal, `aria-current="page"` on active item, roving tabindex within
  menu groups
- Breadcrumbs for hierarchical navigation: `<nav aria-label="Breadcrumb">`
  with `aria-current="page"` on the current item, links for all ancestors
- Tab navigation uses Tabs (Radix): arrow keys switch tabs, `aria-selected`
  tracks active tab, tab panels are associated via `aria-labelledby`
- Page-level keyboard shortcuts documented and discoverable (help modal
  via `?` key); shortcuts must not conflict with browser or screen reader
  keys
- Focus must return to the trigger element when closing modals, popovers,
  and dropdown menus
- Navigation landmarks: `<main>`, `<nav>`, `<aside>`, `<header>`,
  `<footer>` — one `<main>` per page, labeled `<nav>` elements when
  multiple exist
- Skip-to-content link as the first focusable element on every page

### Selection

- Single selection: Select (Radix) or RadioGroup — arrow keys cycle options,
  typeahead jumps to matching item
- Multi-selection: Checkbox groups with `aria-describedby` for group context,
  select-all/none controls, count badge showing "N selected"
- Row selection in tables: checkbox column, Shift+click for range select,
  bulk action toolbar appears when selection is non-empty
- Selection state must be visually obvious (not just color — use checkmarks,
  borders, or background patterns for color-blind users)

### Disclosure and Overlays

- Tooltips: Tooltip (Radix) — hover and focus triggered, 200ms open delay,
  Escape to dismiss, never contain interactive content
- Popovers: Popover (Radix) — click triggered, focus trapped inside, Escape
  to close, returns focus to trigger
- Dialogs: Dialog (Radix) — focus trapped, Escape to close, scroll locked on
  body, returns focus to trigger on close
- Dropdown menus: DropdownMenu (Radix) — arrow-key navigation, typeahead,
  submenus, checkable items, Escape closes current level
- Accordions: Accordion (Radix) — arrow keys between headers, Enter/Space
  toggles, `aria-expanded` tracked
- Sheets/drawers: same focus trap and return rules as Dialog

## Drift Signals (anti-patterns to reject in review)

- Custom dropdown without keyboard navigation → use Radix Select or DropdownMenu
- Modal without focus trap → use Radix Dialog
- Search input without listbox association → use combobox pattern
- Tooltip with interactive content (links, buttons) → move to Popover
- Delete button without confirmation → add Dialog confirmation
- Filter that requires clicking "Apply" → filter live with debounce
- Navigation menu built from plain `<div>` + click handlers → use Radix NavigationMenu or semantic `<nav>` + `<a>`
- Tab implementation using divs with onClick → use Radix Tabs
- Focus lost after modal close → ensure focus returns to trigger
- Keyboard shortcut that overrides browser default (Ctrl+P, Ctrl+S) → choose non-conflicting binding

## When to use

Any project with interactive user interfaces that involve searching, editing,
navigating, or selecting data. Composes with `a11y-wcag-aa` for compliance
requirements and `react-nextjs` for React-specific implementation patterns.
Framework-agnostic in principle — the patterns are WAI-ARIA standards; Radix
is the reference implementation for React projects, and shadcn/ui is the
prescribed component library that wraps Radix for React projects.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: shadcn/ui + Radix as the UI-primitives prescription (component library copied, not npm dep)
- DESIGN_SYSTEM: WAI-ARIA interaction patterns for search/edit/nav/select/disclosure; Radix primitives; shadcn component conventions; states
- TEST_PLAN: keyboard navigation, focus-return, active-state, and live-filter behavior checks

## ADR References

- ADR-011: ux-radix owns the Radix and shadcn component-library prescription;
  framework concerns reference rather than re-prescribe

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

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
