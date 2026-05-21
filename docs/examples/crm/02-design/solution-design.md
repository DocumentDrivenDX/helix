---
ddx:
  id: crm.solution-design
  type: solution-design
  depends_on:
    - crm.prd
    - crm.vision
  status: draft
---

# CRM Solution Design

**Scope**: The initial technical and architectural design for the MVP CRM system, derived from `crm.prd` and `crm.vision`.

**Status**: Draft (speculative design from framed PRD; detailed stack decisions deferred to ADRs).

## Executive Summary

The CRM is a multi-tenant, browser-based SaaS application that provides a single shared view of contacts, accounts, leads, opportunities, and activities for small B2B sales teams. The design prioritizes simplicity and day-one usability: one workspace per customer, opinionated pipeline defaults, and activity capture integrated into the daily workflow rather than a separate compliance step.

**Key Architectural Constraints**:
- Browser-based (no native mobile or on-premise deployment)
- Multi-tenant per workspace with strict data isolation
- MVP performance target: sub-second operations for workspaces ≤100k records
- Role-based access control (rep, manager, admin)
- Audit trail for compliance (GDPR right-to-be-forgotten, data deletion)

## Domain Architecture

### Core Entities

The CRM data model is centered around five core record types:

#### 1. Contact
A person with whom the sales team interacts.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable record identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `name` | STRING | NOT NULL, max 255 | Contact's full name |
| `email` | STRING | NOT NULL, unique(workspace_id, email) | Primary communication channel; triggers email-to-activity matching (R-10) |
| `phone` | STRING | optional, max 20 | Phone number |
| `title` | STRING | optional, max 255 | Job title / role |
| `account_id` | UUID | FK(account), optional | Link to employer (NULL for unqualified leads) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Record creation (audit) |
| `created_by` | UUID | FK(user), NOT NULL | Record owner (audit) |
| `updated_at` | TIMESTAMP | NOT NULL, default now() | Last modification (audit) |
| `updated_by` | UUID | FK(user), NOT NULL | Last modifier (audit) |

**Constraints**:
- Email uniqueness is scoped per workspace (different workspaces can have duplicate emails)
- Contact deletion cascades to dependent activities if enforcement is chosen; soft-delete alternative exists (see Data Deletion / GDPR section)

#### 2. Account
A company or prospect organization.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable record identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `name` | STRING | NOT NULL, unique(workspace_id, name) | Company name |
| `domain` | STRING | optional, max 255 | Email domain for routing and matching |
| `industry` | STRING | optional, enum or free-text | Classify segment (e.g., "SaaS", "Manufacturing") |
| `size` | ENUM | optional | {1-10, 11-50, 51-200, 200+} (for later reporting) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Record creation |
| `created_by` | UUID | FK(user), NOT NULL | Record owner |
| `updated_at` | TIMESTAMP | NOT NULL, default now() | Last modification |
| `updated_by` | UUID | FK(user), NOT NULL | Last modifier |

**Constraints**:
- Account name is unique per workspace
- Contacts link to accounts via `contact.account_id` (1:N cardinality)
- Opportunities also link to accounts (1:N cardinality)

#### 3. Lead
An unqualified prospect with contact-like attributes plus qualification state.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable record identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `name` | STRING | NOT NULL, max 255 | Lead name |
| `email` | STRING | NOT NULL | Email address (may collide with contacts; separate records) |
| `phone` | STRING | optional, max 20 | Phone number |
| `title` | STRING | optional, max 255 | Job title |
| `company` | STRING | optional, max 255 | Company name (text, not FK; lead may not match existing account) |
| `source` | ENUM | NOT NULL | {webinar, referral, email, outbound, other} (extensible P1) |
| `status` | ENUM | NOT NULL, default "new" | {new, working, qualified, disqualified} (qualification pipeline) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Record creation |
| `created_by` | UUID | FK(user), NOT NULL | Record owner |
| `updated_at` | TIMESTAMP | NOT NULL, default now() | Last modification |
| `updated_by` | UUID | FK(user), NOT NULL | Last modifier |

