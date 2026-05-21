---
ddx:
  id: crm.prd
---

# Product Requirements Document

## Summary

A browser-based CRM for small B2B sales teams (2–25 reps) that records
contacts, accounts, leads, opportunities, and activities in one shared system
and surfaces pipeline state to reps and managers. The MVP targets the
day-to-day workflow of a small sales team that today coordinates by
spreadsheet plus chat: list view, detail view, activity logging, and a
pipeline view by stage. Success is measured by adoption depth (≥80% weekly
active reps), pipeline freshness (≥90% of open deals updated in the last
14 days), and time-to-first-value (a team runs its first weekly pipeline
review from the CRM within one week of signup).

This PRD governs the CRM example artifact stack rooted at `crm.vision` and is
the canonical replacement for the provisional spec-id `CRM-001` used by
existing downstream beads.

## Problem and Goals

### Problem

Small B2B sales teams (2–25 reps) keep pipeline state across spreadsheets,
inboxes, and chat threads. The cost is visible in three failure modes:

1. **Manager visibility lag.** A manager cannot see the team's current
   pipeline without asking each rep individually; weekly pipeline reviews
   require 30–60 minutes of pre-meeting reconciliation.
2. **Deal loss at handoff.** When a rep leaves, joins, or shifts territories,
   half the context lives in their inbox; the next rep starts from a
   spreadsheet row with no history.
3. **Stale data.** Pipeline reports are only as fresh as the last spreadsheet
   reconciliation, which happens days or weeks after the deal moved.

Enterprise CRMs (Salesforce, HubSpot, Dynamics) solve this for teams willing
to invest in setup and admin time, but the configuration cost outweighs the
return for a team of 2–25 reps. The result is the long tail of B2B sales
teams that operate at "spreadsheet maturity" indefinitely.

### Goals

1. **Single shared source of truth.** Every rep, manager, and admin sees the
   same contact, account, deal, and activity data — no parallel spreadsheets.
2. **Daily-workflow logging.** Activity capture is part of the rep's
   day-to-day flow, not a separate compliance task done weekly.
3. **Manager-grade pipeline visibility.** A manager can review the team
   pipeline by stage, owner, and next-step status in under 5 minutes without
   leaving the CRM.
4. **Day-one usable.** Defaults work without configuration; new teams produce
   pipeline value in their first session.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Time-to-first-value | First pipeline review from CRM within 7 days of signup | Onboarding telemetry: signup → first pipeline-view session by manager |
| Weekly active reps | ≥ 80% of seats log ≥ 1 activity per 7-day window | Activity-log table + seat list, sampled weekly |
| Pipeline freshness | ≥ 90% of open opportunities updated (any field) in last 14 days | Opportunities table `updated_at` scan |
| Adoption depth | ≥ 70% of customer teams use contact + opportunity + activity within 30 days | Per-team feature-use audit at day 30 |
| Retention | ≥ 85% of month-3 active teams still active in month 6 | Cohort analysis: monthly-active team list |

### Non-Goals

- **Marketing automation** (email campaigns, drip sequences, landing-page
  capture). Out of scope for MVP; teams can integrate dedicated tools.
- **Customer support ticketing.** This is a sales CRM; support cases belong
  in a help-desk product.
- **Quote-to-cash / billing.** No quote generation, contract management, or
  invoice tracking in MVP.
- **AI-generated content, lead scoring, or predictive analytics.** Deferred
  past MVP.
- **Mobile-native apps.** MVP is browser-only (mobile-web is acceptable).
- **On-premise / self-hosted deployment.** SaaS only.
- **Multi-currency, multi-language UI.** USD + English for MVP.
- **Heavy customization** (custom objects, custom fields, custom workflows).
  MVP ships fixed schema; field-level customization deferred.

Deferred items are tracked alongside this PRD; until a parking lot exists in
this example tree, they remain enumerated in the non-goals list above.

## Users and Scope

### Primary Persona: Sales Rep

