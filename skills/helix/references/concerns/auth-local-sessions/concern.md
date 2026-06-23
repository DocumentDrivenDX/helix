# Concern: Local Sessions (auth-provider)

## Category
tech-stack

## Areas
api, data

## Slot
auth-provider

## Boundary

This concern is the **default `auth-provider` slot filler** — a real, working,
self-contained authentication backend that needs no external identity service.
It supplies the *mechanism* the `auth` concern's product surface sits on. An
external IdP (Auth0/OIDC, Clerk, …) is a **different filler of the same slot**,
swapped in without changing call sites.

For the family ownership table (and the boundaries with `auth`,
`authorization-model`, `multi-tenancy`, and `security-owasp`) see
[README-auth-family.md](../README-auth-family.md).

## Components

- **Credential store**: principals with securely hashed passwords (e.g. PBKDF2/
  bcrypt/argon2 with per-credential salt), stored in the project datastore.
- **Sessions**: server-side sessions keyed by an HttpOnly cookie.
- **Provider interface**: a single auth/identity interface the rest of the app
  calls (signup, authenticate, resolve-principal, logout) so the backend is
  swappable.

## Constraints

- Passwords are **hashed** (salted, work-factored) — never stored or logged in
  plaintext.
- Session cookies are **HttpOnly** (and Secure in production); sessions are
  validated server-side on each protected request.
- The app calls the **provider interface**, never local-session internals
  directly — so swapping to an external IdP is a filler change, not a rewrite.
- This filler is the runnable default; it does not preclude selecting an
  external IdP filler for production (recorded as a slot swap / deferred-live).

## Drift Signals (anti-patterns to reject in review)

- Plaintext or unsalted/un-work-factored passwords → use a real password hash
- Client-readable session token (non-HttpOnly) or no server-side validation
- App code reaching into local-session internals instead of the provider
  interface → breaks swappability

## When to use

Fills `auth-provider` for any product that selects the `auth` concern and has no
operator-chosen external IdP. It is the shipped default; operators override per
project (`concerns.local.yml: auth-provider: <other-filler>`) to choose an
external IdP filler instead.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: local sessions as the auth-provider slot filler (swap recorded when moving to an external IdP)
- TD: hashed-credential store, HttpOnly server-side sessions, single provider interface
- DATA_DESIGN: principals with hashed passwords + server-side session store

## ADR References

Record an ADR when swapping this default for an external IdP filler.
