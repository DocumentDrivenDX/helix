# Concern: Security (OWASP)

## Category
security

## Areas
all

## Boundary

This concern owns the **hardening posture** for the product (OWASP Top 10:
injection, CSRF, secret handling, input validation, TLS, dependency auditing,
parameterized queries, error-detail leakage) and the **audit-logging policy**
for security-relevant events — what to log on authz denial, login failure,
privilege escalation. It is composable, applies across every area, and does
not fill a slot.

For the family ownership table (auth / authorization-model / multi-tenancy /
security-owasp, plus the admin-console and unity-catalog neighbors) see
[README-auth-family.md](../README-auth-family.md). Broken Access Control is the
OWASP umbrella; `authorization-model` is the per-handler model that prevents
it, and `multi-tenancy` is the tenant-predicate refinement — neither is
restated here.

## Components

- **Standard**: OWASP Top 10 (current edition)
- **Dependency auditing**: language-specific tooling (see per-stack practices)
- **Secret management**: environment variables or secret manager — never in code or config files
- **TLS**: HTTPS/TLS required for all network-facing services
- **Input validation**: at all system boundaries (API endpoints, file parsers, CLI args)

## Constraints

- No secrets, credentials, API keys, or tokens committed to source control
- All external inputs validated before use; reject or sanitize at the boundary
- Authentication and authorization checked on every protected endpoint
- Dependencies must be audited for known vulnerabilities before release
- HTTPS/TLS enforced for all production network traffic
- SQL queries must use parameterized queries / prepared statements — no string interpolation
- Error responses must not leak implementation details (stack traces, internal paths, SQL errors)

## Per-Stack Dependency Audit Commands

| Stack | Audit command |
|-------|--------------|
| Rust | `cargo deny check advisories` |
| Go | `govulncheck ./...` |
| TypeScript/Bun | `bun audit` |
| Python | `pip-audit` or `uv run pip-audit` |
| Scala | `sbt dependencyCheck` (OWASP plugin) |

## When to use

All projects with network-facing services, user authentication, or data storage.
Security is a cross-cutting concern — it is not a activity or a separate checklist,
it applies throughout every activity of development.

## Artifact Impact

Selecting this concern requires these artifacts to change (a selected concern absent from them is drift):
- ADR: OWASP Top 10 as the security baseline
- ADR: security architecture — secret management, TLS, boundary input validation, dependency auditing
- TEST_PLAN: authz-on-every-protected-endpoint, parameterized-query, and input-validation checks

## ADR References