**Role**: Individual contributor responsible for working a book of accounts
and progressing opportunities through the pipeline.
**Goals**: Find the deals that need attention today; log calls, notes, and
emails without leaving the deal; update next steps as they happen.
**Pain Points**: Spreadsheets get stale, inbox context disappears, manager
asks the same status questions every Monday.

### Secondary Persona: Sales Manager

**Role**: First-line sales manager owning a team of 3–10 reps and the team's
quarterly number.
**Goals**: See the pipeline in aggregate by stage, owner, and close period;
spot deals at risk; coach reps on next steps without dragging answers out of
them.
**Pain Points**: Pre-meeting reconciliation eats hours each week; can't trust
the spreadsheet because reps update it the morning of the review.

### Tertiary Persona: CRM Admin

**Role**: Sales operations contractor or part-time admin (often the founder,
the office manager, or a dedicated ops person at larger end of the segment).
**Goals**: Get reps onboarded; import lead lists; manage user access and seat
assignments; export data for analysis or migration.
**Pain Points**: Existing CRMs assume a full-time admin; this person has 2–5
hours per week for CRM upkeep.

### In Scope (MVP)

- Authenticated multi-user web application (SaaS)
- Core records: contacts, accounts, leads, opportunities, activities, notes
- Pipeline view (kanban by stage; list view by owner / close period)
- Activity logging (call, email, meeting, note) inline on records
- CSV import for contacts, accounts, leads
- Role-based access (rep, manager, admin)
- Basic search and filter across records
- Per-team workspaces with seat-based access

### Out of Scope (see Non-Goals above)

## Requirements

### Must Have (P0)

1. **R-1: Authenticated multi-user access.** Each user signs into a team
   workspace with role-based permissions (rep / manager / admin).
2. **R-2: Core entity CRUD.** Reps can create, read, update, and delete
   contacts, accounts, leads, and opportunities they have access to.
3. **R-3: Activity logging on records.** Reps can log calls, emails,
   meetings, and notes against any contact, account, or opportunity, with
   timestamp, author, and free-text body.
4. **R-4: Pipeline view.** Managers and reps can see opportunities grouped
   by stage, with owner, value, and next-step date visible at the card
   level.
5. **R-5: Owner-scoped and team-scoped views.** Reps see their own pipeline
   by default; managers see their team's pipeline by default; both can
   switch.
6. **R-6: CSV import.** An admin can upload a CSV of contacts, accounts, or
   leads, map columns, preview the result, and commit the import.
7. **R-7: Search.** Users can search records by name, email, or company,
   and results return within 1 second for workspaces under 100k records.
8. **R-8: CSV export.** An admin can export any record list (contacts,
   accounts, leads, opportunities, activities) as CSV.

### Should Have (P1)

1. **R-9: Activity reminders.** Users see open next-step dates due today /
   overdue on their home view.
2. **R-10: Email-to-activity capture.** Forwarding an email to a workspace
   address logs an activity on the matching contact (best-effort match by
   email address).
3. **R-11: Bulk edit.** Admins can bulk-assign owner, change stage, or
   delete on multi-selected records.
4. **R-12: Audit log.** Every record change records who, when, and what
   field changed; viewable by admin.

### Nice to Have (P2)

1. **R-13: Saved views and filters.** Users can save a filtered list view
   for repeat use.
2. **R-14: Custom stages.** A workspace admin can rename the default
   pipeline stages (without changing the stage count).
3. **R-15: Webhooks / API.** Read-only API for integration with downstream
   reporting tools.

## Functional Requirements

**Auth & Workspaces.** Each user belongs to exactly one workspace. Workspaces
are isolated: no cross-workspace data access. Sign-up creates a new workspace
and seats the creator as admin.

**Roles.** Three roles: `rep` (CRUD on own records, read on team records),
`manager` (CRUD on team records), `admin` (CRUD on all workspace records,
plus user management, import/export, audit log access).

