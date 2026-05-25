---
ddx:
  id: example.design-system.depositmatch
  depends_on:
    - example.prd.depositmatch
---

# DESIGN.md — DepositMatch

This is DepositMatch's **interface system**: the concrete UX/design-system
decisions the app commits to. It is DepositMatch's instance of the `ux-radix`
interface guidelines — not a copy of the concern library.

## Navigation and Active State

DepositMatch uses a **persistent left sidebar** for primary navigation
(Dashboard, Imports, Matches, Clients, Settings) and **Radix Tabs** for
same-page switching inside a client view (Overview / Activity / Documents).

**Active-state convention (required):** the sidebar item for the current
section shows a tinted background, a 3px left accent border, and a bolder label
**and** carries `aria-current="page"`. The visible style is bound to the
`data-active` / `aria-current` state via the `.nav-item[aria-current="page"]`
token contract, so the cue is derived from the state rather than set ad hoc.
`aria-current` is also the accessibility signal screen readers announce
(composes with `a11y-wcag-aa`). *(Which test asserts this cue, and on which
route, belongs in the story/project test plan — not here. DESIGN.md states the
contract; the test plan verifies it.)*

| Surface | Component | Active cue (visible) | Semantic |
|---|---|---|---|
| Primary nav | Sidebar links (NavigationMenu) | Tinted bg + 3px left accent border + bold label | `aria-current="page"` |
| Client sub-nav | Tabs | 2px bottom underline in brand color | `aria-selected` |
| Breadcrumb | `<nav aria-label="Breadcrumb">` | Current crumb is non-link, bolder | `aria-current="page"` |

## Visual Hierarchy

- **Layout**: fixed 240px sidebar; content area is a max-1120px centered column.
  The primary action for each screen sits top-right of the content header; the
  eye lands on the screen title, then the primary action, then the data table.
- **Type scale**: Display 32/40, H1 24/32, H2 20/28, Body 14/20, Caption 12/16.
- **Weight & emphasis**: primary content uses weight 600 titles + 400 body;
  secondary metadata uses the neutral-500 color at weight 400; tertiary hints
  use Caption + neutral-400.
- **Spacing rhythm**: 24px between major sections, 16px within a card, 8px
  between a label and its value.

## Interaction States

States are used **where applicable**:

| State | Applies to | Convention |
|---|---|---|
| Hover + `:focus-visible` | All buttons, sidebar links, table row actions, inputs | Hover raises bg one step; `:focus-visible` shows a 2px brand focus ring |
| Disabled | "Commit import" until a summary is confirmed; bulk actions with no selection | Reduced-contrast fill + `disabled` attribute (not color alone) |
| Loading | Import upload, validation run, "Commit import" | Inline spinner on the button + disabled while pending (double-submit guard) |
| Empty | Imports list, Matches list with zero items | Icon + "No imports yet. Upload a bank and invoice CSV to start." + primary action |
| Error | CSV validation results, form submit | Row-level message naming field + reason + retry; never a raw error code |

## Tokens

### Color
- Brand: `#1F6FEB` (primary), `#0B3D91` (primary-hover)
- Neutrals: `#0F172A` (text), `#475569` (text-muted), `#E2E8F0` (border), `#F8FAFC` (surface)
- Semantic: success `#16A34A`, warning `#D97706`, danger `#DC2626`, info `#2563EB`

### Spacing
4 / 8 / 12 / 16 / 24 / 32 / 48 (px), referenced as `space-1` … `space-7`.

### Type
- Family: `Inter, system-ui, sans-serif`; numerals use `tabular-nums` in tables.
- Scale: see Visual Hierarchy type scale above.

## Non-Goals

This document is DepositMatch's **interface system only**. It does NOT cover:

- **Runtime architecture** — the API/worker/Postgres topology lives in
  `architecture.md`.
- **Data flow** — how CSV rows move from upload to validation to commit is the
  solution design / architecture's job, not this document's.
- **Component implementation internals** — react-hook-form wiring, table
  virtualization, and file layout belong in technical designs (`TD-XXX`).
- **Architecture-significant decisions** — e.g. "PostgreSQL as system of
  record" is **ADR-001**, not a DESIGN.md entry.
