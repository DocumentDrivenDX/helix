---
title: "Plan — UX interface guidelines (ux-radix active-state) + DESIGN.md artifact (2026-05-25)"
slug: plan-2026-05-25-ux-design
weight: 600
activity: "Design"
source: "02-design/plan-2026-05-25-ux-design.md"
generated: true
---
# Plan — UX interface guidelines (ux-radix active-state) + DESIGN.md artifact (2026-05-25)

## Context

Operator, inspecting the live demo apps: clicking "Invoices" gives **no current-location feedback** — no
active tab, no `aria-current`, no header change. HELIX prescribes navigation *components* (ux-radix) but
nothing requires indicating the **current location** or other visual cues. There's also no per-project design
artifact. Operator decision (recorded): **strengthen `ux-radix` + add a DESIGN.md artifact**, and **mechanize
the review** — visual cues must be asserted by the browser e2e (not eyeballed), feeding the it.25/26 e2e gate.

Scope-disciplined: extend one concern's practices + add one artifact + one e2e-assertion requirement. No new
concern, no slot.

## Changes

- **U1 — `ux-radix` practices: required visual cues.** The current page MUST show an active state **and**
  `aria-current="page"` on the active nav item (ARIA/navigation semantics, framework-agnostic; also an a11y
  signal — composes with `a11y-wcag-aa`). Interactive elements express their states **where applicable**
  (codex fix 1): hover + **focus-visible** for enabled interactive controls; disabled where disablement
  exists; loading for async actions; empty/error for data/form/content surfaces. (ux-radix already owns the
  Navigation section — codex fix 6: keep it here, not a new concern.)
- **U2 — `DESIGN.md` artifact (per-project, 02-design).** A governed artifact capturing the app's concrete
  **interface-system** decisions: navigation model + active-state convention, visual hierarchy, the
  applicable interaction states, and tokens (color/spacing/type). It is the app-specific UX/design-system
  *instance* — not a mirror of the concern library (codex fix 5). **Non-goal** (codex fix 4): no runtime
  architecture, data flow, component implementation internals, or ADR material — those live in
  architecture/solution-design/ADRs. Template + prompt + meta + example.
- **U3 — Mechanized visual-cue verification.** The browser e2e (the `e2e-framework` slot, run by the
  `verification` gate) MUST assert the current-location cue: navigate to a route → assert the active nav item
  carries **`aria-current="page"` (required, non-optional)**; an active class/style may be asserted
  *additionally* but is **never a substitute** for `aria-current` (codex fix 2). The active visual style
  should be **derived from that state** (or asserted via a stable token/class contract) so the cue is both
  semantic and visible — **no pixel/screenshot assertions** for this gate (codex fix 3). This makes "does it
  show me where I am?" a checkable gate (the operator's exact bug becomes a failing test until fixed).

## Bucket 1 — docs/ specs

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| U1/U2 | Govern interface-quality guidelines + the DESIGN.md artifact (current-location feedback, interactive states, DESIGN.md as the per-project design system) | extend `FEAT-008-artifact-template-quality.md` | FEAT covers the visual-cue guidelines + DESIGN.md artifact. *(Revised post-diff-review: no FEAT-006 note — FEAT-006 governs the concern mechanism, not concern-specific UX content, which lives in the ux-radix concern + DESIGN.md.)* |

## Bucket 2 — workflows/ concern + artifact + actions

| # | Change | File(s) | Done when |
|---|--------|---------|-----------|
| U1 | Extend ux-radix Navigation/practices: current page MUST show active state + `aria-current="page"`; interactive states **where applicable** (hover/focus-visible for enabled controls; disabled where it exists; loading for async; empty/error for data/form/content surfaces) | `workflows/concerns/ux-radix/practices.md` | practices require current-location feedback + applicable-state guidance |
| U2 | New DESIGN.md artifact: template + prompt + meta + example (nav model, active-state convention, hierarchy, applicable states, tokens) — with the explicit non-goal (no architecture/data-flow/impl-internals/ADR) | `workflows/activities/02-design/artifacts/design-system/{template.md,prompt.md,meta.yml,example.md}` (output `docs/helix/02-design/DESIGN.md`) | artifact exists; meta output = DESIGN.md; non-goal stated |
| U3 | Verification/e2e: a UI web app's browser e2e MUST assert `aria-current="page"` (required) on the active nav for ≥1 route; active class/style only as an additional assertion, never a substitute; no screenshot assertions | `workflows/concerns/ux-radix/practices.md` + `workflows/concerns/e2e-playwright/practices.md` (cross-ref verification) | practices require the aria-current e2e assertion (non-optional) |

## Bucket 3 — skill (`skills/helix/SKILL.md`) — normative, runtime-neutral

| # | Change | Done when |
|---|--------|-----------|
| U1/U3 | UI guidance: current page shows active state + aria-current; the e2e asserts that cue | SKILL.md reflects the visual-cue requirement + its e2e assertion |

## How we'll re-run the bench (validate THIS plan)

Parallel re-bench (claude + codex). Expect: both apps render an active-nav state with `aria-current="page"`,
a `DESIGN.md` is produced under docs/helix/02-design/, and the browser e2e **asserts** the active-nav cue
(visible in the e2e spec + still end-to-end-completeness=VERIFIED). The operator's "Invoices gives no
feedback" bug should not recur — and if a runtime omits the cue, its e2e assertion fails (caught, not shipped).

## Invariants
- Strengthen `ux-radix` (no new concern/slot). DESIGN.md is the per-project instance of the guidelines.
- Visual-cue review is MECHANIZED via e2e assertions (not eyeballed) — composes with the verification gate.
- `aria-current` is both UX and a11y — keep consistent with `a11y-wcag-aa`.
- Runtime neutrality; no `Skill tool_use`; don't flatten the loop. Keep `check-workflow-paths` green; re-bless
  ddx hashes; codex-review this plan BEFORE and the diff AFTER.
