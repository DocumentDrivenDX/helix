---
title: "Auth family — ownership table"
generated: true
---

The auth family is a five-way cluster of concerns whose boundaries are easy to
restate and easy to confuse. Per ADR-006 (concern boundary lives once, in
`concern.md`), each concern in the family states its own boundary in its own
`concern.md`. This README is the **single ownership table** the family's
concerns cross-reference, so the per-concern files do not restate each other's
scope.

Two cross-tree neighbors (`admin-console`, `unity-catalog`) are included
because they materially compose with the family but live outside it.

## Family members and what each owns

| Concern | Owns |
|---|---|
| `auth` | principal / session / account bootstrap; **session-token semantics** (issuance, rotation, revocation) |
| `authorization-model` | permission semantics (RBAC / ABAC / ReBAC) and the deny-by-default per-handler check |
| `multi-tenancy` | tenant predicate; tenant scoping rules (the inter-tenant guarantee) |
| `security-owasp` | hardening posture; **audit-logging policy** (what to log on authz denial) |

The `auth-provider` slot (default filler: `auth-local-sessions`) sits beneath
`auth` and owns the *mechanism* (how identities/sessions are stored and
verified). A different slot filler (Auth0/OIDC, Clerk, …) is a swap, not a
rewrite. The slot is what `auth` defers to; it is not itself a member of the
ownership table because it has no scope `auth` does not already cover at the
surface level.

## Neighbors that reference into the family

| Neighbor | References |
|---|---|
| `admin-console` | `auth` (for operator-workflow gates — the operator surface is what `auth` gates) |
| `unity-catalog` | `authorization-model` (Databricks catalog grants compose with app-layer authz; neither substitutes for the other) |

## Ordering invariants the family preserves

1. **Authentication precedes authorization.** `auth` establishes the principal;
   `authorization-model` decides what that principal may do. The two are
   composable and ordered; an authz check on no principal is undefined.
2. **Tenant predicate precedes permission.** `multi-tenancy` guarantees the
   record is in the caller's tenant; `authorization-model` then decides whether
   the caller may act on it. A permission check on a wrong-tenant record is
   still a cross-tenant leak.
3. **Hardening is a posture, not a substitute.** `security-owasp` owns the
   umbrella (Broken Access Control, injection, CSRF, secret handling) plus
   audit-logging policy on authz denial. It does not replace the per-handler
   permission check (`authorization-model`) or the tenant predicate
   (`multi-tenancy`).

## Where ambiguous items land

Two items historically fell through the gaps between these concerns; this
README records the owner so reviewers do not have to re-litigate:

- **Session-token semantics** (issuance, rotation, revocation) → `auth`.
  Tokens are the materialization of the session `auth` already owns.
- **Audit-logging policy** (what to log on authz denial, login failure,
  privilege escalation) → `security-owasp`. Logging policy is a hardening
  posture; the authz decision itself is `authorization-model`'s.

## How to use this README

- A concern in the family states **only its own** boundary in its `concern.md`.
- Where a concern would otherwise restate a neighbor's scope, it points here
  ("see `workflows/concerns/README-auth-family.md` for the family ownership
  table") and lets the table do the cross-reference work.
- A new concern that overlaps the family adds itself to the ownership table
  in this README rather than restating the table in its own boundary.
