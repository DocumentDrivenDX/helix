---
ddx:
  id: ADR-201
  type: product-decision-record
  status: resolved
  depends_on:
    - crm.solution-design
    - crm.prd
  decided_by: Product Lead + Legal Review
  decision_date: 2026-05-18
---

# ADR-201: GDPR Data Deletion & Right-to-Forget Implementation Strategy

**Status**: Resolved (Soft Delete + 90-day grace period)

**Context**: The CRM stores contact and activity data for EU residents. GDPR Article 17 ("Right to Erasure" / Right to Be Forgotten) requires that data subjects can request deletion of their personal data, except where:
- Legitimate legal interest overrides (e.g., retain contract data for 7 years for tax)
- Record-keeping requirements apply (e.g., audit trail for financial transactions)

The CRM's audit trail (activity logs, contact history) creates a tension: full hard deletion breaks audit integrity; soft deletion (archival) satisfies audit requirements but increases storage/complexity.

**Applicable Constraints from PRD**:
- Non-goal: On-premise deployment (so we control data centers and backup policies)
- Non-goal: Multi-region (simplifies compliance — single data location)
- Constraint: GDPR-applicable customer data (EU contacts)
- Constraint: Data export and deletion required (R-8, implied by right-to-forget)

**Options Under Consideration**:

| Option | Approach | Pros | Cons | Recommended When |
|--------|----------|------|------|-----------------|
| **Hard Delete (Cascade)** | Contact deleted → cascade delete all activities, opportunities linked to that contact | Simple logic; full data removal | Breaks audit trail; potential legal liability if auditors need to prove what happened to a contact | Never (violates audit and compliance expectations) |
| **Soft Delete (Archival)** | Contact marked `is_deleted = true`; queries filter out deleted records; auditors can access full history via admin-only view | Preserves audit trail; supports compliance audits; reversible (restore within grace period) | Storage cost; UI complexity (hide deleted records but allow recovery); GDPR requires "forgotten" data not appear in normal operations | Most CRMs do this; recommended if customer says "we need history for audits" |
| **Pseudonymization** | Contact name, email, phone replaced with hash / UUID; activities retain record of "deleted contact #xyz" | Audit trail intact; personal data removed; compliant with GDPR privacy principle | Complex to implement; doesn't fully satisfy right-to-forget (hash could theoretically be reversed); customer can't recover data | Rare; only if customer insists on permanent removal but audit trail is also critical |
| **Hybrid (Soft + Purge)** | Soft-delete all contact records and activities immediately. After 90-day grace period, hard-delete from database (but retain logs in immutable audit storage) | Right-to-forget satisfied after grace period; audit trail retained in separate immutable log; customer can recover within grace period | Complex; requires separate audit storage; grace period must be documented in terms of service | Best compromise if customer wants erasure guarantees + audit trail |

## RESOLVED DECISION

**Strategy Chosen**: **Soft Delete (Archival)** with 90-day grace period and automated purge

**Rationale**:
- MVP targets small sales teams that don't have sophisticated compliance requirements
- Soft delete is industry standard for SaaS CRMs (Salesforce, HubSpot both soft-delete on request)
- Reversible within grace period (customer can contact support to restore if deletion was a mistake)
- No additional infrastructure beyond `is_deleted` flag + filtered queries
- If a customer later requires hard deletion, a batched purge job can be added in P1

**Decision Details**:
- **Deletion Strategy**: Soft delete (archival) for all personal data
- **Grace Period**: 90 days (customer recovery window)
- **Auto-purge After Grace Period**: Yes, hard-delete after 90 days
- **Immutable Audit Log**: Not required for MVP; database deletion log sufficient
- **Customer-Facing Confirmation UI**: Yes, explicit confirmation modal required before deletion
- **Affected Records**: Contact + all linked activities, opportunities, leads (marked `is_deleted = true`)
- **Non-Affected Records**: Admin audit logs of deletion events (retained indefinitely for compliance proof)

## Schema Implications

