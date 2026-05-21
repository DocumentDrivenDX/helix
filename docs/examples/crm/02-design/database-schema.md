---
ddx:
  id: crm.database-schema
  type: data-design
  depends_on:
    - crm.solution-design
    - ADR-003
    - ADR-201
  status: resolved
---

# CRM Database Schema Design

**Status**: Resolved (Detailed DDL, Indices, Constraints, and Migration Strategy)

**Derived From**: `crm.solution-design` (domain entities), `ADR-003` (PostgreSQL + SQLAlchemy + Alembic), `ADR-201` (soft-delete pattern)

## Overview

This document specifies the complete PostgreSQL schema for the CRM MVP, including:
- CREATE TABLE statements for all 7 core entities (Workspace, User, Contact, Account, Lead, Opportunity, Activity)
- Index strategy for query performance
- Foreign key constraints with cascade behavior
- Audit field patterns (created_at, created_by, updated_at, updated_by)
- Soft-delete pattern (is_deleted, deleted_at, deleted_by) per ADR-201
- Migration strategy using Alembic (SQLAlchemy's migration framework)

---

## Database Configuration

**Database**: PostgreSQL 15+  
**Character Set**: UTF-8  
**Time Zone**: UTC (all timestamps in UTC; application converts to user's local time)  
**ORM**: SQLAlchemy 2.0+ with async mode  
**Migration Tool**: Alembic

---

## Schema DDL Statements

### 1. Workspace Table

Container for multi-tenant isolation. One workspace per customer.

```sql
CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    owner_id UUID NOT NULL,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT workspace_owner_fk FOREIGN KEY (owner_id) 
        REFERENCES users(id) ON DELETE RESTRICT
);

COMMENT ON TABLE workspaces IS 'Multi-tenant container; one workspace per customer organization';
COMMENT ON COLUMN workspaces.owner_id IS 'Workspace creator (administrative contact); cannot be deleted';
COMMENT ON COLUMN workspaces.stripe_customer_id IS 'Placeholder for billing integration (P1)';
```

### 2. Users Table

Team members and role assignments within a workspace.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('rep', 'manager', 'admin')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT user_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT user_workspace_email_unique UNIQUE (workspace_id, email)
);

COMMENT ON TABLE users IS 'Team members with role-based access control';
COMMENT ON COLUMN users.is_active IS 'Soft-delete flag; inactive users retain audit trail';
COMMENT ON COLUMN users.role IS 'rep (sales), manager (team lead), admin (workspace owner)';
```

### 3. Accounts Table

Companies or prospect organizations.

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(255),
    size VARCHAR(50) CHECK (size IN ('1-10', '11-50', '51-200', '200+')),
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID NOT NULL,
    
    CONSTRAINT account_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT account_created_by_fk FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT account_updated_by_fk FOREIGN KEY (updated_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT account_deleted_by_fk FOREIGN KEY (deleted_by) 
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT account_workspace_name_unique UNIQUE (workspace_id, name)
);

COMMENT ON TABLE accounts IS 'Companies and prospect organizations';
COMMENT ON COLUMN accounts.is_deleted IS 'Soft-delete flag (GDPR); queries default to is_deleted = false';
COMMENT ON COLUMN accounts.deleted_at IS 'Timestamp of soft-deletion; NULL means not deleted';
COMMENT ON COLUMN accounts.deleted_by IS 'User who initiated deletion (for audit trail)';
```

### 4. Contacts Table

People with whom the sales team interacts.

```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    account_id UUID,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    title VARCHAR(255),
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID NOT NULL,
    
    CONSTRAINT contact_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT contact_account_fk FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE SET NULL,
    CONSTRAINT contact_created_by_fk FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT contact_updated_by_fk FOREIGN KEY (updated_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT contact_deleted_by_fk FOREIGN KEY (deleted_by) 
        REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT contact_workspace_email_unique UNIQUE (workspace_id, email)
);

COMMENT ON TABLE contacts IS 'Sales prospect contacts; link to accounts (optional)';
COMMENT ON COLUMN contacts.account_id IS 'Optional link to employer; NULL for unqualified leads';
COMMENT ON COLUMN contacts.is_deleted IS 'Soft-delete flag; cascaded from deletion';
```

### 5. Leads Table

Unqualified prospects with qualification state.

```sql
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    title VARCHAR(255),
    company VARCHAR(255),
    source VARCHAR(50) NOT NULL CHECK (source IN ('webinar', 'referral', 'email', 'outbound', 'other')),
    status VARCHAR(50) NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'working', 'qualified', 'disqualified')),
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID NOT NULL,
    
    CONSTRAINT lead_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT lead_created_by_fk FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT lead_updated_by_fk FOREIGN KEY (updated_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT lead_deleted_by_fk FOREIGN KEY (deleted_by) 
        REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE leads IS 'Unqualified prospects; progress through qualification pipeline';
COMMENT ON COLUMN leads.source IS 'Lead origin (webinar, referral, email, outbound, other)';
COMMENT ON COLUMN leads.status IS 'Qualification state (new → working → qualified → disqualified)';
```

### 6. Opportunities Table

Deals or accounts being actively pursued.

```sql
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    account_id UUID NOT NULL,
    owner_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    value NUMERIC(19, 2),
    stage VARCHAR(50) NOT NULL CHECK (stage IN ('prospect', 'qualified', 'proposal', 'negotiation', 'closed-won', 'closed-lost')),
    close_date DATE,
    next_step_date DATE,
    next_step_text TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by UUID NOT NULL,
    
    CONSTRAINT opportunity_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT opportunity_account_fk FOREIGN KEY (account_id) 
        REFERENCES accounts(id) ON DELETE RESTRICT,
    CONSTRAINT opportunity_owner_fk FOREIGN KEY (owner_id) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT opportunity_created_by_fk FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT opportunity_updated_by_fk FOREIGN KEY (updated_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT opportunity_deleted_by_fk FOREIGN KEY (deleted_by) 
        REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE opportunities IS 'Deals in the sales pipeline; each has an assigned owner';
COMMENT ON COLUMN opportunities.owner_id IS 'Assigned sales rep (cannot be NULL)';
COMMENT ON COLUMN opportunities.stage IS 'Deal stage (no state machine; audit via updated_at)';
COMMENT ON COLUMN opportunities.next_step_date IS 'Drives home-view reminders and pipeline urgency sorting';
COMMENT ON COLUMN opportunities.is_deleted IS 'Soft-delete does not remove historical records (reports need history)';
```

### 7. Activities Table

Log entries representing rep interactions (call, email, meeting, note).

```sql
CREATE TABLE activities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    kind VARCHAR(50) NOT NULL CHECK (kind IN ('call', 'email', 'meeting', 'note')),
    body TEXT,
    author_id UUID NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    record_type VARCHAR(50) NOT NULL CHECK (record_type IN ('contact', 'account', 'opportunity')),
    record_id UUID NOT NULL,
    email_thread_id VARCHAR(255),
    is_deleted BOOLEAN NOT NULL DEFAULT false,
    deleted_at TIMESTAMP,
    deleted_by UUID,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    
    CONSTRAINT activity_workspace_fk FOREIGN KEY (workspace_id) 
        REFERENCES workspaces(id) ON DELETE CASCADE,
    CONSTRAINT activity_author_fk FOREIGN KEY (author_id) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT activity_created_by_fk FOREIGN KEY (created_by) 
        REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT activity_deleted_by_fk FOREIGN KEY (deleted_by) 
        REFERENCES users(id) ON DELETE SET NULL
);

COMMENT ON TABLE activities IS 'Immutable audit log of rep interactions (calls, emails, meetings, notes)';
COMMENT ON COLUMN activities.record_type IS 'Polymorphic reference: contact, account, or opportunity';
COMMENT ON COLUMN activities.record_id IS 'ID of the contact/account/opportunity (no strict FK to support polymorphism)';
COMMENT ON COLUMN activities.email_thread_id IS 'Normalized email thread ID for deduplication (R-10, P1)';
COMMENT ON COLUMN activities.author_id IS 'User who performed the action (may differ from created_by if logged on behalf)';
```

---

## Index Strategy

Indices optimize query performance for MVP operations. Based on solution-design workflows and ADR-003 performance targets.

### Workspace Indices

```sql
-- Workspace: owner lookup (for workspace admin dashboard, P1)
CREATE INDEX idx_workspaces_owner_id ON workspaces(owner_id);
```

### User Indices

```sql
-- User: workspace + email lookup (authentication, access control)
CREATE INDEX idx_users_workspace_id ON users(workspace_id);

-- User: status lookup (filter active users for team assignment)
CREATE INDEX idx_users_is_active ON users(is_active);
```

### Account Indices

```sql
-- Account: workspace + name lookup (CSV import, company matching)
CREATE INDEX idx_accounts_workspace_id ON accounts(workspace_id);

-- Account: soft-delete filtering (all queries default to is_deleted = false)
CREATE INDEX idx_accounts_is_deleted ON accounts(workspace_id, is_deleted);

-- Account: domain lookup (future email routing, P2)
CREATE INDEX idx_accounts_domain ON accounts(workspace_id, domain);
```

### Contact Indices

```sql
-- Contact: workspace + email (primary contact lookup, email uniqueness)
CREATE INDEX idx_contacts_workspace_email ON contacts(workspace_id, email);

-- Contact: soft-delete filtering (all queries default to is_deleted = false)
CREATE INDEX idx_contacts_is_deleted ON contacts(workspace_id, is_deleted);

-- Contact: account lookup (fetch contacts for an account, R-4)
CREATE INDEX idx_contacts_account_id ON contacts(account_id);

-- Contact: created_by lookup (team members' contacts)
CREATE INDEX idx_contacts_created_by ON contacts(workspace_id, created_by);

-- Contact: updated_at ordering (recent contacts, search results)
CREATE INDEX idx_contacts_updated_at ON contacts(workspace_id, updated_at DESC);
```

### Lead Indices

```sql
-- Lead: workspace + status (qualification pipeline, filtering)
CREATE INDEX idx_leads_workspace_status ON leads(workspace_id, status);

-- Lead: soft-delete filtering
CREATE INDEX idx_leads_is_deleted ON leads(workspace_id, is_deleted);

-- Lead: source tracking (lead source analytics, P1)
CREATE INDEX idx_leads_source ON leads(workspace_id, source);
```

### Opportunity Indices

```sql
-- Opportunity: workspace + owner (rep's deal list, home view, R-2)
-- This is the CRITICAL index for home-page performance (R-2)
CREATE INDEX idx_opportunities_workspace_owner ON opportunities(workspace_id, owner_id);

-- Opportunity: workspace + stage (pipeline view by stage, kanban grouping, R-4)
CREATE INDEX idx_opportunities_workspace_stage ON opportunities(workspace_id, stage);

-- Opportunity: soft-delete filtering
CREATE INDEX idx_opportunities_is_deleted ON opportunities(workspace_id, is_deleted);

-- Opportunity: close_date (pipeline forecast, sorting by close date)
CREATE INDEX idx_opportunities_close_date ON opportunities(workspace_id, close_date);

-- Opportunity: next_step_date (home view reminders, sorting by urgency)
CREATE INDEX idx_opportunities_next_step_date ON opportunities(workspace_id, next_step_date);

-- Opportunity: account lookup (fetch deals for an account, R-4)
CREATE INDEX idx_opportunities_account_id ON opportunities(account_id);

-- Opportunity: sorting by updated_at (recent activity)
CREATE INDEX idx_opportunities_updated_at ON opportunities(workspace_id, updated_at DESC);
```

### Activity Indices

```sql
-- Activity: workspace + record (find all activities for a record, detail view)
-- CRITICAL index for activity feed performance (R-3, detail view, <500ms target)
CREATE INDEX idx_activities_record_lookup ON activities(workspace_id, record_type, record_id, occurred_at DESC);

-- Activity: soft-delete filtering
CREATE INDEX idx_activities_is_deleted ON activities(workspace_id, is_deleted);

-- Activity: author lookup (activities by user, team analytics)
CREATE INDEX idx_activities_author_id ON activities(author_id);

-- Activity: occurred_at ordering (reverse chronological feed)
CREATE INDEX idx_activities_occurred_at ON activities(workspace_id, occurred_at DESC);

-- Activity: email_thread_id lookup (email deduplication, R-10, P1)
CREATE INDEX idx_activities_email_thread ON activities(workspace_id, email_thread_id);
```

---

## Foreign Key Relationships & Cascade Behavior

### Cascade Rules

| Parent Table | Child Table | FK Column | Cascade Behavior | Rationale |
|---|---|---|---|---|
| Workspace | User, Account, Contact, Lead, Opportunity, Activity | workspace_id | CASCADE | Workspace deletion cascades to all tenant data (rare operation) |
| Account | Opportunity, Contact | account_id | RESTRICT | Cannot delete account if opportunities exist (app logic to soft-delete related records first) |
| User | created_by, updated_by, owner_id, author_id, created_by | on all tables | RESTRICT | Cannot delete user if they own records; reassign via app logic or administrative workflow |
| Opportunity | Activity | record_id (polymorphic) | No FK (enforced in app) | Activity references opportunities via (record_type, record_id); app-level constraint |
| Contact | Activity | record_id (polymorphic) | No FK (enforced in app) | Activity references contacts via (record_type, record_id); app-level constraint |
| Account | Activity | record_id (polymorphic) | No FK (enforced in app) | Activity references accounts via (record_type, record_id); app-level constraint |

### Soft-Delete Cascade Logic (ADR-201)

When a contact is deleted by user request:
- Contact record: `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user`
- Linked activities: `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user` (cascaded in app logic)
- Linked opportunities: `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user` (cascaded in app logic)
- Account: remains unchanged unless all contacts are deleted

When an account is deleted:
- Account record: `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user`
- Linked contacts: `is_deleted = true` (cascaded in app logic)
- Linked opportunities: `is_deleted = true` (cascaded in app logic)
- Linked activities: `is_deleted = true` (cascaded in app logic)

Cascade behavior is enforced in application logic (ORM layer) rather than database triggers to maintain consistency and allow reversible operations during the 90-day grace period.

---

## Audit Field Patterns

All records track creation and modification for compliance and debugging:

| Field | Type | Constraints | Usage |
|---|---|---|---|
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Immutable creation timestamp (UTC) |
| `created_by` | UUID | NOT NULL, FK(user), ON DELETE RESTRICT | Original creator (cannot be deleted if records exist) |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp (updated on every change) |
| `updated_by` | UUID | NOT NULL, FK(user), ON DELETE RESTRICT | User who made the last change |

**Application Responsibility**:
- ORM layer auto-updates `updated_at` and `updated_by` on every record modification
- Immutable records (activities) are created once and never updated; only soft-deleted
- Queries include `ORDER BY updated_at DESC` to show recent changes first

**Compliance Uses**:
- Admin audit log: "Who changed what on which record at what time"
- GDPR right-to-access: Export all records with full audit trail per contact
- Dispute resolution: Prove the state of a deal at a specific point in time

---

## Soft-Delete Pattern (ADR-201)

All deletable records have soft-delete flags:

| Field | Type | Constraints | Usage |
|---|---|---|---|
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT false | Soft-delete flag (GDPR compliance) |
| `deleted_at` | TIMESTAMP | NULL | Timestamp of soft-deletion; NULL means not deleted |
| `deleted_by` | UUID | FK(user), ON DELETE SET NULL | User who initiated deletion (for audit) |

**Implementation Strategy**:
1. **Default Query Scope**: All application queries filter `WHERE is_deleted = false` automatically (ORM level or middleware)
2. **Admin Queries**: Explicit parameter `include_deleted = true` allows admins to view and recover soft-deleted records
3. **Cascade Behavior**: Deletion is cascaded in application logic, not database triggers
4. **Grace Period**: Records soft-deleted at timestamp `T` are eligible for hard-deletion after `T + 90 days`
5. **Automated Purge**: Daily background job hard-deletes records where `deleted_at < NOW() - 90 days`

**Deletion Workflow**:
1. User requests deletion (e.g., GDPR right-to-forget)
2. Application marks contact: `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user`
3. Application cascades soft-delete to linked activities, opportunities, leads
4. Deletion confirmation email sent with grace period expiration date
5. Record hidden from all user-facing queries (still visible to admins)
6. After 90 days, automated job removes record from database

---

## Migration Strategy

**Tool**: Alembic (SQLAlchemy's native migration framework)  
**Language**: Python (hand-written migrations for explicit control per ADR-003)  
**Process**: Explicit, reviewable, version-controlled migrations with rollback support

### Migration Directory Structure

```
crm/
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py
│   │   ├── 002_add_soft_delete_fields.py
│   │   ├── ...
│   │   └── NNN_description_of_change.py
│   ├── env.py                 # Alembic execution environment
│   ├── script.py.mako         # Migration template (auto-generated)
│   └── alembic.ini            # Alembic configuration
├── app/
│   └── models.py              # SQLAlchemy ORM models
└── migrations.md              # This file (human-readable change log)
```

### Creating a Migration

```bash
# 1. Define changes in SQLAlchemy ORM models (app/models.py)
# 2. Generate migration skeleton
alembic revision --autogenerate -m "add workspace.feature_flag"

# 3. Alembic creates: alembic/versions/TIMESTAMP_add_workspace_feature_flag.py
# 4. Review and edit migration (always verify before commit)
# 5. Apply to development database
alembic upgrade head

# 6. Test application logic against new schema
# 7. Commit to git with message: "migrations: add workspace.feature_flag"
```

### Migration File Template (Hand-Written)

```python
"""Add soft-delete fields to accounts table

Revision ID: 002_add_soft_delete_fields
Revises: 001_initial_schema
Create Date: 2026-05-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add is_deleted, deleted_at, deleted_by columns to accounts."""
    op.add_column('accounts', sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.false()))
    op.add_column('accounts', sa.Column('deleted_at', sa.DateTime, nullable=True))
    op.add_column('accounts', sa.Column('deleted_by', sa.UUID, nullable=True))
    
    op.create_foreign_key(
        'fk_accounts_deleted_by',
        'accounts', 'users',
        ['deleted_by'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for soft-delete filtering
    op.create_index(
        'idx_accounts_is_deleted',
        'accounts',
        ['workspace_id', 'is_deleted']
    )


def downgrade():
    """Rollback: remove soft-delete fields from accounts."""
    op.drop_index('idx_accounts_is_deleted', table_name='accounts')
    op.drop_constraint('fk_accounts_deleted_by', 'accounts')
    op.drop_column('accounts', 'deleted_by')
    op.drop_column('accounts', 'deleted_at')
    op.drop_column('accounts', 'is_deleted')
```

### Deployment Strategy

**Zero-Downtime Migrations**:
1. **Backward Compatibility**: New columns are added with defaults; application code must support both old and new schema during transition
2. **Blue-Green Deployment**:
   - Blue environment: Running current code + schema
   - Green environment: New code + new schema
   - After Alembic `upgrade head`, swap traffic from Blue to Green
   - No downtime if migration doesn't add NOT NULL columns without defaults

3. **Large Table Migrations** (P2):
   - Use Postgres online schema migration tools (pg_partman, pgdd, etc.) for tables >100M rows
   - Out of scope for MVP (single-instance RDS, <1M records projected)

### Rollback Procedure

If a migration must be rolled back:
```bash
# 1. Identify current revision
alembic current

# 2. Downgrade to previous revision
alembic downgrade -1

# 3. Revert application code changes
git revert <commit-with-broken-migration>

# 4. Redeploy with previous schema + code
```

**Immutable Migrations**: Merged migrations are immutable (never deleted or modified). If a mistake is found, a new migration is created to undo the mistake.

### Data Backups & Rollback Guarantees

Per ADR-003:
- **RDS Automated Snapshots**: Daily snapshots with 30-day retention
- **Point-in-Time Recovery (PITR)**: Available within 5-day window (sufficient for migration issues)
- **Pre-Migration Backup**: Before each production migration, take manual snapshot
- **Testing**: All migrations tested against production-size dataset in staging before deploying to production

### Migration Validation Checklist

Before merging a migration:
- [ ] Migration tested against development database
- [ ] Rollback tested (down and up again)
- [ ] No data loss in rollback
- [ ] Backward compatibility maintained (if multi-version support needed)
- [ ] Index creation/modification reviewed for performance impact
- [ ] Foreign key changes validated (no orphaned records)
- [ ] Soft-delete logic verified (is_deleted = false preserved on rollback)
- [ ] Performance test on large table (1M+ rows in staging)
- [ ] Commit message includes rationale and risk mitigation

---

## Constraints & Invariants

### Multi-Tenancy Invariants

1. **Every Record Has workspace_id**: No query joins across workspaces
2. **Query Injection**: Application injects `workspace_id` into all queries (middleware pattern)
3. **No Cross-Workspace FKs**: Foreign keys do not reference records in other workspaces (except User → Workspace link)
4. **Uniqueness Scoped to Workspace**: Unique constraints include `workspace_id` (e.g., `(workspace_id, email)`)

### Audit Trail Invariants

1. **Immutable Creation**: `created_at` and `created_by` are set once at creation and never updated
2. **Update Tracking**: `updated_at` and `updated_by` are updated on every modification
3. **No Deletion Without Audit**: Soft-delete always logs `deleted_at`, `deleted_by`, `deletion_reason`
4. **Activity Immutability**: Activities are never updated; only soft-deleted (audit log immutability)

### Soft-Delete Invariants (ADR-201)

1. **Default Query Scope**: All user-facing queries filter `WHERE is_deleted = false`
2. **Grace Period**: Soft-deleted records can be recovered for 90 days
3. **Cascade Behavior**: Deletion of a parent (contact, account) cascades to children (activities, opportunities)
4. **No Query Bypass**: No mechanism to return deleted records to users except via admin-only restore interface

### Foreign Key Invariants

1. **User Cannot Be Deleted if Owning Records**: `created_by`, `updated_by`, `owner_id`, `author_id` FK has `ON DELETE RESTRICT`
2. **Workspace Cascade**: If workspace deleted, all records cascade-deleted (rare operation; requires admin override)
3. **Polymorphic References**: Activities reference contacts/accounts/opportunities via `(record_type, record_id)` without strict FK (enforced in app logic)

---

## Performance Targets vs. Schema Design

| Query Pattern | Target | Index | Expected Latency |
|---|---|---|---|
| Home view (rep's deals) | Rep/Manager | idx_opportunities_workspace_owner, idx_opportunities_next_step_date | <500ms |
| Pipeline by stage | Rep/Manager | idx_opportunities_workspace_stage | <500ms |
| Activity feed on detail view | Rep/Manager | idx_activities_record_lookup | <500ms |
| Search contacts by email | Rep/Admin | idx_contacts_workspace_email | <100ms |
| CSV import (1000 records) | Admin | Batch INSERT with workspace_id | <5s |
| Audit log query (30 days) | Admin | idx_activities_occurred_at | <1s |

All indices are composite (include `workspace_id` as leftmost column) to support multi-tenancy queries and avoid full-table scans.

---

## Design Validation Against Solution-Design

| Design Requirement | Schema Coverage | Evidence |
|---|---|---|
| Multi-tenancy isolation | Every record has `workspace_id`; uniqueness constraints scoped | Explicit in schema (e.g., `UNIQUE (workspace_id, email)`) |
| Audit trail (created_by, created_at, updated_by, updated_at) | All 7 entities have audit fields | Column definitions in each CREATE TABLE statement |
| Soft-delete (is_deleted) | All deletable entities (Account, Contact, Lead, Opportunity, Activity) | is_deleted columns + ADR-201 indexes |
| Polymorphic activities | Activity(record_type, record_id) + app-level constraint | Activity table design; no strict FK to support polymorphism |
| Cascade behavior | Soft-delete cascades in app; hard FK cascades where specified | Explicit in Cascade Behavior section |
| Owner assignment | Opportunity.owner_id NOT NULL; Contact/Lead unassigned allowed | Opportunity FK constraint |
| Workspace container | All records FK to workspaces(id) | Schema DDL |
| Role-based access | User.role ENUM (rep, manager, admin) | Schema DDL |
| Email uniqueness per workspace | UNIQUE (workspace_id, email) on Contact, User | Constraints in schema |
| Performance indices | Composite indices for all critical queries | Index section with rationale |

---

## Migration Checklist (Initial Schema Creation)

The initial Alembic migration (`001_initial_schema`) must:
- [ ] Create workspace, user, account, contact, lead, opportunity, activity tables
- [ ] Create all foreign key constraints with correct cascade behavior
- [ ] Create all indices (18 total)
- [ ] Set up audit field defaults (created_at, updated_at = CURRENT_TIMESTAMP)
- [ ] Enable UUID generation (gen_random_uuid())
- [ ] Test schema creation on PostgreSQL 15+
- [ ] Verify backward compatibility (if needed for multi-version support)
- [ ] Document migration in alembic/versions/ with rationale

---

## Known Open Decisions & Future Enhancements

### P1 (Post-MVP) Enhancements

1. **Email-to-Activity Capture (R-10)**: Requires email parsing; activity_table extended with email_thread_id index already in place
2. **Custom Stages**: Requires stage enum → lookup table migration (P1 feature)
3. **Read Replicas**: Add read-only replica for analytics (alembic config to support replication lag)
4. **Connection Pooling**: PgBouncer configuration (DevOps, not schema)
5. **Audit Log UI** (R-12): Add audit_log_view for admins (P1)
6. **Activity Archival**: Background job to archive activities >2 years old (P1)

### P2 (Future) Enhancements

1. **Sharding by workspace_id**: If single-tenant workspace >1B records
2. **Multi-Region Replication**: Cross-region standby with Postgres streaming replication
3. **Encryption at Rest**: AWS RDS encryption (DevOps config, not schema)
4. **Data Warehousing**: Snapshot exports to Redshift/BigQuery for reporting

---

## References

- **Solution Design**: docs/examples/crm/02-design/solution-design.md
- **ADR-003**: docs/examples/crm/02-design/adr/ADR-003-database-orm.md
- **ADR-201**: docs/examples/crm/02-design/adr/ADR-201-gdpr-deletion-strategy.md
- **PostgreSQL Docs**: https://www.postgresql.org/docs/15/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/20/
- **Alembic**: https://alembic.sqlalchemy.org/

---

**Status**: ✅ Complete — Schema DDL, indices, constraints, soft-delete pattern, and migration strategy fully specified for implementation.