**Entities.**
- *Contact*: person with `name`, `email`, `phone`, `title`, `account` (FK).
- *Account*: company with `name`, `domain`, `industry`, `size`.
- *Lead*: unqualified prospect with contact-like fields plus `source` and
  `status` (`new`, `working`, `qualified`, `disqualified`).
- *Opportunity*: deal with `name`, `account` (FK), `owner` (FK to user),
  `value`, `stage` (default: `prospect`, `qualified`, `proposal`,
  `negotiation`, `closed-won`, `closed-lost`), `close_date`,
  `next_step_date`, `next_step_text`.
- *Activity*: log entry with `kind` (`call`, `email`, `meeting`, `note`),
  `body`, `author`, `record_ref` (polymorphic to contact / account /
  opportunity), `occurred_at`.

**Pipeline view.** Default view shows opportunities grouped by stage, sorted
within stage by `close_date`. Drag-and-drop between stages updates `stage`.
Card displays opportunity name, account name, value, owner, next-step date
(with overdue indicator).

**Search.** Single global search box; returns matching contacts, accounts,
opportunities; sub-second p95 for workspaces ≤100k records.

**Import.** CSV upload → column-mapping step → preview (first 10 rows) →
commit. Failed rows reported with reasons; partial-success allowed.

## Acceptance Test Sketches

| Requirement | Scenario | Input | Expected Output |
|---|---|---|---|
| R-1 (auth) | Rep signs in, attempts to read another workspace's contact via direct URL | Valid rep session for workspace A; URL for contact in workspace B | 404 (no cross-workspace leak) |
| R-2 (CRUD) | Rep creates a contact | POST contact with name + email | Contact appears in list view; visible to rep and to manager; not visible to reps in other workspaces |
| R-3 (activity) | Rep logs a call on an opportunity | Activity form with `kind=call`, body, occurred_at | Activity appears in opportunity's activity feed, ordered by occurred_at desc; author = rep |
| R-4 (pipeline) | Manager opens pipeline view | No filter | Opportunities grouped by stage, sorted by close_date within stage; manager sees full team pipeline |
| R-5 (scope) | Rep opens pipeline view | No filter | Rep sees only their own opportunities by default; can switch to "team" view if granted read access |
| R-6 (import) | Admin imports 500-row contact CSV | Valid CSV with `name`, `email`, `company` columns | All 500 contacts created; 0 errors; rows linked to matching accounts where company matches existing account name |
| R-7 (search) | User searches "acme" in 50k-record workspace | Single query string | Results within 1s; includes Acme Corp account + contacts with "acme" in email |
| R-8 (export) | Admin exports opportunities CSV | No filter | CSV with all opportunity fields; row count = total opportunities in workspace |

## Technical Context

Stack decisions are deferred to ADRs in the design activity. The MVP target
shape is:

- **Delivery model**: Browser-based SaaS; multi-tenant per workspace.
- **Frontend**: Modern SPA framework; mobile-web-responsive.
- **Backend**: HTTP/JSON API; relational database for entity storage.
- **Auth**: Email + password to start; SSO deferred to P2.
- **Hosting**: Single-region cloud; multi-region deferred past MVP.

Specific stack selections (language, framework, database, hosting) are
explicitly **Open Questions** below; downstream ADRs will resolve them.

## Constraints, Assumptions, Dependencies

### Constraints

- **Technical**: Browser-based; no native installs. No on-premise option.
- **Business**: MVP must be operable with a small team (no dedicated CRM
  admin assumed at the customer).
- **Legal/Compliance**: GDPR-applicable customer data (EU contacts). Data
  export and deletion (right-to-be-forgotten) requirements apply.

### Assumptions (Explicit — derived from sparse intake)

These assumptions originated from the sparse request `"design a CRM"` and the
parent epic `helix-db7d13a9`'s scope notes. Each is recorded so downstream
work can confirm, override, or refine without re-discovering them.

1. **Audience**: Small B2B sales teams (2–25 reps) — not enterprise; not
   consumer; not transactional / e-commerce CRM.
2. **Primary users**: Sales reps, sales managers, and CRM admins (no
   marketing, no support, no finance personas in MVP).
