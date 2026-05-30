---
title: "Security (OWASP)"
slug: security-owasp
generated: true
aliases:
  - /reference/glossary/concerns/security-owasp
---

**Category:** Security & Compliance · **Areas:** all

## Description

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
[README-auth-family.md](../readme-auth-family/). Broken Access Control is the
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

## Practices by activity

Agents working in any of these activities inherit the practices below via the bead's context digest.

## Requirements (Frame activity)
- Identify trust boundaries: where does data enter the system from untrusted sources?
- Classify data sensitivity: what data requires encryption at rest or in transit?
- Identify authentication model: who authenticates, how, and what are the session semantics?
- Include security acceptance criteria in user stories for any auth, data access, or input-handling feature

## Design
- Apply least-privilege: services, users, and credentials have minimum necessary permissions
- Prefer deny-by-default for authorization (explicitly allow rather than explicitly deny)
- Separate authentication (who are you?) from authorization (what can you do?)
- Never store plaintext passwords — use `argon2id` or `bcrypt`
- Encryption at rest for sensitive data stores; TLS for all transport
- Audit log for security-relevant actions (login, auth failure, privilege escalation)

## Implementation
- Input validation at every system boundary — validate type, length, format, and range
- SQL: use parameterized queries or ORM with parameter binding; no string interpolation
- Secrets: load from environment variables or secret manager at startup; never embed in source
- Error messages: return generic error to clients; log full details server-side with correlation ID
- File operations: validate paths (prevent path traversal); confirm file type before processing
- Dependencies: run audit tool before merging; pin to known-good versions
- TLS: use `rustls` (Rust), Go's stdlib `crypto/tls`, or established TLS library; no SSLv3/TLS 1.0/1.1
- CORS: whitelist allowed origins; do not use wildcard `*` for authenticated endpoints

## Testing
- Include at least one negative test per auth boundary (unauthenticated access must be rejected)
- Fuzz parser inputs where practical (Rust: `cargo fuzz`, Go: `go test -fuzz`, Python: hypothesis)
- Secrets scanning: run `trufflesecurity/trufflehog` or `gitleaks` in CI
- Dependency audit in CI gate (see per-stack commands in concern.md)

## Quality Gates (per-stack, add to CI)
- Rust: `cargo deny check advisories`
- Go: `govulncheck ./...` + `gosec ./...`
- TypeScript: `bun audit`
- Python: `uv run pip-audit`
- All: `gitleaks detect` or equivalent secrets scan on PR

## Incident Response
- Rotate compromised credentials immediately; do not wait to assess
- File a security work item with `security` label; treat as P0 if customer data at risk
- Document the incident in `docs/helix/06-iterate/` post-resolution
