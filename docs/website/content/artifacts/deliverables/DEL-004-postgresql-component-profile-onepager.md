---
title: "PostgreSQL as DepositMatch's system of record"
slug: DEL-004-postgresql-component-profile-onepager
weight: 520
activity: "Iterate"
source: "06-iterate/deliverables/DEL-004-postgresql-component-profile-onepager.md"
generated: true
collection: deliverables
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Rendered from this script.** The Markdown below is the document of record; open the rendered file to see the finished deck: [HTML](https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/06-iterate/deliverables/assets/DEL-004-postgresql-component-profile-onepager.html), [PDF](/artifacts/deliverables/del-004-postgresql-component-profile-onepager.pdf).

> **Source identity** (from `06-iterate/deliverables/DEL-004-postgresql-component-profile-onepager.md`):

```yaml
ddx:
  id: DEL-004
  type: deliverable
  activity: iterate
  kind: one-pager
  status: draft
  authoring:
    home: repo
    export:
      - docs/helix/06-iterate/deliverables/assets/DEL-004-postgresql-component-profile-onepager.html
      - docs/helix/06-iterate/deliverables/assets/DEL-004-postgresql-component-profile-onepager.pdf
  links:
    - id: component-profile-postgresql
      kind: informed_by
```

# PostgreSQL as DepositMatch's system of record

## Brief

