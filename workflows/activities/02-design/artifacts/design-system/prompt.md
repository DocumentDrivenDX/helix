# DESIGN.md Generation Prompt

Create the project's `DESIGN.md` — the concrete interface-system instance for
this app.

## Purpose

DESIGN.md is the **per-project interface system**. Its unique job is to record
the app-specific UX/design-system decisions a builder needs to make the
interface consistent and legible: the navigation model and active-state
convention, the visual hierarchy, the applicable interaction states, and the
design tokens.

It is this app's **instance** of the interface-quality guidelines that the
`ux-interaction-patterns` concern prescribes — it applies and concretizes those guidelines for
this product. It is **not** a mirror or restatement of the concern library, and
it is **not** an architecture document.

## Reference Anchors

- The `ux-interaction-patterns` concern (`practices.md`, `concern.md`) — the guidelines this
  document instantiates, including the required current-location cue (visible
  active state + `aria-current="page"`) and the where-applicable interaction
  states.
- `a11y-wcag-aa` — `aria-current` is both a UX and an accessibility signal; keep
  the active-state convention consistent with it.

## Focus

- Create one project artifact at `docs/helix/02-design/DESIGN.md`.
- Name the navigation model and a **concrete** active-state convention: the
  visible active cue **and** `aria-current="page"` on the active nav item, with
  the visible style derived from / bound to that state.
- Capture the visual hierarchy and the design tokens as concrete local values or versioned external references.
- List interaction states **where applicable** — do not demand every state on
  every element.
- Keep architecture, data flow, component implementation internals, and ADR
  material OUT — state these as explicit non-goals.
- When the app supports several modalities (screen, voice, chat) or size
  classes, add the optional Modalities, Size Classes and App Frame section:
  the modalities, each size class with its breakpoint, and the app frame
  (screen, top-bar, top-nav or side-nav). Add the optional Destinations by
  Size Class table under Navigation and Active State when destinations move
  between size classes. Wireframes cite these size classes by name.

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
  `aria-current="page"` on the active nav item.
- Interaction states are scoped where-applicable.
- Tokens name concrete local values or versioned external role-token references, not placeholders.
- The non-goals section excludes architecture, data flow, component internals,
  and ADR material.
- The document reads as this app's instance of the guidelines, not a copy of
  the `ux-interaction-patterns` concern library.

## External packages and applicability

When packaged-design-system applies, record installed package versions,
supported themes/appearances, documented token references, component mappings
and gaps. Use installed-version documentation; never assume particular provider
APIs, mandatory dark mode or duplicated branding. A host-owned presentation
contract is recorded where relevant. Local tokens remain an alternative when
no suitable package is available. Name applicable behavior conventions in
Interaction States; test mappings belong in STPs.

## Navigation applicability

The active-page convention applies only where page navigation exists. For a
single-surface or embedded view with none, record in Navigation and Active State:
`Page navigation: not-applicable;` followed by a concrete reason. Do not create
navigation merely to satisfy the template. Tabs still use their own selection
semantics. Review applicability rather than accepting a bare exemption marker.
