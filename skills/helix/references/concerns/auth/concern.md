# Concern: Authentication & Accounts

## Category
quality-attribute

## Areas
api, data, ui

## Boundary

This concern owns the **authentication & account product surface** — that an
account/multi-tenant product can actually be signed into and is scoped to its
principals, plus **session-token semantics** (issuance, rotation, revocation).
It is composable and does NOT fill a slot; it defers the *backend* to the
`auth-provider` slot (default `auth-local-sessions`).

For the family ownership table (auth / authorization-model / multi-tenancy /
security-owasp, plus the admin-console and unity-catalog neighbors) see
[README-auth-family.md](../README-auth-family.md).

`auth` owns the one thing the rest of the family does not state: **an
account/tenant product is not done until a real principal can sign up, sign in,
and act only within their authorized scope.**

## Components

- **Onboarding**: a working signup that bootstraps the account/tenant and its
  first owner — not a pre-seeded-only system.
- **Session lifecycle**: login, logout, and server-side sessions.
- **Authorization (RBAC)**: roles appropriate to the product (e.g.
  owner/admin/member) plus, for multi-tenant products, a global/platform-admin;
  enforced **server-side**, never UI-only.
- **Isolation through the principal**: every data access and mutation is scoped
  by the authenticated principal's account/tenant — a cross-account id is
  unreachable, not merely unlinked in the UI.
- **Swappable backend**: all of the above sit behind the `auth-provider` slot
  interface so the provider can change with no call-site rewrite.

## Constraints

### A real, usable auth surface — not a stub or a seam-only abstraction

- Signup, login, logout, and sessions must actually work end-to-end against the
  running system. A provider *interface* with no usable signup/login flow does
  not satisfy this concern.
- Onboarding provisions the account/tenant **and** its owner principal in one
  flow; the product is reachable by a brand-new user, not only by seeded data.

### Authorization and isolation are enforced server-side, through the principal

- Roles gate actions on the server (return forbidden on denial); hiding a button
  is not authorization.
- Every read and write is scoped by the authenticated principal's account/tenant.
  Tenant isolation is a property of the principal, not of careful query-writing.

### The backend is swappable; external IdPs are deferred, never hardcoded

- The auth backend is selected via the `auth-provider` slot. The shipped default
  (`auth-local-sessions`) is a real working local backend. An external IdP
  (Auth0/OIDC, Clerk, …) is a **different slot filler**, swapped in by config
  with **no call-site change** — its identity provider is never hardcoded across
  the app, and a deferred live integration is recorded, not faked as "done".

## Drift Signals (anti-patterns to reject in review)

- A multi-tenant / account product with **no signup, login, or sessions** (data
  silently single-tenant or open) → the auth surface is missing
- Roles checked only in the UI (buttons hidden) with the server still accepting
  the action → authorization not enforced
- Tenant scoping done ad hoc per query instead of through the authenticated
  principal → isolation will leak; bind scope to the principal
- An `AuthProvider`/identity *interface* with no usable signup/login flow behind
  it → seam-only; build the real local default
- A specific IdP (e.g. Auth0) referenced throughout call sites → not swappable;
  contain it to the `auth-provider` slot filler

## When to use

Account-based / multi-tenant products — anything with users, accounts, tenants,
orgs, sign-in/session semantics, roles, or principal-scoped data or actions.
High autonomy auto-selects this concern for such products (see
`workflows/references/concern-resolution.md`). Do **not** select it for
anonymous public sites, libraries, single-user local CLIs, or machine-only
internal APIs unless user/tenant principals are explicit. Compose with the
`auth-provider` slot (backend) and `security-owasp` (hardening).

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- FEAT: signup/login/logout + session lifecycle as a real product surface
- TD: server-side RBAC and principal-scoped isolation behind the swappable auth-provider slot
- DATA_DESIGN: principals/accounts (tenant) and session storage
- ADR: auth-provider filler choice (local sessions now, external IdP later) + role model

## ADR References

Projects record an ADR when choosing or swapping the `auth-provider` filler
(e.g. local sessions now, Auth0/OIDC later) and when defining the role model.
