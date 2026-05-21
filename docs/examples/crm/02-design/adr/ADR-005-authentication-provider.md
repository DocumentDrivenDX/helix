---
ddx:
  id: ADR-005
  type: architecture-decision-record
  status: resolved
  decision_date: 2026-05-18
  depends_on:
    - crm.prd
    - ADR-001
    - ADR-003
---

# ADR-005: Authentication Provider Selection

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-18 | Resolved | Architecture + Security | crm.prd, ADR-001, ADR-003 | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | CRM MVP requires email + password authentication with workspace isolation. Decisions needed: managed service vs. hand-rolled; session vs. JWT; and how workspace isolation is enforced at the auth layer. |
| Current State | Authentication is unimplemented; only framework (FastAPI) and database (PostgreSQL) are decided. |
| Requirements | PRD R-1: "Each user signs into a team workspace with role-based permissions (rep / manager / admin)." Workspace-level isolation is critical for multi-tenant SaaS. GDPR data deletion (ADR-201) requires direct database access to user records. |
| Decision Drivers | Time-to-launch (learning curve, integration friction); security debt risk (hand-rolled auth accumulates compliance work); vendor lock-in (managed services require migration later); cost (Auth0 licensing vs. self-hosted infrastructure); workspace isolation implementation complexity. |

## Decision

We will implement **hand-rolled JWT authentication with FastAPI-Users** (session management layer) and **bcrypt password hashing**, with workspace isolation enforced at the middleware and database query layers.