**Constraints**:
- Leads progress through qualification (new → working → qualified → disqualified)
- Qualified leads often become contacts linked to accounts; promotion workflow is a future P1

#### 4. Opportunity
A deal or prospect account actively being pursued.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable record identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `name` | STRING | NOT NULL, max 255 | Deal name / opportunity title |
| `account_id` | UUID | FK(account), NOT NULL | Link to the target company |
| `owner_id` | UUID | FK(user), NOT NULL | Assigned sales rep |
| `value` | DECIMAL | optional, scale 2 | Deal value in USD (or configurable currency in P2) |
| `stage` | ENUM | NOT NULL | {prospect, qualified, proposal, negotiation, closed-won, closed-lost} (custom stages in P2) |
| `close_date` | DATE | optional | Expected close date for pipeline forecasting |
| `next_step_date` | DATE | optional | When the next action is due (drives home-view reminders, R-9) |
| `next_step_text` | TEXT | optional, max 500 | Brief description of next action |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Record creation |
| `created_by` | UUID | FK(user), NOT NULL | Record owner |
| `updated_at` | TIMESTAMP | NOT NULL, default now() | Last modification |
| `updated_by` | UUID | FK(user), NOT NULL | Last modifier |

**Constraints**:
- `owner_id` cannot be NULL (every opportunity must have an assigned rep)
- `stage` transitions are unrestricted in MVP (no state-machine enforcement); audit via updated_at
- Closing a deal (stage → closed-won/closed-lost) does not soft-delete the record (reports need historical pipeline)

#### 5. Activity
A log entry representing a rep interaction (call, email, meeting, note).

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable record identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `kind` | ENUM | NOT NULL | {call, email, meeting, note} (extensible in P2) |
| `body` | TEXT | optional | Free-text activity summary (call notes, email subject/thread excerpt, etc.) |
| `author_id` | UUID | FK(user), NOT NULL | User who logged the activity |
| `occurred_at` | TIMESTAMP | NOT NULL | When the activity occurred (may predate the log entry) |
| `record_type` | ENUM | NOT NULL | {contact, account, opportunity} (polymorphic reference) |
| `record_id` | UUID | NOT NULL | The ID of the contact, account, or opportunity being referenced |
| `email_thread_id` | STRING | optional | Normalized email thread identifier (for R-10 email-to-activity deduplication) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | When the activity was logged |
| `created_by` | UUID | FK(user), NOT NULL | User who created this log entry (may differ from author if logged on behalf) |

**Constraints**:
- `(record_type, record_id)` forms a polymorphic foreign key reference (enforced in application or via triggers)
- Activities are immutable after creation (no updates, only soft-delete via archiving in P2)
- `email_thread_id` allows R-10 to deduplicate forwarded emails that match an existing thread

#### 6. User / Team Membership
Users and role assignments within a workspace.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable user identifier |
| `workspace_id` | UUID | FK(workspace), NOT NULL | Multi-tenancy boundary |
| `email` | STRING | NOT NULL, unique(workspace_id, email) | Email used for sign-in |
| `name` | STRING | NOT NULL | Display name |
| `role` | ENUM | NOT NULL | {rep, manager, admin} (see Permissions & Access Control) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Account creation |
| `updated_at` | TIMESTAMP | NOT NULL | Last role/status change |
| `is_active` | BOOLEAN | NOT NULL, default true | Soft-delete flag (inactive users retain audit trail) |

**Constraints**:
- Email is unique per workspace (no cross-workspace sign-in sharing)
- Each workspace has at least one admin (enforced by application logic)
- User deletion (is_active = false) must not orphan records; reassign ownership or maintain audit trail

