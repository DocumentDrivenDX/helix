---
title: "Proof of Concept"
linkTitle: "Proof of Concept"
slug: proof-of-concept
activity: "Design"
artifactRole: "supporting"
weight: 16
generated: true
---

## Purpose

Minimal working implementation that validates a risky technical concept
end-to-end before production design or build commitment.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.proof-of-concept.depositmatch
  depends_on:
    - example.feasibility-study.depositmatch
    - example.data-design.depositmatch
    - example.security-requirements.depositmatch
  review:
    self_hash: 1a4e090e57a39c4ba3be9461a32b13865453dab1bd9fc9e6049827da15bd90bf
    deps:
      example.data-design.depositmatch: dc25da87b6288f686dfb11eae276dd334aca0dce4d6cd562c8da70b7f169a7c5
      example.feasibility-study.depositmatch: 356da096953895f8c152a1ac8b880fbc03a3617c1c80516e6f0d3b4033a62c72
      example.security-requirements.depositmatch: 2a1f7efe6e55c1edaa67b76e5a11a49be55e4420d9adc456be5482d417312a43
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Proof of Concept: CSV Import and Evidence-Backed Match Review

**PoC ID**: POC-001 | **Lead**: Engineering Lead | **Time Budget**: 5 days | **Status**: Completed

## Objective

**Primary Question**: Can DepositMatch import representative bank and invoice
CSVs, normalize records by firm/client, suggest matches with visible evidence,
and preserve reviewer decisions without implementing bank feeds or ledger
writeback?

**Success Criteria**:

- **Functional**: WORKING: Import two CSV files, normalize records, generate
  match suggestions, require reviewer approval, and record decisions.
- **Performance**: VALIDATED: Process 500 deposits and 500 invoices for one
  client in under 10 seconds on a local development machine.
- **Integration**: VALIDATED: Source files, normalized records, suggestions,
  review decisions, and exports follow the Data Design relationships.
- **Security**: VALIDATED: Firm/client scoping is enforced in API calls and no
  raw financial identifiers appear in telemetry fixtures.

**In Scope**: CSV parsing, column mapping, normalized records, deterministic
matching rules, evidence display payload, reviewer approval/rejection, and
audit-log write.

**Out of Scope**: Production UI polish, bank-feed integrations, accounting
writeback, ML matching, support tooling, and live customer data.

## Approach

**Architecture Pattern**: Thin vertical workflow from CSV upload through
review decision, using the pilot Data Design and Security Requirements.

**Key Technologies**:

- **Primary**: Local API harness, PostgreSQL-compatible schema, deterministic
  matching service, fixture CSVs.
- **Integration**: Object-storage stub for source files and audit-log table for
  reviewer actions.

## Implementation

### Architecture Overview

```text
CSV fixtures
  -> import validator
  -> normalized deposit/invoice records
  -> deterministic matching service
  -> review queue payload with evidence
  -> reviewer decision endpoint
  -> append-only review_decision audit record
```

### Core Components

#### Import Validator

- **Purpose**: Validate required columns, size limits, encoding, and formula
  injection before normalization.
- **Implementation**: Schema-driven parser with per-client column mapping and
  rejected-row report.

#### Matching Service

- **Purpose**: Suggest candidate deposit-to-invoice matches with evidence.
- **Implementation**: Deterministic rules using amount equality, payer
  reference similarity, and date proximity.

#### Review Decision Endpoint

- **Purpose**: Require reviewer approval or rejection before match state
  changes.
- **Implementation**: Transaction writes suggestion status and immutable
  review_decision record with actor, timestamp, action, and source references.

### Integration Points

| Integration | Type | Status | Notes |
|-------------|------|--------|-------|
| CSV fixtures | File input | Working | Covers two representative bank/invoice export shapes |
| PostgreSQL-compatible schema | Database | Working | Uses pilot entities from Data Design |
| Object-storage stub | File/object store | Partial | Stores source-file metadata only |
| Audit log | Database table | Working | Captures reviewer actions and source refs |

## Results

### Test Scenarios

| Scenario | Result | Status |
|----------|--------|--------|
| Import valid bank and invoice CSVs | 500 deposits and 500 invoices normalized with no rejected rows | Pass |
| Import CSV with missing required column | Batch rejected with field-level error report | Pass |
| Import formula-injection value | Value neutralized before export payload generation | Pass |
| Generate suggested matches | 417 exact-amount/date-window suggestions produced with evidence payload | Pass |
| Reviewer approves match | Suggestion marked accepted and review_decision row appended | Pass |
| Cross-firm read attempt | API returns 403 for records outside firm scope | Pass |
| Performance baseline | 1,000 rows processed in 6.8 seconds locally | Pass |

### Findings

- **FINDING 1**: IMPLEMENTATION: CSV-first import is feasible for the pilot if
  per-client column mapping is explicit.
- **Evidence**: Two fixture formats normalized into the same deposit/invoice
  schema and produced a consistent review queue.
- **Implications**: FEAT-001 should include a mapping step and rejected-row
  report, not a fixed one-format parser.

- **FINDING 2**: VALIDATED: Deterministic matching is sufficient for first-pass
  pilot suggestions.
- **Evidence**: Amount/date/payer rules produced reviewable suggestions with
  evidence payloads and no automatic acceptance.
- **Implications**: ML matching is unnecessary for v1 and should remain parked.

- **FINDING 3**: WORKING: Audit-log writes can be transactionally tied to
  reviewer decisions.
- **Evidence**: Approval/rejection tests wrote suggestion state and
  review_decision rows together.
