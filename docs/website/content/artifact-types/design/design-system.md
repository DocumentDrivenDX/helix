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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/DESIGN.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/design/technical-design/">Technical Design</a><br><a href="../../../artifact-types/test/story-test-plan/">Story Test Plan</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># DESIGN.md Generation Prompt&#10;&#10;Create the project&#x27;s `DESIGN.md` — the concrete interface-system instance for&#10;this app.&#10;&#10;## Purpose&#10;&#10;DESIGN.md is the **per-project interface system**. Its unique job is to record&#10;the app-specific UX/design-system decisions a builder needs to make the&#10;interface consistent and legible: the navigation model and active-state&#10;convention, the visual hierarchy, the applicable interaction states, and the&#10;design tokens.&#10;&#10;It is this app&#x27;s **instance** of the interface-quality guidelines that the&#10;`ux-radix` concern prescribes — it applies and concretizes those guidelines for&#10;this product. It is **not** a mirror or restatement of the concern library, and&#10;it is **not** an architecture document.&#10;&#10;## Reference Anchors&#10;&#10;- The `ux-radix` concern (`practices.md`, `concern.md`) — the guidelines this&#10;  document instantiates, including the required current-location cue (visible&#10;  active state + `aria-current=&quot;page&quot;`) and the where-applicable interaction&#10;  states.&#10;- `a11y-wcag-aa` — `aria-current` is both a UX and an accessibility signal; keep&#10;  the active-state convention consistent with it.&#10;&#10;## Focus&#10;&#10;- Create one project artifact at `docs/helix/02-design/DESIGN.md`.&#10;- Name the navigation model and a **concrete** active-state convention: the&#10;  visible active cue **and** `aria-current=&quot;page&quot;` on the active nav item, with&#10;  the visible style derived from / bound to that state.&#10;- Capture the visual hierarchy and the design tokens as concrete values.&#10;- List interaction states **where applicable** — do not demand every state on&#10;  every element.&#10;- Keep architecture, data flow, component implementation internals, and ADR&#10;  material OUT — state these as explicit non-goals.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Navigation model, active-state convention, visual hierarchy, interaction states, tokens | DESIGN.md |&#10;| System-wide structure, deployment, data flow | Architecture |&#10;| One architecture-significant decision | ADR |&#10;| How a specific component is implemented (props, state, files) | Technical Design |&#10;| Which test asserts the active-nav cue | Story/Project Test Plan |&#10;&#10;## Completion Criteria&#10;&#10;- The navigation section names the active-state convention and requires&#10;  `aria-current=&quot;page&quot;` on the active nav item.&#10;- Interaction states are scoped where-applicable.&#10;- Tokens name concrete values, not placeholders.&#10;- The non-goals section excludes architecture, data flow, component internals,&#10;  and ADR material.&#10;- The document reads as this app&#x27;s instance of the guidelines, not a copy of&#10;  the `ux-radix` concern library.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: design-system&#10;---&#10;&#10;# DESIGN.md — [App Name]&#10;&#10;This is the per-project **interface system**: the concrete UX/design-system&#10;decisions this app commits to. It is this app&#x27;s *instance* of the interface&#10;guidelines in the `ux-radix` concern — not a copy of the concern library.&#10;&#10;## Navigation and Active State&#10;&#10;[Describe the navigation model: top nav, sidebar, tabs, or a combination, and&#10;where each is used.]&#10;&#10;**Active-state convention (required):** When the user is on a navigable&#10;destination, the active nav item shows a visible active state **and** carries&#10;`aria-current=&quot;page&quot;`. State the concrete visible cue (e.g. &quot;left border +&#10;bolder label + tinted background&quot;) and bind it to a stable class/token so the&#10;visual style is *derived from* the active state. `aria-current` is also an&#10;accessibility signal (composes with `a11y-wcag-aa`). State the **contract** here&#10;(the cue + how the visible style binds to the state); *which* test asserts it,&#10;on *which* route, belongs in the story/project test plan — not in DESIGN.md.&#10;&#10;| Surface | Component | Active cue (visible) | Semantic |&#10;|---|---|---|---|&#10;| [Primary nav] | [e.g. sidebar links] | [e.g. tinted bg + left border] | `aria-current=&quot;page&quot;` |&#10;| [Secondary nav] | [e.g. tabs] | [e.g. underline] | `aria-selected` |&#10;&#10;## Visual Hierarchy&#10;&#10;[How the interface ranks importance. Name the rules, not adjectives.]&#10;&#10;- **Layout**: [primary regions, where the eye lands first, density]&#10;- **Type scale**: [the steps — e.g. display / h1 / h2 / body / caption]&#10;- **Weight &amp; emphasis**: [how primary vs secondary vs tertiary content is distinguished]&#10;- **Spacing rhythm**: [the spacing pattern that separates and groups content]&#10;&#10;## Interaction States&#10;&#10;State the interaction states this app uses, **where applicable** — only where&#10;the state actually exists for that element, not every state on every element.&#10;&#10;| State | Applies to | Convention |&#10;|---|---|---|&#10;| Hover + `:focus-visible` | Enabled interactive controls (buttons, links, toggles, inputs) | [visible hover + keyboard focus ring] |&#10;| Disabled | [controls that can be disabled] | [disabled affordance + `disabled`/`aria-disabled`, not color alone] |&#10;| Loading | [async actions: save, submit, fetch] | [progress signal + double-submit guard] |&#10;| Empty | [data/content surfaces] | [icon + message + primary action] |&#10;| Error | [data/form surfaces] | [message + retry/fix path; no raw error codes] |&#10;&#10;## Tokens&#10;&#10;Concrete values, not placeholders.&#10;&#10;### Color&#10;[Palette: brand, neutrals, semantic (success/warning/danger/info), surfaces.]&#10;&#10;### Spacing&#10;[Spacing scale — e.g. 4 / 8 / 12 / 16 / 24 / 32 / 48.]&#10;&#10;### Type&#10;[Font families and the type scale with sizes/line-heights/weights.]&#10;&#10;## Non-Goals&#10;&#10;This document is the **interface system only**. It deliberately does NOT cover:&#10;&#10;- **Runtime architecture** — containers, services, deployment → `architecture.md`.&#10;- **Data flow** — how data moves through the system → `architecture.md` / solution design.&#10;- **Component implementation internals** — props, state management, file layout&#10;  → technical designs (`TD-XXX`).&#10;- **Architecture-significant decisions** — these belong in **ADRs**, not here.&#10;&#10;If a decision is about *how the system is built* rather than *how the interface&#10;looks and behaves*, it belongs in architecture / solution-design / ADRs.&#10;&#10;## Review Checklist&#10;&#10;- [ ] Navigation section names the active-state convention AND requires&#10;      `aria-current=&quot;page&quot;` on the active nav item&#10;- [ ] Active visual cue is derived from / bound to the active state, not a&#10;      free-floating style&#10;- [ ] Interaction states are scoped where-applicable, not demanded universally&#10;- [ ] Visual hierarchy is concrete enough to build against&#10;- [ ] Tokens name real values (palette, spacing scale, type scale)&#10;- [ ] Non-goals section keeps architecture, data flow, component internals, and&#10;      ADR material out of this document&#10;- [ ] Reads as this app&#x27;s instance of the guidelines, not a copy of the&#10;      `ux-radix` concern library</code></pre></details></td></tr>
</tbody>
</table>