#### 7. Workspace
Container for multi-tenant isolation.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Immutable workspace identifier |
| `name` | STRING | NOT NULL | Team or organization name |
| `owner_id` | UUID | FK(user), NOT NULL | Workspace creator (administrative contact) |
| `created_at` | TIMESTAMP | NOT NULL, default now() | Workspace creation |
| `stripe_customer_id` | STRING | optional | Placeholder for future billing integration |

**Constraints**:
- Each user belongs to exactly one workspace
- Workspace deletion is irreversible (cascades to all data); not a standard operation

### Entity Relationships

```
Workspace (1)
  ├── User (N) [role: rep, manager, admin]
  ├── Account (N)
  │   ├── Contact (N) [account_id → Account.id]
  │   └── Opportunity (N) [account_id → Account.id, owner_id → User.id]
  ├── Contact (N) [not linked to Account, representing leads or external contacts]
  ├── Lead (N) [independent records, no Account link initially]
  └── Activity (N) [polymorphic: references Contact, Account, or Opportunity]
```

### Data Constraints & Invariants

1. **Multi-tenancy Isolation**: Every record has a `workspace_id` and `(workspace_id, ...)` uniqueness constraints where applicable. No query will ever JOIN across workspaces.
2. **Audit Trail**: All records track `created_at`, `created_by`, `updated_at`, `updated_by`. Activities are the primary audit log for deal progression.
3. **Soft Delete**: User deletion is soft (is_active flag). Contact/Account/Opportunity/Lead deletion in MVP is hard (DROP); soft-delete for GDPR compliance is a P1 enhancement.
4. **Polymorphic References**: Activities use (record_type, record_id) to reference contacts, accounts, or opportunities without a strict FK (enforced in app logic).
5. **Owner Assignment**: Opportunities always have an owner; contacts and leads can be unassigned (NULL created_by is not permitted, but owner can be reassigned).

## Workflow Design

### Rep Workflow

**Daily Driver**: Rep opens the CRM home page and sees their own deals.

1. **Home View (Rep)**
   - Query: `SELECT * FROM opportunities WHERE workspace_id = ? AND owner_id = ? ORDER BY next_step_date ASC NULLS LAST, close_date ASC`
   - Display: Pipeline card for each opportunity, sorted by urgency (next-step due date first)
   - Actions: Click card → detail view; quick-edit fields on card (stage drag-drop, next-step date)

2. **Opportunity Detail View**
   - Show: Account name, stage, value, close date, next-step date/text
   - Show: Linked activities (call, email, meeting, note) reverse-chronological, with author and occurred_at
   - Actions:
     - Add activity (button → modal form with kind, body, occurred_at)
     - Edit next-step date/text
     - Change stage (drag-drop or dropdown)
     - View linked contacts on the account
     - Link new contact to the account (if contact not yet created)

3. **Activity Logging** (inline on detail view)
   - Modal form: kind (radio: call/email/meeting/note), body (text area), occurred_at (date+time)
   - On save: Create activity record with `author_id = current_user`, `created_at = now()`, `occurred_at = form value`
   - Display: Activity appears in the activity feed immediately (reverse-chron order)

4. **Search & Filter**
   - Global search box: query across contact names, account names, email addresses
   - Filter sidebar (future P1): filter by stage, value range, close date range, owner
   - Expected response: <1s for workspaces ≤100k records

### Manager Workflow

**Leadership View**: Manager opens the team pipeline and reviews deals by stage.

1. **Team Pipeline View**
   - Query: `SELECT * FROM opportunities WHERE workspace_id = ? AND owner_id IN (team_rep_ids) GROUP BY stage`
   - Display: Kanban board (columns by stage) with opportunity cards; each card shows name, owner, value, close date, next-step-date-overdue indicator
   - Actions: Click card → detail view (same as rep detail, but not editable by non-owner except admin)

2. **Manager Notes / Coaching**
   - Manager can log an activity on any team opportunity (type = note), creating a record visible to the rep
   - Activity shows: "Coach note from Manager on Date"
   - Rep sees this in the opportunity detail and uses it as guidance

