# Concern: Databricks Apps identity (auth-provider)

## Category
tech-stack

## Areas
api, ui

## Slot
auth-provider

## Platform

**Platform-specific (Databricks).** The `auth-provider` filler of the
`databricks-apps` profile in `slots.yml`. Databricks Apps signs users in through
workspace single sign-on before a request reaches the app and forwards their
identity; this filler makes that platform identity the app's only source of
principals. Platform facts are owned by `databricks-apps`.

## Boundary

This concern is an **`auth-provider` slot filler**: the mechanism the `auth`
concern's product surface sits on, swapped in for `auth-local-sessions`. It
owns how the app resolves the principal from the platform and what the app
does not build because the platform signs users in. For the family ownership
table see [README-auth-family.md](../README-auth-family.md).

- **`databricks-apps`** owns the platform identity layer itself: forwarded
  headers, the `x-forwarded-access-token`, `user_api_scopes`, the app service
  principal, and when to call on behalf of the user versus as the service
  principal. This concern does not restate those rules.
- **`auth`** owns the product surface (principal, account bootstrap, session
  semantics); **`authorization-model`** owns what a principal may do.

## Components

- **Provider interface**: one `resolve_principal(request)` the app calls,
  reading the platform-forwarded user and email; no signup, password, or login
  form.
- **Access grant**: a user is a workspace identity granted `CAN_USE` on the app
  through a directory-provisioned group.
- **Role mapping**: app roles derived from directory groups, resolved
  server-side.
- **Local fixture identity**: an explicitly configured stub principal for
  local development and tests, marked as a fixture.

## Constraints

- The platform proxy is the only identity source: the app stores no
  credentials, issues no login of its own, and trusts forwarded identity headers
  only from the platform.
- Every protected request resolves the principal through the provider
  interface; app code never reads identity headers directly elsewhere.
- Calls that read or write user-scoped data run with the user's forwarded token
  per `databricks-apps`; the service principal is never a stand-in for a user.
- Access is granted to groups, not to individual users.
- A fixture identity is accepted only in local and test configuration, never in
  a deployed app.
- On-behalf-of paths are verified on a deployed app, because local runs do not
  receive the user token.

## Drift Signals (anti-patterns to reject in review)

- An app-owned signup, password, or login screen → platform sign-on only
- Identity headers read ad hoc across handlers → one provider interface
- A shared service principal used for user-scoped reads → on-behalf-of
- Per-user `CAN_USE` grants → group grants
- A fixture or header-spoofing identity reachable in a deployed app → local
  and test configuration only

## When to use

Fills `auth-provider` for a product with users that is hosted on Databricks
Apps (`deploy-target: databricks-apps`). It is the `auth-provider` default of the
`databricks-apps` profile. Compose with **`auth`** and
**`authorization-model`**.

Do **not** select it for an app hosted off Databricks, or one whose users
are not Databricks account identities.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- TD: provider interface over platform identity; group-to-role mapping; fixture identity for local use
- Deployment/runbook: the groups granted `CAN_USE` per environment

## ADR References

Selecting this concern needs no ADR; `concerns.md` records it. Write an ADR only
when the project deviates from a constraint here.