- **Implications**: Review logs can support the PR-FAQ trust model if the
  production design preserves append-only decision history.

### Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Fixture CSVs are not representative enough | High | Medium | Run Research Plan sample intake before finalizing parser scope |
| Deterministic matching misses split payments | Medium | Medium | Route ambiguous deposits to exception queue; defer split support if needed |
| Import performance changes with production storage | Medium | Low | Add performance test with production-like storage before pilot launch |

## Analysis

**Overall Assessment**: VIABLE WITH CONDITIONS

**Rationale**: The PoC proves the end-to-end CSV-first workflow can work without
bank feeds or ledger writeback. Production design should proceed, but only
after research collects representative sample files and confirms the required
column mapping scope.

## Recommendations

1. Proceed with FEAT-001 CSV Import and Column Mapping -- the PoC validated the
   core path -- Design now.
2. Keep matching deterministic in v1 -- sufficient for reviewable suggestions
   and easier to explain -- Design now.
3. Add rejected-row reports and formula-injection protection to acceptance
   criteria -- both materially affect safety and supportability -- Before build.
4. Keep ML matching, bank feeds, and ledger writeback out of v1 -- not needed to
   validate the trust model -- Parking Lot.

### Follow-up

- [ ] Update FEAT-001 technical design with mapping and rejected-row behavior.
- [ ] Add CSV import security tests for formula injection and malformed files.
- [ ] Add performance test using production-like object storage and database.
- [ ] Confirm sample-file compatibility through the Research Plan before build.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/proofs-of-concept/</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/design/architecture/">Architecture</a><br><a href="../../../artifact-types/design/contract/">Contract</a><br><a href="../../../artifact-types/build/implementation-plan/">Implementation Plan</a><br><a href="../../../artifact-types/design/adr/">ADR</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Proof of Concept Prompt&#10;Use the PoC to validate the smallest risky assumption that matters.&#10;&#10;## Focus&#10;- State the objective and success criteria clearly.&#10;- Keep the approach small and the findings evidence-based.&#10;- End with a decision or recommendation.&#10;- Preserve enough implementation and test evidence for another engineer to reproduce the result.&#10;&#10;## Role Boundary&#10;&#10;Proof of Concept is not a tech spike, feature spec, or production design. It&#10;records a small working implementation that proves or disproves a risky&#10;technical approach. Tech Spike records investigation; PoC records working&#10;evidence.&#10;&#10;## Completion Criteria&#10;- The hypothesis is tested.&#10;- Results are easy to interpret.&#10;- The next step is obvious.&#10;- The production implications and remaining gaps are explicit.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: POC-XXX&#10;---&#10;&#10;# Proof of Concept: {{poc_title}}&#10;&#10;**PoC ID**: {{poc_id}} | **Lead**: {{poc_lead}} | **Time Budget**: {{time_budget}} | **Status**: In Progress | Completed&#10;&#10;## Objective&#10;&#10;**Primary Question**: [What technical concept needs validation?]&#10;&#10;**Success Criteria**:&#10;- **Functional**: [Working implementation demonstrates X]&#10;- **Performance**: [Baseline metric]&#10;- **Integration**: [Systems involved]&#10;&#10;**In Scope**: [Core functionality and key integrations]&#10;**Out of Scope**: [Production hardening and full feature set]&#10;&#10;## Approach&#10;&#10;**Architecture Pattern**: [Approach to demonstrate]&#10;&#10;**Key Technologies**:&#10;- **Primary**: [Core stack]&#10;- **Integration**: [External systems/APIs]&#10;&#10;## Implementation&#10;&#10;### Architecture Overview&#10;```&#10;[Architecture diagram or ASCII representation]&#10;```&#10;&#10;### Core Components&#10;#### [Component Name]&#10;- **Purpose**: [What it does]&#10;- **Implementation**: [Technology and approach]&#10;&#10;### Integration Points&#10;| Integration | Type | Status | Notes |&#10;|-------------|------|--------|--------|&#10;| [System] | [API/DB/Queue] | [Working/Partial/Failed] | [Details] |&#10;&#10;## Results&#10;&#10;### Test Scenarios&#10;| Scenario | Result | Status |&#10;|----------|--------|--------|&#10;| [Core workflow] | [What happened] | Pass/Fail/Partial |&#10;| [Integration] | [What happened] | Pass/Fail/Partial |&#10;| [Performance] | [What happened] | Pass/Fail/Partial |&#10;&#10;### Findings&#10;- **FINDING 1**: [Key discovery]&#10;- **Evidence**: [Concrete proof]&#10;- **Implications**: [What this means]&#10;&#10;### Risks&#10;| Risk | Prob | Impact | Mitigation |&#10;|------|------|--------|------------|&#10;| [Risk] | H/M/L | H/M/L | [Strategy] |&#10;&#10;## Analysis&#10;&#10;**Overall Assessment**: VIABLE | VIABLE WITH CONDITIONS | NOT VIABLE&#10;&#10;**Rationale**: [Evidence-based assessment]&#10;&#10;## Recommendations&#10;1. [Action] -- [Rationale] -- [Timeline]&#10;&#10;### Follow-up&#10;- [ ] Design updates, additional PoCs, ADRs to create&#10;&#10;## Artifacts&#10;&#10;Preserved under `proofs-of-concept/{{poc_id}}/`:&#10;- **Code**: [Working implementation files]&#10;- **Data**: [Test data and fixtures]&#10;- **Evidence**: [Logs, screenshots, benchmark output]</code></pre></details></td></tr>
</tbody>
</table>
