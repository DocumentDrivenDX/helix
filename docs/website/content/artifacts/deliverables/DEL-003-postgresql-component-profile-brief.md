---
title: "PostgreSQL as DepositMatch's system of record"
slug: DEL-003-postgresql-component-profile-brief
weight: 510
activity: "Iterate"
source: "06-iterate/deliverables/DEL-003-postgresql-component-profile-brief.md"
generated: true
collection: deliverables
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Rendered from this script.** The Markdown below is the document of record; open the rendered file to see the finished deck: [HTML](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/06-iterate/deliverables/assets/DEL-003-postgresql-component-profile-brief.html), [PDF](/artifacts/deliverables/del-003-postgresql-component-profile-brief.pdf).

> **Source identity** (from `06-iterate/deliverables/DEL-003-postgresql-component-profile-brief.md`):

```yaml
ddx:
  id: DEL-003
  type: deliverable
  activity: iterate
  kind: brief
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-003-postgresql-component-profile-brief.html
      - docs/helix/06-iterate/deliverables/assets/DEL-003-postgresql-component-profile-brief.pdf
  links:
    - id: component-profile-postgresql
      kind: informed_by
```

# PostgreSQL as DepositMatch's system of record

## Brief

- **Audience**: the product and engineering leads who own the system-of-record decision, and the reviewers who sign off on it
- **Occasion**: read alongside the system-of-record decision and kept as the reference on this candidate
- **Decision or action sought**: the system-of-record choice, recorded in the decision this brief informs
- **Time slot or page budget**: as many pages as the record needs
- **Kind**: brief
- **As of**: 22 September 2026
- **Constraints**: internal only; nothing beyond the public record; every figure carries the record's own label; no owner, date, or grade the record lacks
- **Look**: classic
- **Scope**: the PostgreSQL component profile (one candidate; the sibling profiles carry the alternatives' own records)
- **Breadth**: deep-dive
- **Angle**: the seven capabilities the system-of-record decision requires
- **Must cover**: the need and the seven required capabilities; what PostgreSQL is and who governs it; what the record shows on each capability; what is outside the core; every alternative on the same capabilities; every open question and its route
- **Must omit**: a recommendation among the candidates; owners, dates, durations, or grades the record does not state
- **Max messages**: 4
- **Takeaway**: on the public record PostgreSQL 16 meets all seven capabilities DepositMatch requires of its system of record, six from its own documentation and encryption at rest from the Amazon RDS hosting; restore time and replica lag under an import burst are the questions only a drill or a test can answer

## Story

- **Flow**: candidate-briefing
- **Takeaway**: on the public record PostgreSQL 16 meets all seven capabilities DepositMatch requires of its system of record, six from its own documentation and encryption at rest from the Amazon RDS hosting; restore time and replica lag under an import burst are the questions only a drill or a test can answer
- **Messages** (ranked by how much each informs the system-of-record decision):
  1. PostgreSQL 16 meets every one of the seven required capabilities on the public record, and the verdict is Fit (evidence: component-profile-postgresql#capability-alignment)
  2. DepositMatch needs one store for imports, source rows, invoices, deposits, matches, decisions, exceptions, and the audit log, so that every accepted match can be explained at month-end and every exception stays owned (evidence: component-profile-postgresql#need, component-profile-postgresql#required-capabilities)
  3. MySQL 8.4 has no native row-level security and a document database trades relational integrity for flexible payloads; Amazon RDS adds the at-rest encryption, five-minute log interval, and failover standby the software cannot supply (evidence: component-profile-postgresql#competitive-landscape)
  4. PostgreSQL is a community-governed object-relational database, the most-used in the 2025 developer survey, with a yearly major release, five years of support, and a no-fee licence (evidence: component-profile-postgresql#what-it-is)
- **Beats and headings** (label headings; the flow's `heading_style` is `label`):

  | # | Beat | Heading | Message |
  |---|---|---|---|
  | 1 | introduction | PostgreSQL as DepositMatch's system of record | M2 |
  | 2 | required-capabilities | Required capabilities | M2 |
  | 3 | what-it-is | What it is | M4 |
  | 4 | capability-alignment | Capability alignment | M1 |
  | 5 | competitive-landscape | Competitive landscape | M3 |
  | 6 | open-questions | Open questions | M1 |
  | 7 | sources | Sources | all |

- **Concept coverage**:

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | The need: the role, the use cases, the goals, and the incumbent | Need, Scope | covered | M2 (introduction) |
  | 2 | The seven required capabilities and where each comes from | Required Capabilities | covered | M2 (section 1) |
  | 3 | What PostgreSQL is, who governs it, adoption, cadence, licence | What It Is | covered | M4 (section 2) |
  | 4 | What the record shows on each capability, and the verdict | Capability Alignment | covered | M1 (section 3) |
  | 5 | What is outside the core or left to the hosting | Capability Alignment (other capabilities), Technology and Operations, Pricing and Licensing | covered | M1 (section 3, folded in as the flow allows when short) |
  | 6 | Every alternative on the same capabilities | Competitive Landscape | covered | M3 (section 4) |
  | 7 | Every open question and its route | Open Questions | covered | M1 (section 5) |
  | 8 | How much of the record is corroborated | Confidence | covered | M1 (section 3 notes) |
  | 9 | Hosting, integrations, security process | Technology and Operations | omitted | angle: none of the seven capabilities turns on them beyond what the alignment carries; the profile carries the table |
  | 10 | The profile's own review checklist | Review Checklist | omitted | audience: authoring hygiene for the record, of no use to the decision |

- **Horizontal-logic test**: label headings; the check does not apply. Read in order the headings give a reader the reference's shape: the need and the finding, the criteria, the thing, the record on each criterion, the alternatives, what is unsettled.

## Content

### 1. PostgreSQL as DepositMatch's system of record

**Pattern**: title
**Body**:
- DepositMatch needs a system of record for its reconciliation workspace: each client firm's imports and source rows, the invoices and deposits they become, match suggestions, reviewer decisions, exceptions, and the audit log behind all of it.
- The goals are a review log a firm can explain at month-end, exceptions that stay owned, and a pilot with one store to operate.
- The store must commit an import and its derived rows atomically under constraints, record who decided what and keep the history, scope access by role to the column, encrypt data in transit and at rest, recover to a point in time within fifteen minutes, run the worker's job queue, and take a read replica later.
- We evaluated PostgreSQL 16 against those seven capabilities on the public record. It meets all seven, six from its own documentation and encryption at rest from the Amazon RDS hosting the architecture names. Restore time and replica lag under an import burst wait on a drill and a test.
**Visual**: kind: none | icon: database. Masthead icon only; no title page in a document
**Notes**: n/a for a document render
**Sources**: S1, S2, S4

### 2. Required capabilities

**Pattern**: table
**Body**:
- Each capability comes from a project document, named in the last column
**Visual**: kind: table | columns: Capability / Serves / Comes from | rows: An import and its derived rows commit together or not at all, under constraints / a review log a firm can explain / the decision record and the import-integrity standard; Every decision and correction is recorded with who and when, and history is kept / auditability as usability / the auditability standard and the principles; Access scoped by role down to the column / protecting financial records / the financial-data standard; Encryption in transit by the software, at rest by the hosting / records unreadable if traffic or storage leaks / the financial-data standard and the architecture document; Point-in-time recovery within fifteen minutes / the disaster-recovery target / the architecture document; A job queue inside the store for several workers / one store to operate / the architecture document and the decision record; A read replica later, without a schema change / reports that do not slow imports / the decision record. The seven criteria every later section is measured against
**Notes**: Two nice-to-haves the record also speaks to, semi-structured storage for raw rows and partitioning of import sessions, appear under Outside the public record.
**Sources**: S2

### 3. What it is

**Pattern**: claim-evidence
**Body**:
- An open-source object-relational database, ACID-compliant since 2001, governed by a community with no controlling vendor, and the most-used database in the 2025 Stack Overflow Developer Survey
**Visual**: kind: icon-list | items: database / object-relational, transactional / SQL, ACID, constraints, extensions; users / community governed / committers and a core team, no controlling vendor; chart / most-used database, 2025 survey / 55.6% of respondents; calendar / one major release a year / five years of support each, version 16 until 2028; dollar / no licence fee / use, copy, modify, distribute | columns: 1. Five facts from the record on kind, governance, adoption, cadence, and licence
**Notes**: The record names three built-for use cases: general transactional applications, mixed relational and document data through the JSONB type, and incremental change feeds through built-in logical replication.
**Sources**: S3

### 4. Capability alignment

**Pattern**: table
**Body**:
- Two documented cautions bear on role scoping: superusers always bypass row security and owners do unless the table forces them, and a tenant set with plain SET persists across a pooled connection where SET LOCAL resets it
- Encryption at rest and the five-minute log interval come from the Amazon RDS hosting the architecture names; every other row is the software's own documentation
- Outside the public record: certifications and running cost belong to the hosting, cross-server sharding is not native, and raw CSV rows fit the core JSONB type
**Visual**: kind: table | columns: Capability / What the record shows / Status | rows: Atomic commit and constraints / All-or-nothing transactions, six constraint types including foreign keys / Met; Attribution and history / Trigger functions writing user, time, and the changed row to an audit table / Met; Role scope to the column / Column-level privileges and row security since 9.5, SET LOCAL behind a pool / Met; Encryption / TLS from the software, AES-256 at rest from the hosting / Met; Point-in-time recovery / Continuous archiving, hosting uploads logs every 5 minutes / Met; In-store job queue / SELECT FOR UPDATE SKIP LOCKED for queue tables / Met; Read replica later / Hot standby, read-only and eventually consistent, replicas with a lag metric on the hosting / Met | highlight: 1. Seven rows in the criteria's order, the record's own status word on each
**Notes**: The profile's verdict is Fit. Confidence is Medium: adoption and row-security practice are independently corroborated, and the transaction, constraint, trigger, archiving, and queue claims rest on the maker's documentation alone.
**Sources**: S4, S5, S6, S8

### 5. Competitive landscape

**Pattern**: table
**Body**:
- MySQL 8.4 has no native row-level security, and the documented alternative is views with WHERE clauses plus triggers; a document database supports multi-document transactions, and its own maker cautions against relying on them in place of schema design
**Visual**: kind: table | columns: Candidate / Atomic commit / Role scope / At rest / PITR / Replica | rows: PostgreSQL 16 / Met / Met / via hosting / via hosting / Met; MySQL 8.4 Community / InnoDB ACID model / Unmet, no native row security / not researched / not researched / not researched; Document database (MongoDB) / Transactions since 4.0 / not researched / not researched / not researched / not researched; Amazon RDS for PostgreSQL 16 / Inherits / Inherits / AES-256 / Logs every 5 minutes / Replicas, lag metric | highlight: 1. The profile's landscape on five of the seven capabilities; attribution and queueing read Met for PostgreSQL and not researched for the rest
**Notes**: Each alternative has its own profile with its own record, or none yet; a cell marked not researched is filled there. The decision record's third alternative, an event store with read models, is an architecture pattern with no single component to profile.
**Sources**: S7

### 6. Open questions

**Pattern**: table
**Body**:
- Each answer has a home: the scheduled restore drill, the decision's review trigger, or a test
**Visual**: kind: table | columns: Open question / Why it matters / Where the answer comes from | rows: Does a point-in-time restore complete within the four-hour recovery-time target? / The record carries the recovery point and no restore duration / The quarterly restore drill before paid launch; What replica lag would a reporting replica see during an import burst, should reporting load grow? / Decides whether firm-level reports can leave the primary / The decision's review trigger, then a planned test; If per-firm isolation moves into row security, does throughput hold behind the API's connection pool? / Decides whether isolation lives in the database or the application / A planned test, only if row security is adopted. The profile's three open questions with its own routes
**Notes**: The source names no owner, date, or duration for any of the three.
**Sources**: S9

### 7. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the PostgreSQL component profile, which cites 33 public sources with access dates
**Visual**: kind: none. Numbered reference list, claim and section
**Notes**: n/a for a document render
**Sources**: S1

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | Scope and Summary: PostgreSQL 16, the system-of-record role, the accepted decision this informs; 33 sources | component-profile-postgresql#scope, component-profile-postgresql#summary, component-profile-postgresql#sources |
| S2 | Need and Required Capabilities: the goals and the seven capabilities with their origins | component-profile-postgresql#need, component-profile-postgresql#required-capabilities |
| S3 | What It Is: object-relational, ACID-compliant since 2001, community governed, 55.6% of 2025 survey respondents, one major a year, five years of support, 16 until 2028, no-fee licence | component-profile-postgresql#what-it-is |
| S4 | Capability Alignment: transactions and constraints; triggers with current_user and now(); column privileges and row security since 9.5 (superusers always bypass, owners unless forced, SET LOCAL); TLS, AES-256 via hosting; archiving, logs every 5 minutes; SKIP LOCKED; hot standby; Met on all seven; verdict Fit | component-profile-postgresql#capability-alignment |
| S5 | Other capabilities: JSONB in core; no cross-server sharding; logical replication since 10 | component-profile-postgresql#capability-alignment |
| S6 | Operations and pricing: certifications and running cost not published | component-profile-postgresql#technology-and-operations, component-profile-postgresql#pricing-and-licensing |
| S7 | Competitive Landscape: MySQL 8.4 (InnoDB ACID, no native row-level security, GPL); MongoDB (transactions since 4.0); Amazon RDS for PostgreSQL 16 (PostgreSQL 13 to 17, AES-256, logs every 5 minutes, replicas with a lag metric, Multi-AZ standby) | component-profile-postgresql#competitive-landscape |
| S8 | Confidence: Medium; design-defining claims rest on the maker alone | component-profile-postgresql#confidence |
| S9 | Open Questions: restore within the 4-hour target, replica lag under an import burst, row-security throughput behind the pool; drill, review trigger, test | component-profile-postgresql#open-questions |

## Assumptions and gaps

- **Assumption**: the audience is the product and engineering leads named as deciders on the system-of-record decision, from the decision record's own header. This run exercises the research process, the mapping, and the renderer end to end against the catalog's example project.
- **Gap**: the profile marks most MySQL and MongoDB landscape cells not researched. The table carries those marks rather than filling them.
- **Gap**: the profile names no owner, date, or duration for the restore drill or the lag spike, so this brief has no next-steps unit and ends on the open questions.

## Render

- **Theme**: deliverables/theme.yml, look `classic` (scripts/render-doc.js --kind brief)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-003-postgresql-component-profile-brief.html and .pdf (headless Chrome print-to-pdf), 4 pages; a brief has no fixed page count. The renderer reported no em dash on the page and drew no placeholder.
- **Gate**: check-deliverable.py, 0 blocking, 0 warnings; label headings, so the horizontal-logic check does not apply.
- **Visual**: every one of the 4 pages was rendered to an image with pdftoppm and inspected: the masthead carries the title and the as-of date, the introduction runs need, criteria, finding in one paragraph, each table renders one row per criterion or alternative with no split cells, the page ends on the open questions and the source list, no overflow or collision.
- **By hand**: every body proves its heading from the Sources rows; every number and status word on the page appears in the profile; no HELIX vocabulary on any page; the candidate-briefing checklist holds; coverage 10 of 10 groups covered or omitted with a reason, 6 of 6 must-cover items carried, the must-omit items absent from every heading and body.
