# Concern: Admin Console (operator backend)

## Category
quality-attribute

## Areas
ui, api

## Boundary

This concern owns the **operator product surface and its workflow-coverage
target**: for an operator-facing product, the human operator can do their
jobs-to-be-done from the UI. It is composable.

For access gating, `admin-console` references `auth` — the operator surface is
what `auth` gates; see [README-auth-family.md](../README-auth-family.md) for
the auth family ownership table. For evidence (`verification`), the e2e
tool/form (`e2e-framework` slot), interaction quality (`ux-radix`), the stack
(`frontend-framework` slot), and hardening (`security-owasp`), see those
concerns directly.

`admin-console` owns the one thing those do not state: **the operator's
jobs-to-be-done — CRUD over the core domain objects plus the domain's
lifecycle/control actions — must be built as usable UI, and the primary
operator workflow must be exercised end-to-end through that UI.** A backend
pipeline with read-only dashboards does not satisfy it.

## Components

- **Manage the core domain objects**: create / read / update / delete the
  product's primary entities through the UI (e.g. lists, records, templates,
  campaigns) — not just view them.
- **Lifecycle / control actions**: where a domain object has controllable state,
  the operator can drive it from the UI — schedule, pause, cancel, resume,
  retry, archive, revoke, approve, etc., as the domain requires.
- **Primary operator workflow**: the end-to-end job the operator actually
  performs, wired to the engine and reachable as a sequence of UI screens.

## Constraints

### Build the operator's jobs-to-be-done as usable UI — not a read-only shell

- The operator must be able to **act**, not just observe: the core CRUD and the
  domain's control actions exist as real UI screens wired to the engine.
- "Read-only dashboard + backend job pipeline" is **not** an admin console — it
  is the named drift signal this concern exists to catch.

### Cover the primary operator workflow end-to-end through the UI

- Identify the product's **primary operator workflow** (the main job-to-be-done)
  and build it as a navigable UI flow.
- It must be **exercised end-to-end through the UI**: the workflow starts from
  the rendered UI surface and drives the **same controls an operator would use**.
  A direct API-only e2e does NOT satisfy this concern. (`verification` records
  the evidence; the `e2e-framework` slot supplies the form — a browser e2e for
  client-rendered/interactivity-heavy UIs, or live-server HTTP + rendered-markup
  assertions for server-rendered flows, per the verification concern.)

### Stay in your lane

- Do not re-specify evidence rules (`verification`), the e2e tool
  (`e2e-framework`), interaction quality (`ux-radix`), the stack
  (`frontend-framework`), security hardening (`security-owasp`), or access
  gating (`auth`). Require the surface + the workflow coverage; let those own
  the rest.

## Drift Signals (anti-patterns to reject in review)

- **Read-only dashboards + a backend pipeline, no operator actions** → the admin
  console is missing; build the CRUD + control surface
- CRUD exists in the **API** but there is no UI to drive it → not an operator
  console; build the screens
- A domain object with controllable state but **no pause/cancel/etc. control** in
  the UI → lifecycle actions missing
- The e2e drives the engine **programmatically / API-only**, skipping the UI →
  does not satisfy the through-the-UI coverage target
- "Slice" scoped to the backend mechanics, deferring the operator UI as
  secondary → the operator surface IS the product for an operator-facing app

## When to use

Operator-facing / back-office / admin products — where a human operator (or
admin) must manage mutable domain objects or lifecycle state through a UI. High
autonomy auto-selects this concern for such products (see
`workflows/references/concern-resolution.md`). Do **not** select it for pure API
services, CLIs, libraries, public/marketing content sites, or read-only
dashboards unless an operator UI is explicitly required. Compose with the
`frontend-framework` slot, `ux-radix`, `verification`, the `e2e-framework` slot,
and (usually) `auth`.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- FEAT: operator CRUD over core domain objects + lifecycle/control actions + the primary operator workflow as usable UI
- DESIGN_SYSTEM: operator UI screens for manage + control actions (not a read-only dashboard)
- ADR: which operator workflows are in the slice vs deferred (deferral recorded)

## ADR References

Projects record an ADR when scoping which operator workflows are in the slice
and which are deferred (with the deferral recorded, not silent).