### is_deleted Flag Usage
Every record subject to deletion has an `is_deleted BOOLEAN DEFAULT false` flag:
- **Contacts**: `is_deleted` marks the contact as hidden from normal queries
- **Accounts**: If all contacts in an account are deleted, the account should also be soft-deleted (cascading soft-delete)
- **Leads**: `is_deleted` marks lead records as archived; they don't appear in qualification pipeline views
- **Opportunities**: Soft-deleted if the related contact is deleted (cascading soft-delete)
- **Activities**: Soft-deleted if the related contact/opportunity is deleted; retain record for audit

### Filtered Queries (ORM Scope / Middleware)
- **Application Queries**: All user-facing queries automatically filter `WHERE is_deleted = false` via ORM default scope or repository middleware
- **Admin/Audit Queries**: Explicit `include_deleted = true` parameter allows admins to view soft-deleted records for recovery or audit purposes
- **Reports**: By default, exclude deleted records; admin must opt-in to include them

### Cascade Behavior
- **Primary Delete**: When a contact is deleted by user request, `is_deleted = true` for:
  - The contact record itself
  - All activities linked to that contact
  - All opportunities linked to that contact
  - The contact's link to its account (but account itself remains unless all contacts are deleted)
- **Admin Hard-Delete**: After 90-day grace period, automated job runs:
  - Removes contact, account (if empty), leads, opportunities, activities where `is_deleted = true` AND `deleted_at < NOW() - 90 days`
  - Retains deletion audit log entry (timestamp, user who requested, records deleted) indefinitely
  - Removes personally identifiable data (name, email, phone) before hard-delete for defense-in-depth

### Deletion Timestamps
Add to all affected record types:
- `deleted_at TIMESTAMP NULL` — timestamp when record was soft-deleted
- `deleted_by UUID FK(user)` — user who initiated deletion (for audit)
- `deletion_reason STRING` — user-provided reason (e.g., "GDPR Right to Erasure request")

## MVP Implementation Details
1. All records (contacts, accounts, leads, opportunities, activities) have `is_deleted BOOLEAN DEFAULT false` and `deleted_at TIMESTAMP NULL`
2. All app queries filter `WHERE is_deleted = false` automatically (via ORM scope or middleware)
3. Admin can view "deleted records" in a separate admin-only view (for recovery or audit)
4. When a contact is deleted:
   - `is_deleted = true`, `deleted_at = NOW()`, `deleted_by = current_user` for the contact
   - Cascade soft-delete: same for linked activities, opportunities, leads
   - Account remains unless all contacts are deleted
5. **Explicit cascade logic**: If contact A is deleted, its activities, opportunities are immediately soft-deleted (visible only to admins)
6. **Data export** (R-8) excludes deleted records by default; admin can opt-in to include deleted records if needed for audit
7. **Automated purge job**: Background job runs daily; for all records where `deleted_at < NOW() - 90 days`, hard-delete from database and log deletion event to audit table
8. **Deletion confirmation modal**: User must confirm deletion with "I understand this cannot be undone after 90 days" checkbox before initiating deletion

## GDPR Compliance Path

**Right to Erasure (Article 17) Implementation**:
- Customer requests deletion (via account settings or support) → app soft-deletes contact + linked records
- Contact data is immediately hidden from reps, managers, and standard admin queries
- Data is no longer visible in reports, exports, or searches by default
- Admin-only "deleted records view" allows recovery during grace period only

**Proof of Deletion**:
- Customer receives immediate confirmation email with deletion timestamp and transaction ID
- Admin can export deletion audit log showing: deleted contact ID, deletion timestamp, deletion initiator, grace period expiration date
- Admin audit log retention: indefinite (for compliance proof if data regulators inquire)
- If customer needs written proof of deletion before 90 days, Support can issue deletion certificate with audit log entry

**Grace Period (90 Days)**:
- Customer can request data restoration within 90 days via support ticket
- After 90 days, automated job permanently removes all soft-deleted records and PII (except deletion event log)
- Grace period expiration timestamp communicated in deletion confirmation email
- Data cannot be recovered after grace period expires

**Data Portability (Article 20)**:
- R-8 (CSV export) is the portability mechanism
- Customer receives option to export all data (in `is_deleted = false` state only) before confirming deletion
- Customers can request a complete data dump including deleted records within grace period for personal records