**Key Points**: 
- User credentials (email, hashed password) stored in PostgreSQL
- Session tokens (short-lived JWT, 15-min expiry) issued on login
- Refresh tokens (long-lived, 30-day expiry) stored in database for revocation
- Every query scoped to `workspace_id` from request context (injected via middleware)
- GDPR deletion via direct user/token table deletion (no third-party API calls)

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| **Hand-rolled JWT + FastAPI-Users** | Complete control over workspace isolation; no vendor lock-in; straightforward GDPR deletion; lower cost; integrates natively with FastAPI | Requires OWASP auth best practices (password hashing, rate limiting, CSRF, secure headers); team must own security audits | **Selected**: MVP timeline and workspace-isolation complexity favor direct control over managed service convenience |
| **Auth0 (or Cognito / Firebase Auth)** | Reduced security debt; battle-tested; MFA/SSO ready; compliance certifications (SOC2, ISO); handles password reset, email verification | Vendor lock-in; workspace isolation requires custom claims + API integration (more complex than direct DB); cost per user (~$25–80/month per 10k MAU); GDPR deletion requires Auth0 API calls (async, eventual consistency); deployment outside our control | Rejected for MVP: workspace-isolation pattern is simpler with hand-rolled auth; cost and GDPR friction outweigh security benefit at MVP scale |
| **Framework-provided (Django auth)** | Batteries-included; OWASP best practices built-in; familiar to many teams | Not applicable: we selected FastAPI, not Django; would require full Django framework overhead for API-only service | Rejected: architecture decision already excludes Django (ADR-001) |
| **API Gateway with auth (AWS API Gateway + Lambda authorizer)** | Centralized auth, reduced app-layer complexity; can enforce rate limiting at AWS edge | Vendor lock-in to AWS; workspace isolation still requires app-layer checks (not solved by API Gateway); adds operational complexity; doesn't simplify JWT implementation | Rejected for MVP: auth logic still required in application; API Gateway adds cost and operational burden without simplification |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Full control over token expiry, workspace scoping, and user session lifecycle. GDPR compliance is straightforward (delete user record → all sessions invalidated). No third-party API dependency for critical auth path. Integration with FastAPI is idiomatic (dependency injection, middleware). Password hashing uses bcrypt (OWASP-approved, slow by design to prevent brute force). |
| Negative | Team owns the auth implementation and its security properties. Pre-launch security audit is required (threat modeling, penetration testing). Rate limiting, CSRF protection, and secure password reset flow must be explicitly implemented (not automatic like Auth0). Post-MVP, if team grows, may face audit/compliance pressure to migrate to managed service. |
| Neutral | User database tables are straightforward (users, sessions/tokens tables); can co-locate in PostgreSQL with business data (no separate identity provider to operate). |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Hand-rolled implementation has security flaw (e.g., timing attack on token validation, weak password reset) | M | H | Pre-launch security audit by third party. Code review checklist: ✓ password hashing uses bcrypt.hashpw with cost factor ≥12, ✓ token validation uses constant-time comparison, ✓ password reset requires email verification, ✓ rate limiting on login endpoint (5 attempts/minute per email). Document password reset flow (security-critical); test with OWASP test suite (e.g., using pytest + hypothesis for timing attacks). |
| Workspace isolation not enforced at query layer, leaking data across workspaces | M | H | Every database query must inject `WHERE workspace_id = ?` via SQLAlchemy context or middleware. Establish code-review rule: any user-facing query must reference workspace_id from `request.state.workspace_id` (set by auth middleware). Write integration tests that verify cross-workspace data is unreachable (query a contact from workspace B while authenticated to workspace A; assert 404 or permission error). |
| Token refresh is stateless (no revocation), user login persists until expiry | M | M | Store refresh tokens in database (not just JWT secret); track issued_at, revoked_at, expires_at. On logout, mark token revoked. On refresh, check revocation status. Cost: one extra DB query on token refresh (acceptable for auth-critical path). Benefit: can force logout (e.g., after password change, or on security incident) by revoking all refresh tokens for a user. |
| Password reset email can be intercepted or token guessed | L | H | Password reset token: generate cryptographically random 32-byte token, hash it (SHA256), store hash in DB with 15-min expiry. Email contains plain token (not hash; user can't hash what they receive). On reset, hash received token, look up hash in DB, verify expiry, then allow password change. This prevents replaying old reset URLs (after 15 min, hash no longer exists) and allows secure audit trail. Test: generate 1000 reset tokens, verify all unique and not guessable (entropy test). |
| GDPR deletion of user cascades fail, leaving orphaned data | M | M | Use database foreign keys with `ON DELETE CASCADE` on all tables referencing users (sessions, activities, etc.). Add pre-deletion hook: verify no business-critical data orphaned (e.g., don't delete user who owns all team's opportunities without reassignment workflow). Audit trail: deletion is logged to immutable audit table before user record is deleted (for compliance audit). |
| Compliance audit requires migration to Auth0 later (post-MVP) | L | M | Architecture is extensible: if Auth0 is needed, can add Auth0 as a second auth provider (OAuth2 integration) without removing hand-rolled JWT. Transition: new users sign up via Auth0; existing hand-rolled JWT users continue to work (dual-mode auth). No forced migration. Plan migration only if customer contracts explicitly require Auth0 or SOC2 certification (not expected for MVP). |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------| 
| User can sign up with email + password, log in, and access their workspace data without exposing another user's data | Any test failure in cross-workspace isolation tests (e.g., workspace A user can read workspace B contact) |
| Session token expires after 15 minutes of inactivity; refresh token expires after 30 days | Token still valid after 15 min of inactivity (session expiry bug) or after 30 days (refresh expiry bug) |
| Password reset requires email verification; reset URL is single-use | Password reset URL can be reused multiple times or works without email verification |
| User deletion removes all session tokens and activities within 5 seconds (GDPR compliance) | User deletion takes >10 seconds or leaves orphaned data in database |
| Rate limiting prevents brute-force login attacks (max 5 attempts per minute per email) | Attacker can submit 100 login attempts in < 1 minute without response delay |
| Pre-launch security audit certifies no high/critical findings | Any security finding remains open at launch |

## Implementation Specifics

### User Table Schema
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  password_hash BYTEA NOT NULL,  -- bcrypt output (60 bytes)
  role VARCHAR(50) NOT NULL,  -- 'rep', 'manager', 'admin'
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(workspace_id, email)
);
```

### Session/Token Table
```sql
CREATE TABLE refresh_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(64) NOT NULL UNIQUE,  -- SHA256(token)
  issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,
  revoked_at TIMESTAMP,  -- NULL until logout or revocation
  last_refreshed_at TIMESTAMP
);
```

### JWT Claims Structure
```json
{
  "sub": "user_id_uuid",
  "workspace_id": "workspace_id_uuid",
  "role": "rep|manager|admin",
  "exp": 1715942400,  // 15 minutes from issue
  "iat": 1715941500,
  "type": "access"
}
```

### FastAPI-Users Integration
- Use `fastapi-users` library for session/token management
- Custom authenticator: check bcrypt hash on login
- Custom dependency: inject `workspace_id` into all handlers via auth middleware
- Rate limiting: `slowapi` library on POST /auth/login (5 attempts/minute per email)

### OWASP Best Practices Enforced
1. **Password Hashing**: bcrypt with cost factor ≥12 (takes ~100ms per hash, prevents brute force)
2. **Password Reset**: Single-use token with 15-min expiry; requires email verification
3. **Rate Limiting**: 5 login attempts per minute per email; progressive backoff
4. **CSRF Protection**: SameSite=Strict cookie flag; validate CSRF token on state-changing requests
5. **Secure Headers**: HSTS, X-Content-Type-Options, X-Frame-Options, CSP
6. **Audit Logging**: Every login success/failure logged (timestamp, email, IP, user agent, result)

## Migration Path to Managed Auth (Post-MVP)

If compliance requirements later demand Auth0 or similar:

1. Add Auth0 as a secondary OAuth2 provider (alongside hand-rolled)
2. Existing users continue with JWT (no forced migration)
3. New users sign up via Auth0
4. Implement gradual migration: offer users "link Auth0 account" workflow
5. Deprecate hand-rolled auth after 6–12 months; existing users migrate or lose access

No architectural changes needed now; hand-rolled auth is evolutionary stepping stone, not dead-end.

## Remaining Decisions (Not in This ADR)

- **ADR-004**: Cloud platform and deployment (AWS/GCP/Azure choice, containerization)
- **ADR-006**: Email service for password reset notifications (SendGrid, AWS SES, etc.)
- **SSO Integration**: SAML/OpenID Connect (P2+; deferred)
- **MFA**: Phone/authenticator app support (P2+; deferred)
- **Password Policy**: Entropy requirements, expiration rules (team decision during implementation)

## Concern Impact

- **Concern selection**: Reinforces `workspace-isolation`, `gdpr-compliance`, and `security-by-design`.
- **Practice override**: None (this ADR aligns with standard auth practices for SaaS).

## References

- PRD: `crm.prd` (R-1: authenticated multi-user access)
- ADR-001: Backend framework (FastAPI selected; influences auth integration pattern)
- ADR-003: Database (PostgreSQL selected; user credentials stored in application database)
- ADR-201: GDPR deletion strategy (requires direct database access to user tables)
- OWASP: [Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- FastAPI Security: [FastAPI OAuth2 + JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- FastAPI-Users: [GitHub - frankie567/fastapi-users](https://github.com/frankie567/fastapi-users)

## Review Checklist

- [x] Context names a specific problem (workspace isolation + managed vs. hand-rolled trade-off)
- [x] Decision statement is actionable ("we will implement hand-rolled JWT + FastAPI-Users")
- [x] At least two alternatives evaluated (hand-rolled, Auth0/managed, Framework-provided)
- [x] Each alternative has concrete pros/cons
- [x] Selected option's rationale explains why it wins (workspace isolation complexity, GDPR, cost, MVP timeline)
- [x] Consequences include both positive and negative impacts
- [x] Negative consequences have documented mitigations (security audit, code review rules, test strategy)
- [x] Risks are specific with probability/impact assessments and mitigations
- [x] Validation section defines success metrics and review triggers
- [x] Implementation specifics include schema, claims structure, and OWASP best practices
- [x] Migration path to Auth0 is documented (evolutionary, not dead-end)
- [x] ADR is consistent with PRD (R-1) and dependent ADRs (ADR-001, ADR-003, ADR-201)
