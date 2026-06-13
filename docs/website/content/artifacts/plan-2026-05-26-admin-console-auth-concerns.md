---
title: "Plan: `admin-console` + `auth` concerns — the foundational product surfaces (it.35)"
slug: plan-2026-05-26-admin-console-auth-concerns
weight: 620
activity: "Design"
source: "02-design/plan-2026-05-26-admin-console-auth-concerns.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

# Plan: `admin-console` + `auth` concerns — the foundational product surfaces (it.35)

Date: 2026-05-26 · Scope: methodology (new concerns + auth-provider slot + frame auto-select) · Branch: helix-self-improvement-2026-05-24
Runtime-neutral; additive `ddx:` frontmatter preserved. Operator-directed ("admin backend = a missing helix concern").

## Problem (operator-surfaced, bench-confirmed)

Both faithful HubSpot greenfield builds (claude FastAPI, codex Next.js) shipped a backend delivery **pipeline +
read-only dashboards** and omitted the two foundational user-facing surfaces of a real SaaS:
- **No operator admin backend** — no UI to upload/edit a list, edit a template, schedule a campaign to a list,
  watch delivery stats, or pause/cancel a send. (claude had CRUD *endpoints* + 5 read pages and no pause/cancel
  even in the API; codex was 4 read-only pages + 1 mutation.)
- **No auth** — no signup, login, sessions, in-tenant roles, or platform admin, in a *multi-tenant* product.

Root cause: nothing in HELIX asserts these surfaces, so "runnable slice" collapsed to "pipeline + dashboards"
and the it.31 e2e "passed" on the pipeline, not the operator's jobs-to-be-done through the UI. Same
locally-correct/globally-wrong failure as it.31, at the product-surface level.

**Evidence to ground the concerns (the two directed admin+auth evolves both independently produced):**
- Auth modeled as an **`auth-provider` slot**: real **local default** (claude `local-sessions` password+magic-link
  behind an `IdentityProvider`; codex `local-password-session-provider`) + **deferred-live external IdP/Auth0**,
  swappable with no call-site change, IdP never hardcoded; signup→tenant+owner; HttpOnly sessions; PBKDF2;
  in-tenant RBAC (owner/admin/member) + platform-admin enforced server-side; tenant isolation through the
  authenticated principal.
- Admin-console: claude's `http-e2e` driven through the UI over the **primary operator workflow** (signup →
  create list → create template → schedule campaign → delivery stats → pause), asserting rendered HTML +
  `aria-current`; both wired operator CRUD + pause/cancel to the engine.

## Change (two concerns + one slot + auto-select), grounded in the above

1. **New exclusive slot `auth-provider`** in `workflows/concerns/slots.yml` — the one swappable
   authentication/identity backend. `defaults: auth-provider: auth-local-sessions`. (Both evolves treated auth
   as a slot; future providers — Auth0/Clerk/OIDC — fill it via their own concern.md `## Slot: auth-provider`.)
2. **New concern `auth`** (`workflows/concerns/auth/{concern.md,practices.md}`), `## Slot: auth-provider`,
   areas `api, data, ui`. Practices (from evidence): an account/multi-tenant product MUST build the auth
   **product surface** — signup that provisions a tenant + its owner, login/logout, server-side sessions
   (HttpOnly), in-tenant RBAC (owner/admin/member or product-appropriate) enforced server-side, a global/
   platform-admin role, and multi-tenant isolation enforced **through the authenticated principal** — with the
   provider behind a swappable interface: a **real working local default** (sessions/password), an external IdP
   (Auth0/OIDC) as a **deferred-live** swap selected by config with **no call-site change** and **never
   hardcoded**. A stub/seam-only auth (no usable signup/login/roles) does NOT satisfy it. Composes with
   `security-owasp`.
3. **New concern `admin-console`** (`workflows/concerns/admin-console/{concern.md,practices.md}`), COMPOSABLE
   (no slot), areas `ui, api`. Practices: for an **operator-facing** product, build the operator's
   **jobs-to-be-done** — CRUD over the core domain objects **+ lifecycle/control actions** (e.g. pause / cancel /
   resume) — as **usable UI screens**, and the **primary operator workflow must be exercised end-to-end THROUGH
   THE UI** (the verification evidence gate + the `e2e-framework` tool drive the real UI over the operator's job;
   `ux-radix` owns the UI quality). A backend pipeline + read-only dashboards does NOT satisfy it — the operator
   must be able to *do their job* from the UI. (This absorbs the "primary-workflow coverage" idea as a concern,
   not a bolt-on gate.) Boundary: `admin-console` owns *which surfaces/workflows exist + e2e-through-UI*;
   `ux-radix` owns *how they look/behave*; `verification` owns *evidence*; the `frontend-framework` slot owns
   *the stack*.
