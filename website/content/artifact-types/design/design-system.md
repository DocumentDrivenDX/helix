---
title: "Design System"
linkTitle: "Design System"
slug: design-system
activity: "Design"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

DESIGN.md is the **per-project interface system**. Its unique job is to record
the app-specific UX/design-system decisions a builder needs to make the
interface consistent and legible: the navigation model and active-state
convention, the visual hierarchy, the applicable interaction states, and the
design tokens.

It is this app's **instance** of the interface-quality guidelines that the
`ux-radix` concern prescribes — it applies and concretizes those guidelines for
this product. It is **not** a mirror or restatement of the concern library, and
it is **not** an architecture document.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
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
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/DESIGN.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a><br><a href="/artifact-types/test/story-test-plan/">Story Test Plan</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># DESIGN.md Generation Prompt

Create the project&#x27;s `DESIGN.md` — the concrete interface-system instance for
this app.

## Purpose

DESIGN.md is the **per-project interface system**. Its unique job is to record
the app-specific UX/design-system decisions a builder needs to make the
interface consistent and legible: the navigation model and active-state
convention, the visual hierarchy, the applicable interaction states, and the
design tokens.

It is this app&#x27;s **instance** of the interface-quality guidelines that the
`ux-radix` concern prescribes — it applies and concretizes those guidelines for
this product. It is **not** a mirror or restatement of the concern library, and
it is **not** an architecture document.

## Reference Anchors

- The `ux-radix` concern (`practices.md`, `concern.md`) — the guidelines this
  document instantiates, including the required current-location cue (visible
  active state + `aria-current=&quot;page&quot;`) and the where-applicable interaction
  states.
- `a11y-wcag-aa` — `aria-current` is both a UX and an accessibility signal; keep
  the active-state convention consistent with it.

## Focus

- Create one project artifact at `docs/helix/02-design/DESIGN.md`.
- Name the navigation model and a **concrete** active-state convention: the
  visible active cue **and** `aria-current=&quot;page&quot;` on the active nav item, with
  the visible style derived from / bound to that state.
- Capture the visual hierarchy and the design tokens as concrete values.
- List interaction states **where applicable** — do not demand every state on
  every element.
- Keep architecture, data flow, component implementation internals, and ADR
  material OUT — state these as explicit non-goals.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Navigation model, active-state convention, visual hierarchy, interaction states, tokens | DESIGN.md |
| System-wide structure, deployment, data flow | Architecture |
| One architecture-significant decision | ADR |
| How a specific component is implemented (props, state, files) | Technical Design |
| Which test asserts the active-nav cue | Story/Project Test Plan |

## Completion Criteria

- The navigation section names the active-state convention and requires
  `aria-current=&quot;page&quot;` on the active nav item.
- Interaction states are scoped where-applicable.
- Tokens name concrete values, not placeholders.
- The non-goals section excludes architecture, data flow, component internals,
  and ADR material.
- The document reads as this app&#x27;s instance of the guidelines, not a copy of
  the `ux-radix` concern library.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: design-system
---

# DESIGN.md — [App Name]

This is the per-project **interface system**: the concrete UX/design-system
decisions this app commits to. It is this app&#x27;s *instance* of the interface
guidelines in the `ux-radix` concern — not a copy of the concern library.

## Navigation and Active State

[Describe the navigation model: top nav, sidebar, tabs, or a combination, and
where each is used.]

**Active-state convention (required):** When the user is on a navigable
destination, the active nav item shows a visible active state **and** carries
`aria-current=&quot;page&quot;`. State the concrete visible cue (e.g. &quot;left border +
bolder label + tinted background&quot;) and bind it to a stable class/token so the
visual style is *derived from* the active state. `aria-current` is also an
accessibility signal (composes with `a11y-wcag-aa`). State the **contract** here
(the cue + how the visible style binds to the state); *which* test asserts it,
on *which* route, belongs in the story/project test plan — not in DESIGN.md.

| Surface | Component | Active cue (visible) | Semantic |
|---|---|---|---|
| [Primary nav] | [e.g. sidebar links] | [e.g. tinted bg + left border] | `aria-current=&quot;page&quot;` |
| [Secondary nav] | [e.g. tabs] | [e.g. underline] | `aria-selected` |

## Visual Hierarchy

[How the interface ranks importance. Name the rules, not adjectives.]

- **Layout**: [primary regions, where the eye lands first, density]
- **Type scale**: [the steps — e.g. display / h1 / h2 / body / caption]
- **Weight &amp; emphasis**: [how primary vs secondary vs tertiary content is distinguished]
- **Spacing rhythm**: [the spacing pattern that separates and groups content]

## Interaction States

State the interaction states this app uses, **where applicable** — only where
the state actually exists for that element, not every state on every element.

| State | Applies to | Convention |
|---|---|---|
| Hover + `:focus-visible` | Enabled interactive controls (buttons, links, toggles, inputs) | [visible hover + keyboard focus ring] |
| Disabled | [controls that can be disabled] | [disabled affordance + `disabled`/`aria-disabled`, not color alone] |
| Loading | [async actions: save, submit, fetch] | [progress signal + double-submit guard] |
| Empty | [data/content surfaces] | [icon + message + primary action] |
| Error | [data/form surfaces] | [message + retry/fix path; no raw error codes] |

## Tokens

Concrete values, not placeholders.

### Color
[Palette: brand, neutrals, semantic (success/warning/danger/info), surfaces.]

### Spacing
[Spacing scale — e.g. 4 / 8 / 12 / 16 / 24 / 32 / 48.]

### Type
[Font families and the type scale with sizes/line-heights/weights.]

## Non-Goals

This document is the **interface system only**. It deliberately does NOT cover:

- **Runtime architecture** — containers, services, deployment → `architecture.md`.
- **Data flow** — how data moves through the system → `architecture.md` / solution design.
- **Component implementation internals** — props, state management, file layout
  → technical designs (`TD-XXX`).
- **Architecture-significant decisions** — these belong in **ADRs**, not here.

If a decision is about *how the system is built* rather than *how the interface
looks and behaves*, it belongs in architecture / solution-design / ADRs.

## Review Checklist

- [ ] Navigation section names the active-state convention AND requires
      `aria-current=&quot;page&quot;` on the active nav item
- [ ] Active visual cue is derived from / bound to the active state, not a
      free-floating style
- [ ] Interaction states are scoped where-applicable, not demanded universally
- [ ] Visual hierarchy is concrete enough to build against
- [ ] Tokens name real values (palette, spacing scale, type scale)
- [ ] Non-goals section keeps architecture, data flow, component internals, and
      ADR material out of this document
- [ ] Reads as this app&#x27;s instance of the guidelines, not a copy of the
      `ux-radix` concern library</code></pre></details></td></tr>
</tbody>
</table>
