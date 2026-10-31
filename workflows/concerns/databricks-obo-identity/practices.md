# Practices: Databricks Apps identity (auth-provider)

These practices realize the `auth-provider` filler for apps hosted on
Databricks Apps. They cover the *mechanism*; for the family ownership table
see [README-auth-family.md](../README-auth-family.md), and for the platform
identity rules see `databricks-apps`.

## Design

- **Provider interface**: one `resolve_principal` reading the forwarded user
  and email; the rest of the app calls only this interface.
- **Roles**: map directory groups to app roles in one place, resolved
  server-side per request.
- **Grants**: name the group granted `CAN_USE` in each environment.

## Build

- No credential store, password handling, or login route.
- Resolve the principal once per request; return unauthenticated when the
  forwarded identity is absent.
- Configure the fixture identity only in local and test settings, and refuse it
  when the app runs deployed.

## Test

- An unauthenticated request (no forwarded identity) is refused.
- The fixture identity is rejected under deployed configuration.
- A user outside the granted group cannot reach the app; a role-gated action is
  refused for a principal without the role (composes with `auth` and
  `authorization-model`).
- On-behalf-of calls are exercised on a deployed app and recorded as evidence
  (`verification`).