3. **Core workflows**: Managing contacts/accounts, qualifying leads,
   tracking opportunities, logging activities, reviewing pipeline.
4. **Delivery model**: Browser-based SaaS with authenticated multi-user
   access (no native mobile, no self-hosted).
5. **Geography/language**: USD + English-only for MVP.
6. **Multi-tenancy**: One workspace per customer; strict isolation between
   workspaces.
7. **Pricing model not yet decided** — has no impact on MVP functional
   scope but affects seat-management UX.
8. **Data scale**: Workspaces ≤100k records for MVP performance budgets.
9. **The repo decision is open**: This artifact stack lives in the HELIX
   repo as a planning exercise; whether it migrates to a dedicated CRM repo
   is the subject of bead `helix-5129f35d`.

### Dependencies

- Design-activity ADRs for stack, hosting, and auth (downstream).
- Bead `helix-5129f35d` (CRM repo-scope decision) — does not block frame
  work but governs where subsequent activities land.

## Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| MVP scope creeps to match enterprise CRM expectations | High | High | Non-goals list is enforced as a frame-activity artifact; new requirements must displace existing P0/P1 or move to P2 |
| Defaults don't fit any real customer because we tried to please everyone | Medium | High | Anchor defaults to one well-understood ICP (small B2B sales) and document the choice; resist "configurable for everyone" pull |
| Spreadsheet-using teams don't switch because the cost of change > the cost of bad data | Medium | High | Time-to-first-value metric is a release gate; onboarding flow is treated as P0 |
| Stack choice prematurely commits before design activity | Low | Medium | All stack selection deferred to ADRs; PRD lists only what affects requirements |
| Data export not credible → procurement blocks adoption | Low | High | R-8 (CSV export) is P0; document the export contract before launch |

## Open Questions

- [ ] Pricing model (per-seat vs flat-team vs freemium) — blocks GTM and seat-mgmt UX; ask product/founder.
- [ ] Stack selection: language, framework, database, hosting — blocks design activity; ask architecture (ADRs).
- [ ] SSO provider scope for P2 — blocks auth ADR; ask product.
- [ ] Definition of "team" for manager-scoped views: territory? reporting line? both? — blocks role/permission design; ask product.
- [ ] Email-to-activity matching algorithm specifics (R-10) — blocks P1 design; ask design activity.
- [ ] Migration path from the major incumbent CRMs — out of scope for MVP but informs P1 priorities; revisit at design.

## Success Criteria

The CRM frame is successful when:

1. A design-activity author can produce a solution design from this PRD and the
   vision without re-deriving scope.
2. Downstream beads (currently spec-id `CRM-001`) reference `crm.prd` as
   their canonical governing artifact.
3. The assumptions list above is explicit enough that any reviewer can
   challenge a specific assumption rather than the whole scope.
4. The non-goals list prevents the design from re-importing
   enterprise-CRM scope.

## Review Checklist

- [x] Summary works as a standalone 1-pager
- [x] Problem statement describes specific failure modes with concrete cost
- [x] Goals are outcomes ("manager can review in under 5 minutes"), not activities
- [x] Success metrics have numeric targets and measurement methods
- [x] Non-goals exclude things reasonable people might assume (marketing, support, mobile-native)
- [x] Personas have specific pain points (pre-meeting reconciliation, stale spreadsheets)
- [x] P0 requirements are necessary for launch — removing any one breaks the daily workflow
- [x] P1/P2 are prioritized below P0 (reminders, email capture, audit log are valuable but not blocking)
- [x] Every P0 has an acceptance test sketch
- [x] Requirements trace upward to the vision (single-source-of-truth, daily-workflow, manager-visibility, day-one-usable)
- [x] Functional requirements are testable
- [x] Technical context lists what's known and explicitly defers what's open
- [x] Risks have concrete mitigations
- [x] Open questions name who can answer and what's blocked
- [x] PRD is consistent with `crm.vision`
- [x] Assumptions from sparse intake are listed explicitly
