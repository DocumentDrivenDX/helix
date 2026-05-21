---
ddx:
  id: example.solution-design.depositmatch.csv-import
  depends_on:
    - example.feature-specification.depositmatch.csv-import
    - example.architecture.depositmatch
    - example.adr.depositmatch.postgresql-system-of-record
    - example.contract.depositmatch.import-session-api
  review:
    self_hash: 4d5a2bf5c6b05affdcf7ecc35497aae9f7bb64007e45b62f2a87b42a6914aa00
    deps:
      example.adr.depositmatch.postgresql-system-of-record: d068dcadcfb1b7b4cfa6842e63e078f711128e78d5c2dd7e1666506a7c59d9ad
      example.architecture.depositmatch: 64b7297158175ff16812e401fe093f7624b5ba70b11265a7a4bdf324e50a6bff
      example.contract.depositmatch.import-session-api: 0f6f77f7dca5d1d05590440459fe958f9620857ed3968839e537655dce27cd04
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Solution Design

**Feature**: FEAT-001 - CSV Import and Column Mapping | **Artifact**:
`docs/helix/02-design/solution-designs/SD-001-csv-import-column-mapping.md`

## Scope

- Feature-level design for creating draft import sessions, uploading CSV files,
  mapping columns, validating rows, summarizing import results, and preserving
  traceability fields.
- Uses the DepositMatch Architecture, ADR-001 PostgreSQL system-of-record
  decision, API-001 import-session contract, and active concerns
  `csv-import-integrity`, `financial-data-security`, and
  `reviewer-auditability`.
- Does not design match suggestion scoring or accounting platform integrations.
- Story-level upload, mapping, and validation implementation details belong in
  TD-001, TD-002, and TD-003.

## Requirements Mapping

### Functional Requirements

| Requirement | Technical Capability | Component | Priority |
|-------------|----------------------|-----------|----------|
| UP-01 accept bank and invoice CSV files | Multipart upload endpoint creates a draft import session and stores encrypted originals | Upload Controller, Source File Store | P0 |
| UP-02 reject non-CSV files | File-type guard before parsing or storage | Upload Controller | P0 |
| MAP-01 require amount/date/identifier mappings | Mapping schema with required semantic fields per source type | Mapping Service | P0 |
| MAP-02 save confirmed mappings for reuse | Per-client mapping profiles keyed by source type | Mapping Service, PostgreSQL | P0 |
| VAL-01 reject missing required mapped columns | Header validation before row import | CSV Validation Service | P0 |
| VAL-02 reject invalid rows | Row validator for amount, date, and duplicate source identifiers | CSV Validation Service | P0 |
| SUM-01 show import summary | Import summary read model from validation results | Import Commit Service, API Service | P0 |
| TRC-01 preserve source metadata | Source row table stores file, row number, identifier, normalized amount/date | Import Commit Service, PostgreSQL | P0 |

### NFR Impact on Architecture

| NFR | Requirement | Architectural Impact | Design Decision |
|-----|-------------|----------------------|-----------------|
| Performance | 10,000 rows summarized in under 5 seconds | Validation must stream parse and batch database writes | Parse in API process, commit accepted rows in one transaction after summary confirmation |
| Security | No raw financial rows in analytics/logs | Logging must use event metadata only | Structured logging allowlist; raw rows only in encrypted S3/PostgreSQL |
| Reliability | Import confirmation atomic | Partial accepted-row commits are not allowed | Transaction boundary in Import Commit Service |

## Solution Approaches

### Approach 1: Parse and validate synchronously in the API

**Description**: The API parses uploaded CSV files, validates mappings and rows,
stores results, and returns an import summary.
**Pros**: Simple user feedback, fewer moving parts, easy pilot operation.
**Cons**: API task must handle peak import CPU and memory.
**Evaluation**: Selected for v1 because pilot imports are bounded at 10,000
rows and the feature needs immediate reviewer feedback.

### Approach 2: Store files and validate asynchronously in the worker

**Description**: The API stores files and enqueues validation work for the
Matching Worker.
**Pros**: Keeps upload endpoint fast and isolates parsing load.
**Cons**: Adds polling or notifications before mapping review; complicates
error recovery for a P0 workflow.
**Evaluation**: Rejected for v1. Revisit if import files exceed 10,000 rows or
validation regularly exceeds 5 seconds.

**Selected Approach**: Synchronous API validation with transactional commit
after reviewer confirmation.

**Architecture/ADR impact**: No change. This design applies the current
Architecture and ADR-001.

## Domain Model

```mermaid
erDiagram
    CLIENT ||--o{ IMPORT_SESSION : owns
    IMPORT_SESSION ||--|{ IMPORT_FILE : contains
    IMPORT_SESSION ||--o{ SOURCE_ROW : accepts
    CLIENT ||--o{ MAPPING_PROFILE : saves
    IMPORT_FILE ||--o{ VALIDATION_RESULT : produces
    SOURCE_ROW ||--o{ MATCH_EVIDENCE : supports
```

### Business Rules

1. **Required source pair**: A draft import session is not ready for mapping
   until it has one bank CSV and one invoice CSV.