3. **Pipeline Reports** (P1, not MVP)
   - Total pipeline value by stage
   - Deals without a next-step date (at-risk indicator)
   - Win rate by rep (closed-won / total closed)

### Admin Workflow

**Setup & Import**: Admin onboards the team and imports lead lists.

1. **Workspace Setup**
   - Create workspace (name, owner email)
   - Invite users (email, role: rep/manager/admin)
   - Set team composition (which reps report to which managers)

2. **CSV Import** (R-6)
   - Upload CSV file (contacts, accounts, or leads)
   - Column mapping: auto-detect standard headers (Name, Email, Company, Phone, Title, etc.) and allow manual override
   - Preview: Show first 10 rows with mapped columns
   - Validation: Check for duplicates (email uniqueness per workspace), missing required fields
   - Commit: Batch insert; report success count and any errors (row-by-row)
   - For contacts: Optional auto-link to account if company field matches existing account name (case-insensitive)

3. **CSV Export** (R-8)
   - Select record type (contacts, accounts, opportunities, leads, activities)
   - Optional filter (e.g., opportunities where stage = "closed-won")
   - Generate CSV with all fields
   - Download file

4. **User Management**
   - Invite new users (email + role)
   - Deactivate users (soft-delete; their created/updated records retain audit trail)
   - Reassign records from a departing user to another user

5. **Audit Log Access** (R-12, P1)
   - Admin-only view of change history: who changed what field on which record and when
   - Query: `SELECT * FROM audit_log WHERE workspace_id = ? ORDER BY changed_at DESC`
   - Used for compliance, dispute resolution, and understanding data drift

## Permissions & Access Control

### Role-Based Access Control (RBAC)

Three roles with fixed permissions (no per-field or per-object granularity in MVP):

#### Rep
- **Own records**: Full CRUD on contacts, accounts, leads, opportunities they created
- **Team records**: Read-only on team members' opportunities and contacts
- **Activities**: Can log activities on any record (contact, account, opportunity) in the workspace
- **Search**: Can search the entire workspace
- **Import/Export**: Cannot import or export (admin-only)
- **User management**: Cannot manage users or roles (admin-only)

**Rationale**: Reps see their own pipeline and can shadow teammates to learn, but cannot modify someone else's deal.

#### Manager
- **Team records**: Full CRUD on records belonging to team members (contacts, leads, opportunities linked to accounts owned by their team)
- **Team pipeline**: Can view team pipeline by stage and owner
- **Activities**: Can log coaching notes on team opportunities
- **Search**: Can search the entire workspace
- **Import/Export**: Cannot perform import/export directly (escalates to admin)
- **User management**: Cannot manage users or roles (admin-only)

**Rationale**: Managers can guide their team's pipeline but do not have administrative access to user management or data.

#### Admin
- **All records**: Full CRUD on all workspace records (contacts, accounts, leads, opportunities, activities, users)
- **User management**: Invite users, change roles, deactivate users
- **Import/Export**: Full authority to import and export CSV
- **Audit log**: Access to audit trail and change history
- **Workspace settings**: Rename workspace, manage billing integration (placeholder)

**Rationale**: Admins maintain the workspace and enable onboarding/data migration.

### Cross-Workspace Isolation

All queries include `WHERE workspace_id = ?` at the application layer. No user can:
- See records in another workspace
- Access another workspace's user list
- Bypass isolation via API or direct database access

**Implementation**: Middleware checks `req.user.workspace_id` and injects it into all queries; audit any violations as a security incident.

## Reporting & Analytics (MVP / P1 Scope)

### MVP Reporting (In-App Views)
1. **Pipeline by Stage** (rep/manager views): Cards grouped by stage; sum of opportunity value visible
2. **Home View Reminders** (rep view): List of opportunities with next-step dates due today or overdue

