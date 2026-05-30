# Practices: Authentication & Accounts

These practices realize the `auth` concern: a real, usable authentication &
account surface, with authorization and isolation enforced through the
authenticated principal, and the backend behind the `auth-provider` slot. For
the family ownership table (and what `security-owasp`, `authorization-model`,
`multi-tenancy`, and the `auth-provider` slot own instead of `auth`) see
[README-auth-family.md](../README-auth-family.md).

## Design

- Identify the principal model: individual users, and — for multi-tenant
  products — the account/tenant they belong to and the role they hold.
- Define the role model and the capability each role grants (e.g. member →
  read; admin → +write/act; owner → +manage; platform/global-admin →
  cross-tenant). Record it (an ADR or an authz capability table).
- Decide the `auth-provider` filler (default `auth-local-sessions`); record any
  deferred external IdP (Auth0/OIDC) as a slot swap, not a rewrite.

## Implementation

- **Onboarding**: signup creates the account/tenant **and** its owner principal,
  then establishes a session — a brand-new user can reach the product.
- **Sessions**: login / logout with server-side sessions; protected surfaces
  redirect unauthenticated requests to login.
- **RBAC**: resolve the principal once per request; gate every protected action
  server-side by capability; return forbidden (not a silent no-op, not a hidden
  button) on denial.
- **Isolation**: derive the account/tenant scope from the authenticated
  principal and apply it to every read and write; a cross-account identifier
  must be unreachable.
- **Swappable backend**: all calls go through the `auth-provider` interface;
  selecting a different filler (e.g. an external IdP) is config, not a call-site
  change; vendor/IdP names are contained to the filler.

## Verification (composes with the `verification` concern)

- The auth surface is exercised against the **running** system: a real
  signup → login → authorized action → logout, observed (not asserted).
- At least one **authorization-denied** path is exercised (a role/tenant that
  must NOT be able to act is refused server-side).
- When an `admin-console` is present, the primary operator workflow e2e starts
  by **signing in through the UI** (see `admin-console` practices).

## Quality Gates

- A new principal can sign up (provisioning the account/tenant + owner), log in,
  and log out against the running system — observed.
- A protected action is refused for an unauthorized role/tenant, server-side.
- Cross-account/tenant data is unreachable for a principal scoped elsewhere.
- The auth backend is reached only through the `auth-provider` interface; the
  default local filler works; any external IdP is a recorded, swappable
  deferral — never hardcoded across call sites, never a stub passed off as done.