4. **Frame AUTO-SELECT** in `workflows/references/concern-resolution.md` (`high` inferred selection, after 2a/2b):
   - 2c: an **operator-facing / back-office product** (a human operator manages domain objects through a UI)
     auto-selects `admin-console` (recorded assumption).
   - 2d: an **account-based / multi-tenant product** (users sign in; data scoped to accounts/tenants)
     auto-selects `auth` and fills `auth-provider` (default `auth-local-sessions`), recorded assumption.
   Mirror in SKILL.md's frame route (one line) so the surfaced rule is also in the skill body.

## Validation (re-bench)

Fresh greenfield via faithful TUI on the HubSpot brief (or a new operator-facing/multi-tenant brief). Success =
the agent, UNPROMPTED, (a) selects `auth` + `admin-console`, (b) builds real signup/login/roles + the operator
admin UI with control actions, and (c) the e2e drives the **primary operator workflow through the UI** green —
vs the pre-it.35 pipeline+dashboards. Cross-check no over-fire: a non-operator-facing product (a pure API
service, a CLI, a library) does NOT auto-select these.

## Codex plan-review: VERDICT SOUND-WITH-FIXES — all 6 incorporated (corrected structure below)

1. **Split auth: composable requirement vs slot filler.** `auth` = COMPOSABLE concern owning the product
   requirement (signup/login/logout, tenant bootstrap, RBAC, platform-admin, isolation-through-principal) —
   it does NOT fill the slot. `auth-local-sessions` = the default `auth-provider` slot filler (the local
   sessions/password impl). Future `auth0-oidc`/`clerk` fill the same slot. (Avoids a provider swap replacing
   the generic auth product requirement.)
2. **`admin-console` boundary** = "required operator product surface + required workflow-coverage target." It
   does NOT own evidence (verification), runner/form (e2e-framework), stack (frontend-framework), UI quality
   (ux-radix), or security hardening (security-owasp) — state each explicitly.
3. **Crisp auto-select triggers (deterministic, no over-fire):** `admin-console` only when a human operator/
   back-office/admin must manage mutable domain objects or lifecycle state through a UI (NOT pure API / CLI /
   library / public content site / read-only dashboard unless an operator UI is explicitly required). `auth`
   only when the product has accounts/users/tenants/orgs/sign-in/session/roles/principal-scoped data or actions
   (NOT anonymous sites / libraries / single-user local CLIs / machine-only APIs unless principals are explicit).
4. **e2e-through-the-UI teeth:** "the workflow starts from the rendered UI surface and drives the same controls
   an operator would use; direct API-only e2e does NOT satisfy `admin-console`." Let `verification` decide the
   form — browser for client-rendered, live-server HTTP + rendered-markup assertions for server-rendered (it.33).
5. **Lifecycle/control actions explicit:** `admin-console` requires CRUD **plus** domain lifecycle controls where
   the domain has controllable state (schedule / pause / cancel / resume / retry / archive / revoke / approve).
   "Read-only dashboard + backend job pipeline" is a named **drift signal**.
6. **Runtime-neutral:** concern/practices text avoids DDx/TUI language; re-bench/validation lives in this plan,
   not the portable concern contract.

### Final file set
- `workflows/concerns/slots.yml`: `auth-provider: { exclusive: true }` + `defaults: auth-provider: auth-local-sessions`.
- `workflows/concerns/auth/{concern.md,practices.md}` — composable (areas api,data,ui), product requirement;
  references the `auth-provider` slot for the backend; composes with `security-owasp`.
- `workflows/concerns/auth-local-sessions/{concern.md,practices.md}` — `## Slot: auth-provider`, the default
  local sessions/password filler (HttpOnly sessions, hashed passwords, behind the swappable interface; external
  IdP e.g. Auth0/OIDC is a *different* filler, deferred-live, never hardcoded).
- `workflows/concerns/admin-console/{concern.md,practices.md}` — composable (areas ui,api).
- `workflows/references/concern-resolution.md` 2c/2d auto-select (crisp triggers) + one-line SKILL.md frame-route mirror.

## Over-engineering guard / risks

- Scope: two concerns + one slot + two auto-select bullets. Don't create per-provider auth concerns now (Auth0
  is a deferred-live swap described in `auth` practices, not a separate concern yet).
- `admin-console` triggers only for **operator-facing** products; `auth` only for **account/multi-tenant** —
  not every product. Keep the practices about *building the surface + e2e-through-UI*, not prescribing specific
  screens/fields.
- Codex-review BOTH ends. Runtime-neutral; preserve `ddx:` frontmatter; SKILL.md 0 ddx hits; re-bless
  `concern-resolution` (stamped).