### P1 Reporting (Deferred)
1. **Win Rate by Rep**: Closed-won / (closed-won + closed-lost) for a date range
2. **Pipeline Forecast**: Total value by close-date month
3. **Activity Velocity**: Activities logged per rep per week (engagement metric)
4. **Custom Views / Saved Filters**: Save a filter combination for repeat use

### Data Export for External Analysis
- R-8 ensures CSV export is available; analysts can extract to their tools (Tableau, Looker, etc.)
- Audit log export (admin-only) supports compliance audits

## External Integrations

### MVP Scope

#### CSV Import/Export
- **R-6 (Import)**: Upload contacts, accounts, or leads from CSV. Auto-link contacts to accounts by company-name match.
- **R-8 (Export)**: Download any record list as CSV.
- **Implementation**: Standard CSV libraries; validation in application (no server-side file-size limits in MVP, ~1MB per file assumed).

### P1 Scope

#### Email-to-Activity Capture (R-10)
- Workspace gets a unique email address (e.g., `workspace-uuid@crm.example.com`)
- Rep forwards an email to that address; the system extracts the sender email and finds the matching contact
- If a match is found, creates an activity (kind=email, body=email subject + excerpt) on that contact
- **Algorithm**: Match by email sender; if ambiguous, prompt the rep to confirm or manually select the contact
- **Deferred Decision**: Whether to ingest the full email thread or just the excerpt; cloud-provider constraints (cloud file storage) will drive this

#### Webhooks / Read-Only API (R-15)
- **Read-only endpoints**: GET /opportunities, GET /contacts, GET /activities (filtered by workspace_id)
- **Use case**: Integrate with downstream reporting tools, Slack notifications, etc.
- **Auth**: API key per workspace (bearer token)
- **Scope**: No write access (prevents external tools from modifying pipeline)

#### SSO Integration (P2)
- OAuth / OIDC support (Google, Microsoft Entra, others) for workspaces >10 users
- Deferred to P2 to avoid blocking MVP launch

## Scalability & Performance Boundaries

### MVP Performance Targets
- **Search response**: <1s p95 for workspaces ≤100k records
- **Pipeline view render**: <500ms for team of 25 reps with 1k opportunities
- **Activity log load**: <500ms for 100 activities on a single opportunity
- **CSV import commit**: <5s for 1000 contacts + auto-account linking

### Scaling Limits & Deferred Decisions
- **Multi-region replication**: Deferred to P2 (single-region cloud in MVP)
- **Denormalization / caching**: Defer to P2 after production profiling
- **Archived activity pruning**: Deferred to P1 (full-history retention for MVP)

## MVP vs Later Scope

### Explicitly Out of MVP (see crm.prd Non-Goals)
- Marketing automation (email campaigns, drip sequences)
- Customer support ticketing
- Quote-to-cash / billing integration
- AI-generated content, lead scoring, predictive analytics
- Mobile-native apps (mobile-web is acceptable)
- On-premise / self-hosted
- Multi-currency UI
- Heavy customization (custom objects, fields, workflows)
- Multi-region / high-availability
- SSO
- Webhooks / API (P1)
- Email-to-activity capture (P1)
- Saved views / filters (P1)
- Custom pipeline stages (P1)
- Audit log UI (P1; DDx can export)
- Bulk edit (P1)
- Activity reminders (R-9, P1)

### Clearly MVP Scope (P0)
- Core CRUD (contacts, accounts, leads, opportunities, activities)
- Role-based access (rep, manager, admin)
- Pipeline view by stage
- Activity logging
- CSV import/export
- Multi-tenant workspaces
- Audit trail (data tracked, not UI)
- Search

## Known Open Decisions & Escalation Points

The following decisions are open and require human judgment or product approval before implementation begins. They are not hidden assumptions; they are explicitly flagged for ADR resolution or product sign-off.

### Technology Stack (ADR-001, ADR-002, ADR-003)

