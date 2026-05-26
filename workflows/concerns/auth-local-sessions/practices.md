# Practices: Local Sessions (auth-provider)

These practices realize the default `auth-provider` filler — a working local
auth backend behind the provider interface the `auth` concern requires. They
cover the *mechanism*; the surface/roles/isolation requirements are in `auth`,
and hardening depth is in `security-owasp`.

## Implementation

- **Provider interface**: expose one auth/identity interface (`signup`,
  `authenticate`, `resolve_principal`, `logout`) that the app calls; keep
  local-session internals behind it.
- **Passwords**: hash with a salted, work-factored algorithm (PBKDF2/bcrypt/
  argon2); never store or log plaintext; verify in constant time.
- **Sessions**: issue a server-side session on login, referenced by an HttpOnly
  cookie (Secure in production); validate on each protected request; clear on
  logout.
- **Principal resolution**: `resolve_principal` returns the authenticated
  principal (+ account/tenant + role) for the request, or unauthenticated.
- **Swap path**: document how an external IdP filler (Auth0/OIDC) replaces this
  one — same interface, config-selected, no call-site change.

## Quality Gates

- Passwords are hashed (salted + work-factored); no plaintext anywhere.
- Session cookie is HttpOnly; sessions validated server-side; logout clears them.
- All app auth calls go through the provider interface (no direct internals).
- A working login/logout against the running system is observed (composes with
  `auth` + `verification`).
