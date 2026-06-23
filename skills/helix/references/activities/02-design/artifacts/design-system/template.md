---
ddx:
  id: design-system
---

# DESIGN.md — [App Name]

This is the per-project **interface system**: the concrete UX/design-system
decisions this app commits to. It is this app's *instance* of the interface
guidelines in the `ux-radix` concern — not a copy of the concern library.

## Navigation and Active State

[Describe the navigation model: top nav, sidebar, tabs, or a combination, and
where each is used.]

**Active-state convention (required):** When the user is on a navigable
destination, the active nav item shows a visible active state **and** carries
`aria-current="page"`. State the concrete visible cue (e.g. "left border +
bolder label + tinted background") and bind it to a stable class/token so the
visual style is *derived from* the active state. `aria-current` is also an
accessibility signal (composes with `a11y-wcag-aa`). State the **contract** here
(the cue + how the visible style binds to the state); *which* test asserts it,
on *which* route, belongs in the story/project test plan — not in DESIGN.md.

| Surface | Component | Active cue (visible) | Semantic |
|---|---|---|---|
| [Primary nav] | [e.g. sidebar links] | [e.g. tinted bg + left border] | `aria-current="page"` |
| [Secondary nav] | [e.g. tabs] | [e.g. underline] | `aria-selected` |

## Visual Hierarchy

[How the interface ranks importance. Name the rules, not adjectives.]

- **Layout**: [primary regions, where the eye lands first, density]
- **Type scale**: [the steps — e.g. display / h1 / h2 / body / caption]
- **Weight & emphasis**: [how primary vs secondary vs tertiary content is distinguished]
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
      `aria-current="page"` on the active nav item
- [ ] Active visual cue is derived from / bound to the active state, not a
      free-floating style
- [ ] Interaction states are scoped where-applicable, not demanded universally
- [ ] Visual hierarchy is concrete enough to build against
- [ ] Tokens name real values (palette, spacing scale, type scale)
- [ ] Non-goals section keeps architecture, data flow, component internals, and
      ADR material out of this document
- [ ] Reads as this app's instance of the guidelines, not a copy of the
      `ux-radix` concern library
