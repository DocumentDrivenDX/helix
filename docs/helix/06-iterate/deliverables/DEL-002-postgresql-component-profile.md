---
ddx:
  id: DEL-002
  type: deliverable
  activity: iterate
  kind: deck
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-002-postgresql-component-profile.pptx
  links:
    - id: component-profile-postgresql
      kind: informed_by
---

# PostgreSQL as DepositMatch's system of record

## Brief

- **Audience**: the product and engineering leads who own the system-of-record decision, and the reviewers who sign off on it
- **Occasion**: a 20-minute technical review alongside the system-of-record decision; presented live, then sent as the record
- **Decision or action sought**: the system-of-record choice, recorded in the decision this deck informs
- **Time slot or page budget**: 20 minutes, at most 7 content slides
- **Kind**: deck
- **As of**: 22 September 2026
- **Constraints**: internal only; nothing beyond the public record; every figure carries the record's own label; no owner, date, or grade the record lacks
- **Look**: technical
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
- **Beats and titles** (label headings; the flow's `heading_style` is `label`):

  | # | Beat | Title | Message |
  |---|---|---|---|
  | 1 | introduction | PostgreSQL as DepositMatch's system of record | M2 |
  | 2 | background | Background | M2 |
  | 3 | required-capabilities | Required capabilities | M2 |
  | 4 | what-it-is | What it is | M4 |
  | 5 | capability-alignment | Capability alignment | M1 |
  | 6 | limits | Outside the public record | M1 |
  | 7 | competitive-landscape | Competitive landscape | M3 |
  | 8 | open-questions | Open questions | M1 |
  | 9 | sources | Sources | all |

- **Concept coverage**:

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | The need: the role, the use cases, the goals, and the incumbent | Need, Scope | covered | M2 (slides 1 and 2) |
  | 2 | The seven required capabilities and where each comes from | Required Capabilities | covered | M2 (slide 3) |
  | 3 | What PostgreSQL is, who governs it, adoption, cadence, licence | What It Is | covered | M4 (slide 4) |
  | 4 | What the record shows on each capability, and the verdict | Capability Alignment | covered | M1 (slide 5) |
  | 5 | What is outside the core or left to the hosting | Capability Alignment (other capabilities), Technology and Operations, Pricing and Licensing | covered | M1 (slide 6) |
  | 6 | Every alternative on the same capabilities | Competitive Landscape | covered | M3 (slide 7) |
  | 7 | Every open question and its route | Open Questions | covered | M1 (slide 8) |
  | 8 | How much of the record is corroborated | Confidence | covered | M1 (slide 5 notes) |
  | 9 | Hosting, integrations, security process | Technology and Operations | omitted | angle: none of the seven capabilities turns on them beyond what the alignment carries; the profile carries the table |
  | 10 | The profile's own review checklist | Review Checklist | omitted | audience: authoring hygiene for the record, of no use to the decision |

- **Horizontal-logic test**: label headings; the check does not apply. Read in order the titles give the room the reference's shape: the subject, the background, the criteria, the thing, the record on each criterion, what the record leaves out, the alternatives, what is unsettled.

## Content

### 1. PostgreSQL as DepositMatch's system of record

**Pattern**: title
**Body**:
- The public record on one candidate, measured against the seven capabilities the system-of-record decision requires
**Visual**: kind: none | icon: database. Full-bleed light surface, title in the display face, subtitle naming the role and the decision this informs, database icon in the hero marker
**Notes**: Say the need once, in the profile's words: DepositMatch needs one store for imports, source rows, invoices, deposits, matches, decisions, exceptions, and the audit log, so that every accepted match can be explained at month-end, every exception stays owned, and the pilot ships with one store to operate. Then say this deck is the record behind the decision.
**Sources**: S1, S2

### 2. Background

**Pattern**: claim-evidence
**Body**:
- Pilot firms reconcile in accounting exports, bank reports, and spreadsheets today
- Every accepted match must be explainable at month-end; every exception must stay owned
- The pilot ships with one store to operate
**Visual**: kind: icon-list | items: shield / a review log a firm can explain / evidence, reviewer, and time on every match; users / exceptions that stay owned / no deposit drifts to a spreadsheet; box / one store to operate / imports, matches, decisions, jobs, and audit together | columns: 1. The three goals the profile's Need states, from the product vision, the principles, and the decision record
**Notes**: These are the profile's goals, cited there to the product vision, principles 2 and 5, and the decision record's drivers.
**Sources**: S1, S2

### 3. Required capabilities

**Pattern**: table
**Body**:
- Each capability comes from a project document, named in the last column
**Visual**: kind: table | columns: Capability / Serves / Comes from | rows: An import, its source rows, and the derived rows commit together or not at all, under constraints / a review log a firm can explain / the decision record and the import-integrity standard; Every reviewer decision and correction is recorded with who and when, and history is kept / auditability as usability / the auditability standard and the principles; Access is scoped by role down to the column / protecting customer financial records / the financial-data standard; Encryption in transit by the software and at rest by the hosting / records that stay unreadable if traffic or storage leaks / the financial-data standard and the architecture document; Point-in-time recovery with a recovery point no older than fifteen minutes / the disaster-recovery target / the architecture document; A durable job queue inside the store for several workers / one store to operate / the architecture document and the decision record; A read replica can be added later without a schema change / reports that do not slow imports / the decision record. The seven criteria every later section is measured against
**Notes**: Read the seven rows aloud; every later slide is measured against them. Two nice-to-haves the record also speaks to, semi-structured storage for raw rows and partitioning of import sessions, appear under Outside the public record.
**Sources**: S2

### 4. What it is

**Pattern**: claim-evidence
**Body**:
- An open-source object-relational database, ACID-compliant since 2001
- Community governed, no controlling vendor; the most-used database in the 2025 survey
**Visual**: kind: icon-list | items: database / object-relational, transactional / SQL, ACID, constraints, extensions; users / community governed / committers and a core team, no controlling vendor; chart / most-used database, 2025 survey / 55.6% of respondents; calendar / one major release a year / five years of support each, version 16 until 2028; dollar / no licence fee / use, copy, modify, distribute | columns: 1. Five facts from the record on kind, governance, adoption, cadence, and licence
**Notes**: The record names three built-for use cases: general transactional applications, mixed relational and document data through the JSONB type, and incremental change feeds through built-in logical replication.
**Sources**: S3

### 5. Capability alignment

**Pattern**: table
**Body**:
- All-or-nothing transactions, six constraint types, and trigger functions that record user and time
- Column privileges and row security since 9.5; superusers always bypass, use SET LOCAL behind a pool
- TLS from the software, AES-256 at rest and 5-minute log uploads from the hosting
- SKIP LOCKED serves the job queue; a hot standby serves reports, eventually consistent
**Visual**: kind: table | columns: Capability / What the record shows / Status | rows: Atomic commit and constraints / All-or-nothing transactions, six constraint types including foreign keys / Met; Attribution and history / Trigger functions writing user, time, and the changed row to an audit table / Met; Role scope to the column / Column-level privileges and row security since 9.5, SET LOCAL behind a pool / Met; Encryption / TLS from the software, AES-256 at rest from the hosting / Met; Point-in-time recovery / Continuous archiving, hosting uploads logs every 5 minutes / Met; In-store job queue / SELECT FOR UPDATE SKIP LOCKED for queue tables / Met; Read replica later / Hot standby, read-only and eventually consistent, replicas with a lag metric on the hosting / Met | highlight: 1. Seven rows in the criteria's order, the record's own status word on each
**Notes**: This is the slide the deck exists for. The profile's verdict is Fit. Confidence is Medium: adoption and row-security practice are independently corroborated, and the transaction, constraint, trigger, archiving, and queue claims rest on the maker's documentation alone.
**Sources**: S4, S8

### 6. Outside the public record

**Pattern**: claim-evidence
**Body**:
- Encryption at rest, certifications, and running cost belong to the hosting
- Cross-server sharding is not native; raw CSV rows fit the core JSONB type
**Visual**: kind: icon-list | items: shield / at rest, certifications, cost / the hosting's alone; box / no native cross-server sharding / partitioning within one server; database / raw rows in JSONB / no second store | columns: 1. Three rows the record marks not published, not native, or the operator's
**Notes**: Partitioning of import sessions by range, list, or hash is in core once a retention policy exists.
**Sources**: S5, S6

### 7. Competitive landscape

**Pattern**: table
**Body**:
- MySQL 8.4 has no native row-level security; views plus triggers are the documented workaround
- A document database supports multi-document transactions; its maker cautions against leaning on them
- Amazon RDS adds at-rest encryption, 5-minute log uploads, and a failover standby
**Visual**: kind: table | columns: Candidate / Atomic commit / Role scope to the column / Encryption at rest / Point-in-time recovery / Read replica | rows: PostgreSQL 16 / Met / Met / Met via hosting / Met via hosting / Met; MySQL 8.4 Community / InnoDB adheres to the ACID model / Unmet, no native row-level security / not researched / not researched / not researched; Document database (MongoDB) / Multi-document transactions since 4.0 / not researched / not researched / not researched / not researched; Amazon RDS for PostgreSQL 16 / Inherits / Inherits / AES-256 / Logs every 5 minutes / Read-only replicas with a lag metric | highlight: 1. The profile's landscape on five of the seven capabilities; attribution and queueing read Met for PostgreSQL and not researched for the rest
**Notes**: Each alternative has its own profile with its own record, or none yet; a cell marked not researched is filled there. The decision record's third alternative, an event store with read models, is an architecture pattern with no single component to profile.
**Sources**: S7

### 8. Open questions

**Pattern**: table
**Body**:
- Restore time waits on the quarterly restore drill already scheduled
- Replica lag waits on the decision's review trigger, then a test
- Row-security throughput waits on a test, only if isolation moves into the database
**Visual**: kind: table | columns: Open question / Why it matters / Where the answer comes from | rows: Does a point-in-time restore complete within the four-hour recovery-time target? / The record carries the recovery point and no restore duration / The quarterly restore drill before paid launch; What replica lag would a reporting replica see during an import burst, should reporting load grow? / Decides whether firm-level reports can leave the primary / The decision's review trigger, then a planned test; If per-firm isolation moves into row security, does throughput hold behind the API's connection pool? / Decides whether isolation lives in the database or the application / A planned test, only if row security is adopted. The profile's three open questions with its own routes
**Notes**: Stop here. The source names no owner, date, or duration for any of the three; if the room asks who runs them, that belongs to the decision this deck feeds.
**Sources**: S9

### 9. Sources

**Pattern**: appendix-sources
**Body**:
- Every figure and claim above maps to a section of the PostgreSQL component profile, which cites 33 public sources with access dates
**Visual**: kind: none. Two-column source list in caption size, claim on the left, section on the right
**Notes**: Not presented.
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
- **Gap**: the profile names no owner, date, or duration for the restore drill or the lag spike, so this deck has no next-steps unit and ends on the open questions.

## Render

- **Theme**: deliverables/theme.yml, look `technical` (scripts/render-deck.js)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-002-postgresql-component-profile.pptx, 12 slides from 9 units (the wide tables continue onto a second slide). No PDF and no slide images on this host: LibreOffice is not installed, so the deck was opened and checked structurally; no slide image was produced.
- **Gate**: check-deliverable.py, 0 blocking, 1 warning: the gate's render-image check fires because no slide image exists on this host (see Targets).
- **By hand**: every body proves its heading from the Sources rows; no HELIX vocabulary in titles, bodies, or notes; the candidate-briefing checklist holds (need, criteria, and finding in the title slide's notes and the background slide; the seven criteria with origins; what-it-is before alignment; alignment rows in criteria order with the profile's status words and its Fit verdict in the notes; every alternative on the same criteria with "not researched" cells kept; open questions with the profile's routes and no owner, date, scale, or grade); coverage 10 of 10 groups covered or omitted with a reason, 6 of 6 must-cover items carried, the must-omit items absent from every title and body.