## Customer-Facing Terms of Service Language

The following language should be added to the CRM Terms of Service under a new section titled "Data Deletion and Right to Erasure":

### Data Deletion and Right to Erasure

**Your Right to Request Deletion**

In compliance with GDPR Article 17 (Right to Erasure) and similar data protection laws, you may request that we delete any contact record or associated data from our system at any time. To request deletion, you may:
- Use the "Delete" function in the contact record interface, or
- Contact our support team at support@[domain] with the contact name and record ID

**What Happens When You Delete a Record**

When you request deletion:
1. **Immediate Soft Deletion**: The contact record and all linked activities, opportunities, and notes are immediately hidden from your team's view and cannot be accessed through normal search or reporting functions.
2. **Grace Period**: You have 90 days from the deletion date to restore the record if deletion was made in error. During this grace period, you may contact our support team to request restoration.
3. **Permanent Deletion**: After 90 days, the record is permanently deleted from our system and cannot be recovered.

**What Data Is Deleted**

Deletion applies to:
- Contact name, email, phone number, title, and company
- All activities (calls, emails, meetings) linked to the contact
- All opportunities and leads associated with the contact
- Contact history and notes

We retain deletion event logs (timestamp, user who requested deletion, and confirmation of deletion) indefinitely for compliance and fraud prevention purposes.

**What Data Is NOT Deleted**

The following data is retained for legal and compliance reasons:
- Audit logs of the deletion request itself (for GDPR compliance proof)
- Financial transaction records and contract history (if applicable, per 7-year legal hold)
- Backup copies held for disaster recovery (deleted within standard backup retention window of 30 days)

**Proof of Deletion**

Upon deletion, you will receive an email confirmation with:
- Deletion timestamp and transaction ID
- Grace period expiration date (90 days from deletion)
- Link to download deletion audit report for your records

You may request a formal deletion certificate from our support team at any time for compliance documentation.

**Data Export Before Deletion**

Before deleting a contact, you may export all associated data (CRM activity history, notes, communications) in CSV format to retain a personal copy. Use the "Export Records" function in the CRM or contact support for bulk export.

**Questions?**

For questions about data deletion, privacy, or your rights under GDPR and similar laws, please contact our Privacy Team at privacy@[domain].

---

## Downstream Deliverables

### Required Changes
1. **Database Schema (ADR-003)**: Add `is_deleted BOOLEAN DEFAULT false`, `deleted_at TIMESTAMP NULL`, `deleted_by UUID`, `deletion_reason TEXT` to contact, activity, opportunity, lead, and account tables
2. **ORM Configuration**: Implement default scope to filter `WHERE is_deleted = false` on all queries (except explicit admin queries)
3. **Automated Purge Job**: Background scheduler to run daily; purge records where `deleted_at < NOW() - 90 days`
4. **Deletion Confirmation Modal**: UI component with confirmation checkbox and grace period warning
5. **Admin Deleted Records View**: Separate admin-only interface to view, recover, or force-delete soft-deleted records
6. **Deletion Audit Log Table**: Track all deletion events (record ID, type, deletion timestamp, user, reason)
7. **Support Documentation**: Internal runbook for handling data deletion requests and recovery requests
8. **Terms of Service**: Add "Data Deletion and Right to Erasure" section (see Customer-Facing ToS above)
9. **Deletion Confirmation Email**: Automated email template with deletion timestamp, grace period expiration, and recovery instructions

### Testing Requirements
- Unit tests: Verify soft-delete and cascade behavior for each entity
- Integration tests: Verify deleted records are excluded from normal queries but visible to admins
- E2E tests: Verify deletion modal, confirmation email, and grace period messaging
- Compliance test: Verify audit log retention and deletion proof export functionality

### Success Criteria
- All soft-deleted records hidden from rep/manager/user queries (except explicit admin access)
- Deletion confirmation email sent within 1 second of deletion request
- Audit log of deletion event retained indefinitely
- Automated purge job executes daily without errors
- Customer can recover deleted record within 90-day grace period
- After 90 days, deleted records permanently removed (verified with DB query)