1. **Backend Language & Framework** (ADR-001)
   - **Options**: Python (Django/FastAPI), Node.js (Express/Fastify), Go (stdlib/Gin), others
   - **Trade-off**: Django brings ORM + batteries-included (auth, admin, migrations), but heavier. FastAPI is lightweight and modern. Go is concurrent and performant. Node.js is familiar to frontend teams.
   - **Decision required**: Who owns this? (CTO / product / founding team)
   - **Impact**: Affects hiring, infrastructure, time-to-launch

2. **Frontend Framework** (ADR-002)
   - **Options**: React, Vue, Svelte, others
   - **Trade-off**: React has largest ecosystem + team familiarity. Vue is lighter. Svelte is elegant but smaller community.
   - **Decision required**: Same as above
   - **Impact**: Frontend developer hiring, component library choices, build tooling

3. **Database & ORM** (ADR-003)
   - **Options**: PostgreSQL (SQLAlchemy, Prisma, Sequelize, etc.), MySQL, others
   - **Trade-off**: PostgreSQL is robust and feature-rich (JSONB, arrays, etc.). MySQL is simple and commodity. NoSQL is a non-starter for relational schema (GDPR audit trail demands relational integrity).
   - **Decision required**: Same as above
   - **Impact**: Schema design, migration tooling, cloud provider selection

4. **Cloud Hosting & Deployment** (ADR-004)
   - **Options**: AWS, Google Cloud, Azure, others
   - **Trade-off**: AWS dominates; GCP is cheaper for compute; Azure integrates with Microsoft enterprise.
   - **Decision required**: CTO / DevOps
   - **Impact**: Infrastructure costs, provider lock-in, multi-region roadmap

5. **Authentication Provider** (ADR-005)
   - **Options**: Email + password (hand-rolled), Auth0, Cognito, others
   - **Trade-off**: Hand-rolled is simple to start but takes on security debt. Auth0 is managed but costs $$.
   - **Decision required**: Security + product
   - **Impact**: Onboarding UX, security posture, costs

### Product Decisions

1. **Pricing Model**
   - **Options**: Per-seat, per-workspace, freemium, usage-based
   - **Trade-off**: Per-seat scales with team size (good for SaaS); freemium lowers barrier to entry but complicates retention metrics.
   - **Impact**: Seat management UX, sales motion, unit economics

2. **Definition of "Team" for Manager Scoping**
   - **Options**: By reporting line, by territory, by custom assignment
   - **Trade-off**: Reporting line is org-aligned; territory is flexible for sales ops.
   - **Decision required**: Product / sales ops
   - **Impact**: Permission checks in queries, manager onboarding complexity

3. **Email-to-Activity Matching Algorithm** (R-10, P1)
   - **Options**: Exact email match, fuzzy name match, manual confirmation
   - **Trade-off**: Exact is fast but misses typos; fuzzy is smarter but slower and error-prone; manual is safe but friction.
   - **Decision required**: Product (after P0 ships, customer feedback)

4. **Data Deletion / GDPR Right-to-Forget Approach**
   - **Options**: Hard delete (cascade / orphan), soft delete (archival), pseudonymization
   - **Trade-off**: Hard delete is clean but breaks audit trail. Soft delete (recommended) preserves history but more complex.
   - **Decision required**: Legal / product
   - **Impact**: Database schema, audit log guarantees, compliance liability

## Design Validation Against PRD

### Acceptance Test Mapping

| PRD Acceptance Test | Design Coverage | Evidence |
|---|---|---|
| R-1 (auth) | Cross-workspace isolation enforced in middleware | Detailed in Permissions section; query injection of workspace_id |
| R-2 (CRUD) | Core entities (Contact, Account, Lead, Opportunity) with full CRUD | Entity definitions + rep/manager/admin role matrix |
| R-3 (activity) | Activity entity + logging workflow in rep workflow | Activity entity design + detail view workflow |
| R-4 (pipeline) | Opportunity + stage; kanban view + card layout in manager workflow | Manager workflow design + entity relationships |
| R-5 (scope) | Owner filtering in queries + role-based visibility | Rep/Manager workflow sections; query patterns specified |
| R-6 (import) | CSV import workflow in admin workflow; column mapping, preview, validation | Admin workflow section details |
| R-7 (search) | Global search across contacts, accounts, opportunities | Rep workflow + search query pattern; <1s target specified |
| R-8 (export) | CSV export in admin workflow; per-record-type options | Admin workflow section; applies to all entity types |

