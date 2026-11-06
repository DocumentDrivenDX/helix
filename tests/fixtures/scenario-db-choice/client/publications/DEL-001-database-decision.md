---
ddx:
  id: DEL-001
  type: deliverable
  activity: iterate
  kind: brief
  status: draft
  authoring:
    home: repo
    export:
      - publications/DEL-001-database-decision.pdf
  links:
    - id: DB-001
      kind: informed_by
    - id: component-profile-sql-server-reusable
      graph: synaptiq-atlas
      kind: informed_by
      authority: advisory
    - id: component-profile-postgresql-reusable
      graph: synaptiq-atlas
      kind: informed_by
      authority: advisory
---

# Build the new application on PostgreSQL, subject to a vector-search spike

## Brief

- **Audience**: the client's engineering lead
- **Occasion**: send-ahead before the database decision
- **Decision or action sought**: approve PostgreSQL for the new application and fund a vector-search spike
- **Time slot or page budget**: 2 pages
- **Kind**: brief
- **Constraints**: client branding; every figure traces to a pinned source
- **Look**: classic
- **Scope**: DB-001; the two technology briefs it evaluates
- **Breadth**: survey
- **Angle**: licence cost and replica availability
- **Must cover**: recommendation; what separates the options; the open unknown
- **Must omit**: hosting
- **Max messages**: 3
- **Takeaway**: PostgreSQL avoids new per-core licences and gives a readable replica, if a vector spike passes

## Story

- **Flow**: proposal
- **Takeaway**: PostgreSQL avoids new per-core licences and gives a readable replica, if a vector spike passes
- **Messages**:
  1. Licence cost and readable replicas separate the options (evidence: DB-001#evaluation)
  2. SQL Server's vector index is still preview; PostgreSQL vector search is unresearched (evidence: DB-001#risks-and-unknowns)
  3. Approve PostgreSQL on the condition of a vector spike (evidence: DB-001#recommendation)
- **Horizontal-logic test**: pass. The titles move from the answer to what separates the options, then to the open unknown and the ask.

## Content

### 1. Licence cost and readable replicas separate the options

**Pattern**: claim-evidence
**Body**:
- SQL Server licenses per core; Standard edition limits a basic availability group to two replicas with no readable secondary
- PostgreSQL has no software licence cost and includes hot standby with read-only queries
**Visual**: kind: table | columns: Criterion / SQL Server / PostgreSQL | rows: Licence / per core / none; Readable replica / Enterprise only / built in | highlight: none. Two-row comparison from DB-001 evaluation
**Notes**: The 2025 SQL Server list price is not published on a maker page; the 2022 figures are labelled as such.
**Sources**: S1, S2

### 2. The vector criterion is open on both sides

**Pattern**: claim-evidence
**Body**:
- SQL Server 2025 has a generally available vector type; the vector index is preview
- The PostgreSQL brief does not cover vector search
**Visual**: kind: none | icon: search. Text only
**Notes**: This is the condition on the recommendation.
**Sources**: S3

### 3. Approve PostgreSQL on the condition of a vector spike

**Pattern**: claim-evidence
**Body**:
- Recommendation: PostgreSQL for the new application
- Condition: a vector-search spike meets recall and latency needs
**Visual**: kind: none | icon: check. Text only
**Notes**: The recommendation reverses if the spike fails.
**Sources**: S3

## Sources

| Id | Claim or figure | Governing artifact and section |
|---|---|---|
| S1 | Basic availability group limits; per-core licensing | component-profile-sql-server-reusable#capabilities-and-limits |
| S2 | Hot standby; no software cost | component-profile-postgresql-reusable#capabilities-and-limits |
| S3 | Recommendation and condition | DB-001#recommendation |

## Assumptions and gaps

- **Assumption**: the client's requirements in DB-001 Context are current; the engineering lead confirms.
- **Gap**: PostgreSQL vector search is not in the PostgreSQL brief; handled as the stated condition.

## Render

- **Theme**: deliverables/theme.yml
- **Targets**: publications/DEL-001-database-decision.pdf, not produced in this fixture
- **Gate**: not run in this fixture; the scenario test checks pinning and reproducibility only
