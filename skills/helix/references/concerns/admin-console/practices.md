# Practices: Admin Console (operator backend)

These practices realize the `admin-console` concern: the operator's
jobs-to-be-done built as usable UI, with the primary operator workflow exercised
end-to-end through that UI. Access gating defers to `auth` — see
[README-auth-family.md](../README-auth-family.md) for the auth family ownership
table. Evidence rules (`verification`), the e2e tool (`e2e-framework`),
interaction quality (`ux-radix`), the stack (`frontend-framework`), and
hardening (`security-owasp`) each live in their own concerns.

## Design

- Name the **primary user(s)** and, for the operator, their **jobs-to-be-done**:
  the core domain objects they manage and the lifecycle/control actions they
  perform.
- Identify the **primary operator workflow** — the main end-to-end job (e.g.
  "create a list → create a template → schedule a campaign → watch delivery →
  pause it"). This is the workflow the e2e must cover through the UI.
- Scope which operator workflows are in the runnable slice; record deferrals
  (parking-lot), never drop them silently.

## Implementation

- Build **CRUD screens** for the core domain objects (create/edit/delete, not
  just list/detail views) wired to the engine.
- Build the **lifecycle/control actions** the domain needs as UI controls —
  schedule, pause, cancel, resume, retry, archive, revoke, approve — and wire
  them to the engine (add the engine capability if missing, e.g. pause/cancel).
- Make the **primary operator workflow** a navigable sequence of screens an
  operator can complete start to finish.
- Gate the console behind `auth` (authenticated, role-appropriate, tenant-scoped).

## Verification (composes with `verification` + `e2e-framework`)

- The **primary operator workflow** has an e2e that **starts from the rendered
  UI surface and drives the same controls an operator would use**, running green
  against the live system. Direct API-only exercise does not count.
- Form per the `verification` concern: a browser e2e for client-rendered /
  interactivity-heavy UIs; live-server HTTP + rendered-markup assertions for
  server-rendered flows (both first-class).
- The control actions (e.g. pause/cancel) are exercised through the UI as part
  of, or alongside, the primary workflow.

## Quality Gates

- The operator can perform the core CRUD **and** the domain's lifecycle/control
  actions from the UI (not API-only, not read-only).
- The primary operator workflow runs green **end-to-end through the UI** against
  the running system (recorded as verification evidence).
- No "read-only dashboard + backend pipeline" standing in for the operator
  console; deferred operator workflows are recorded, not silently dropped.