### Non-Functional Requirements

| PRD Non-Goal | Design Stance | Rationale |
|---|---|---|
| Marketing automation | No email campaign entities or workflow | Separate tool; would add complexity to activity logging |
| Support ticketing | No ticket/case entity; activities are sales-only | Different domain; separate product |
| Quote-to-cash | No proposal, quote, or invoice entities | Future P2 integration; would require complex stage flow |
| Mobile-native | Browser + responsive design only | Reduces complexity; mobile-web is sufficient for MVP |
| On-premise | SaaS-only; workspace isolation assumes multi-tenancy | Infrastructure simplification; on-premise is P2+ |
| Multi-currency | USD + opt-in for future currency field (P2) | Simplifies MVP; add after market validation |
| Heavy customization | Fixed schema; custom stages deferred to P2 | Opinionated defaults are core to day-one usability |

## Deferred Decisions & Risks

### ADRs Required Before Implementation

1. **ADR-001**: Backend language and framework selection
2. **ADR-002**: Frontend framework selection
3. **ADR-003**: Database and ORM selection
4. **ADR-004**: Cloud platform and deployment model
5. **ADR-005**: Authentication implementation (hand-rolled vs. managed service)

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Schema changes after launch break imports/exports | Medium | Medium | Define CSV contract in design; version the contract; test import/export round-trips |
| Activity logging becomes performance bottleneck | Low | High | Create index on (record_type, record_id, occurred_at); profile early |
| Reps don't log activities because workflow is friction | High | High | Embed logging in detail view (not a separate form); log email natively (R-10) |
| Manager can't see their team if "team" definition is ambiguous | High | High | Decision required during ADR-005 design; document team-membership query in implementation |
| Workspace isolation bug leaks data across teams | Critical | Critical | Middleware injects workspace_id into all queries; code review for any raw SQL; automated test per workspace_id |
| User deactivation orphans records | Medium | Medium | App logic enforces reassignment before deactivation; audit trail preserved |

---

## Next Steps

1. **Resolve ADRs** (ADR-001 through ADR-005): Specify language, framework, database, cloud, auth
2. **Data Design Detail**: Expand to include schema DDL, indices, migration strategy
3. **API Contract**: Define REST endpoint signatures and request/response schemas
4. **UI/UX Design**: Wireframes and interaction flows for each persona
5. **Security Design**: Detail threat model, encryption, audit logging, GDPR compliance
6. **Deployment & DevOps**: Container strategy, CI/CD pipeline, monitoring
7. **Implementation Beads**: Break design into implementation tasks (one bead per major component)

---

## Review Checklist

- [x] Design is derived from and consistent with crm.prd and crm.vision
- [x] Domain entities cover all PRD requirements (contacts, accounts, leads, opportunities, activities)
- [x] Entity relationships and constraints are explicit (FKs, uniqueness, cardinality)
- [x] Workflows cover primary personas (rep, manager, admin)
- [x] Permissions/access control is role-based and justified
- [x] Integration points are identified (CSV, email-to-activity, API, future extensions)
- [x] MVP vs P1 boundaries are clear (based on PRD P0/P1 separation)
- [x] Open decisions are flagged as ADRs or product escalations (not hidden assumptions)
- [x] Performance targets are specified for MVP scope
- [x] Risks are identified with concrete mitigations
- [x] Design is reviewable by non-specialists (architects, product, engineering leads)
- [x] Each PRD requirement has a design section (not glossed over)