- **Audience**: the product and engineering leads who own the system-of-record decision, and the reviewers who sign off on it
- **Occasion**: a leave-behind after the review, for readers who will not open the brief
- **Decision or action sought**: the system-of-record choice, recorded in the decision this page informs
- **Time slot or page budget**: one Letter page
- **Kind**: one-pager
- **As of**: 22 September 2026
- **Constraints**: internal only; nothing beyond the public record; every figure carries the record's own label; no owner, date, or grade the record lacks
- **Look**: classic
- **Scope**: the PostgreSQL component profile (one candidate; the sibling profiles carry the alternatives' own records)
- **Breadth**: survey
- **Angle**: the seven capabilities the system-of-record decision requires
- **Must cover**: the need and the seven required capabilities; what PostgreSQL is; what the record shows on each capability; the alternatives on the same capabilities; every open question and its route
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

- **Concept coverage**:

  | # | Concept group | Authority | Status | Carried by / reason |
  |---|---|---|---|---|
  | 1 | The need: the role, the use cases, the goals | Need | covered | M2 (introduction) |
  | 2 | The seven required capabilities and where each comes from | Required Capabilities | covered | M2 (section 1) |
  | 3 | What PostgreSQL is, who governs it, adoption, cadence, licence | What It Is | covered | M4 (section 2) |
  | 4 | What the record shows on each capability, and the verdict | Capability Alignment | covered | M1 (section 3) |
  | 5 | Every alternative on the same capabilities | Competitive Landscape | covered | M3 (section 4) |
  | 6 | Every open question and its route | Open Questions | covered | M1 (section 5) |
  | 7 | What is outside the core, the operational table, pricing, the incumbent, the source list | Capability Alignment (other capabilities), Technology and Operations, Pricing and Licensing, Scope, Sources | omitted | page budget: one page carries the need, the criteria, the thing, the alignment, the landscape, and the open questions; the brief carries the rest |
  | 8 | The profile's own review checklist | Review Checklist | omitted | audience: authoring hygiene for the record, of no use to the decision |

- **Horizontal-logic test**: label headings; the check does not apply.

## Content

### 1. PostgreSQL as DepositMatch's system of record

**Pattern**: title
**Body**:
- DepositMatch needs one system of record for imports, source rows, invoices, deposits, matches, reviewer decisions, exceptions, and the audit log, so that every accepted match can be explained at month-end and every exception stays owned.
- It must meet the seven capabilities below. On the public record PostgreSQL 16 meets all seven, six on its own and encryption at rest through the Amazon RDS hosting; restore time and replica lag under an import burst wait on a drill and a test.
**Visual**: kind: none | icon: database. Masthead icon only; no title page in a document
**Notes**: n/a for a document render
**Sources**: S1, S2, S4

### 2. Required capabilities

**Pattern**: table
**Body**:
- Each capability comes from a project document, named in the last column
**Visual**: kind: table | columns: Capability / Comes from | rows: Atomic import commit under constraints / decision record, import standard; Attribution and kept history / auditability standard; Access scoped by role to the column / financial-data standard; Encryption in transit and at rest / financial-data standard, architecture document; Point-in-time recovery within fifteen minutes / architecture document; A job queue inside the store / architecture document; A read replica later / decision record. The seven criteria every later section is measured against
**Notes**: The brief carries the goal each capability serves and what the record shows on it.
**Sources**: S2

### 3. What it is

**Pattern**: claim-evidence
**Body**:
- An open-source object-relational database, community governed, the most-used in the 2025 Stack Overflow survey, one major release a year with five years of support, no licence fee
**Visual**: kind: none. One sentence carries governance, adoption, and licence
**Notes**: The brief carries the built-for use cases.
**Sources**: S3

### 4. Capability alignment

**Pattern**: table
**Body**:
- Superusers always bypass row security and owners do unless the table forces it; at-rest encryption and the five-minute log interval come from the hosting
**Visual**: kind: table | columns: Capability / Record / Status | rows: Atomic commit / Transactions, six constraint types / Met; Attribution / Triggers write user, time, row / Met; Role scope / Column privileges, row security / Met; Encryption / TLS, AES-256 via hosting / Met; Point-in-time recovery / Archiving, logs every 5 minutes / Met; Job queue / SKIP LOCKED / Met; Read replica later / Hot standby / Met | highlight: 1. Seven rows, the record's status word on each
**Notes**: The profile's verdict is Fit; its confidence grade is Medium, because the transaction, constraint, trigger, archiving, and queue claims rest on the maker alone.
**Sources**: S4, S8

### 5. Competitive landscape

**Pattern**: table
**Body**:
- MySQL 8.4 has no native row-level security; Amazon RDS adds the at-rest encryption the software cannot supply
**Visual**: kind: table | columns: Candidate / Role scope to the column | rows: PostgreSQL 16 / Met; MySQL 8.4 Community / Unmet, no native row-level security; Document database (MongoDB) / not researched; Amazon RDS for PostgreSQL 16 / Inherits | highlight: 1. The capability the alternatives diverge on most; the brief carries all seven
**Notes**: Each alternative has its own profile, or none yet; a cell marked not researched is filled there.
**Sources**: S7

### 6. Open questions

**Pattern**: claim-evidence
**Body**:
- Restore time waits on the scheduled restore drill, replica lag on the decision's review trigger, and row-security throughput on a test if isolation moves into the database
**Visual**: kind: none. One sentence carries the profile's three open questions and their routes
**Notes**: The source names no owner, date, or duration for any of the three.
**Sources**: S9

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
- **Gap**: the profile names no owner, date, or duration for the restore drill or the lag spike, so this page has no next-steps unit and ends on the open questions.

## Render

- **Theme**: deliverables/theme.yml, look `classic` (scripts/render-doc.js --kind one-pager)
- **Targets**: docs/helix/06-iterate/deliverables/assets/DEL-004-postgresql-component-profile-onepager.html and .pdf (headless Chrome print-to-pdf), 1 page, about 410 words against the 450-word budget. The renderer reported no em dash on the page and drew no placeholder.
- **Gate**: check-deliverable.py, 0 blocking, 0 warnings; label headings, so the horizontal-logic check does not apply.
- **Visual**: the page was rendered to an image with pdftoppm and inspected: the masthead carries the title and the as-of date, the introduction runs need, criteria, finding, the two-column grid balances, no split cells, no overflow.
- **By hand**: every body proves its heading from the Sources rows; every number and status word on the page appears in the profile; no HELIX vocabulary on the page; coverage 8 of 8 groups covered or omitted with a reason, 5 of 5 must-cover items carried, the must-omit items absent from every heading and body.