2. **Mapping before import**: Accepted rows cannot be committed until required
   mappings exist for amount, date, and source identifier.
3. **Validation before matching**: Match suggestions cannot be created until the
   reviewer confirms an import summary.
4. **Traceability preservation**: Every accepted row must retain file identity,
   row number, source identifier, normalized amount, and normalized date.

## System Decomposition

### Component: Upload Controller

- **Purpose**: Receive CSV files and create draft import sessions.
- **Responsibilities**: Authenticate and authorize the client, enforce file
  type and size rules, store encrypted originals, return API-001 responses.
- **Requirements Addressed**: UP-01, UP-02.
- **Interfaces**: HTTP API `POST /v1/clients/{clientId}/import-sessions`; S3
  SDK; PostgreSQL.
- **Owned by TDs**: TD-001 upload endpoint and UI integration.

### Component: Mapping Service

- **Purpose**: Manage source-specific column mappings.
- **Responsibilities**: Load saved mappings, validate required semantic fields,
  save confirmed mappings by client and source type.
- **Requirements Addressed**: MAP-01, MAP-02, MAP-03.
- **Interfaces**: API Service internal module; PostgreSQL mapping tables.
- **Owned by TDs**: TD-002 mapping review workflow.

### Component: CSV Validation Service

- **Purpose**: Validate headers and rows before import confirmation.
- **Responsibilities**: Detect missing mapped columns, invalid amounts, invalid
  dates, duplicate source identifiers, and row-level rejection reasons.
- **Requirements Addressed**: VAL-01, VAL-02, VAL-03.
- **Interfaces**: API Service internal module; parsed CSV stream.
- **Owned by TDs**: TD-003 validation rules and test fixtures.

### Component: Import Commit Service

- **Purpose**: Commit accepted rows and import summary atomically.
- **Responsibilities**: Persist accepted source rows, rejection reasons,
  summary counts, and traceability fields.
- **Requirements Addressed**: SUM-01, SUM-02, TRC-01, TRC-02.
- **Interfaces**: PostgreSQL transaction; Evidence Service read model.
- **Owned by TDs**: TD-004 confirmation and source-row persistence.

### Component Interactions

```mermaid
graph TD
    Upload[Upload Controller] --> Mapping[Mapping Service]
    Mapping --> Validation[CSV Validation Service]
    Validation --> Summary[Import Summary]
    Summary --> Commit[Import Commit Service]
    Commit --> Rows[(Source Rows)]
    Commit --> Evidence[Evidence Service]
```

## Technology Rationale

Only feature-specific choices are listed here. System-wide choices remain in
Architecture and ADR-001.

| Layer | Choice | Why | Alternatives Rejected |
|-------|--------|-----|----------------------|
| CSV parser | Papa Parse | Already named in PRD technical context; supports browser and Node parsing patterns | Custom parser rejected because CSV edge cases are easy to mishandle |
| Validation model | Semantic field mapping per source type | Lets client-specific CSV headers map to stable DepositMatch concepts | Hard-coded column names rejected because pilot exports vary |
| Job trigger | PostgreSQL import confirmation state | Keeps matching jobs consistent with accepted rows | Separate queue rejected by ADR-001 for v1 simplicity |

## Traceability

| Requirement ID | Component | Design Element | Test Strategy |
|----------------|-----------|----------------|---------------|
| UP-01 | Upload Controller | Multipart import-session creation | API contract tests for API-001 and US-001 story tests |
| UP-02 | Upload Controller | File-type guard | API negative test with PDF upload |
| MAP-01 | Mapping Service | Required semantic mapping validation | Mapping unit tests with missing amount/date/identifier |
| VAL-02 | CSV Validation Service | Row-level amount/date/duplicate checks | Fixture-based validation tests |
| SUM-02 | Import Commit Service | Matching not enqueued before summary confirmation | Integration test around import status transition |
| TRC-02 | Evidence Service | Source-row evidence projection | Story test for match evidence display |

### Gaps

- [ ] Retention period for uploaded CSV originals needs legal/owner decision.
  Mitigation: keep retention configurable and create an ADR before paid launch.

## Concern Alignment

- **Concerns used**: `csv-import-integrity`, `financial-data-security`,
  `reviewer-auditability`, `a11y-wcag-aa`.
- **Constraints honored**: Required mapping and validation protect CSV
  integrity; raw financial rows stay out of analytics/logs; evidence fields are
  preserved for audit.
- **ADRs referenced**: ADR-001 PostgreSQL as system of record.
- **Departures**: None.

## Constraints & Assumptions

- **Constraints**: v1 supports CSV import only; no bank feed or accounting API
  sync.
- **Assumptions**: Pilot firm files fit within the 10 MB per-file limit and
  10,000-row validation target.
- **Dependencies**: API-001 import-session contract; encrypted S3 storage;
  PostgreSQL 16.

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| CSV layouts vary more than expected | H | M | Keep mappings semantic and per-client; collect pilot fixtures before launch. |
| Synchronous validation exceeds 5 seconds | M | M | Benchmark fixtures in CI; move validation to worker only if target fails repeatedly. |
| Reviewers distrust rejected-row explanations | M | H | Include row number, field, and plain-language reason for every rejection. |
