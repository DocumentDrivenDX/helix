---
title: "Feature Specification"
linkTitle: "Feature Specification"
slug: feature-specification
activity: "Frame"
artifactRole: "core"
weight: 13
generated: true
---

## Purpose

A feature spec is the **feature-level authority for behavior and boundaries**.
It translates PRD requirements into precise feature behavior, functional areas,
non-functional expectations, edge cases, and feature-specific success measures.
Acceptance criteria belong to user stories (ADR-009) and are not defined here.

It sits between the PRD (which defines product scope) and user stories (which
define vertical slices through the feature). The feature spec owns feature
behavior. User stories own user journeys. Solution and technical designs own
how the behavior will be built.

## Authoring guidance

- **Future state before current pain** — describe the desired user-visible
  outcome before optimizing around today's broken surface. The problem statement
  explains why the change is needed; it should not be the only organizing frame.
- **Scope, not solution** — describe what the feature must do, not how to
  build it. Implementation details belong in design docs.
- **Behavior, not journey** — specify feature behavior and boundaries.
  Put end-to-end user flow narrative and acceptance criteria in user stories.
- **One feature, one capability** — a feature spec covers exactly one capability
  (≈ one PRD subsystem). If it covers two, split it; apply the Decomposition test
  below to decide. A functional *area* is a sub-part of one capability, not a
  second capability.
- **Functional areas before requirements** — when a feature spans multiple
  surfaces, stages, or domain objects *within the one capability*, name those

_Additional guidance continues in the full prompt below._

<details>
<summary>Quality checklist from the prompt</summary>

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] Overview links to a specific PRD requirement
- [ ] Ideal Future State is present for broad product-surface, workflow, IA, or documentation features
- [ ] Functional Areas is present when the feature spans multiple surfaces, workflows, user modes, or domain objects
- [ ] Similar domain objects are separated before requirements are written
- [ ] Functional requirements are grouped by area when a flat list would mix unrelated scopes
- [ ] Every functional requirement is testable
- [ ] Non-functional requirements have specific numeric targets
- [ ] User stories are referenced by ID (not duplicated inline)
- [ ] Dependencies name specific feature IDs and external systems
- [ ] Exact API/CLI/event/schema/config/telemetry/adapter surface is linked to a Contract, not defined inline
- [ ] No `[NEEDS CLARIFICATION]` markers remain

### Warning

- [ ] Problem statement quantifies the pain
- [ ] At least one feature-level edge case documented
- [ ] Success metrics are feature-specific (not product-level)
- [ ] Out of scope excludes something plausible

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.feature-specification.depositmatch.csv-import
  depends_on:
    - example.product-vision.depositmatch
    - example.prd.depositmatch
    - example.principles.depositmatch
    - example.concerns.depositmatch
  review:
    self_hash: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
    deps:
      example.concerns.depositmatch: 34738dd02d95489bcc3c00b5be15b630ae9fb15ab4f99f45d0ec1ecd1d3f1c6e
      example.prd.depositmatch: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
      example.principles.depositmatch: bb37a1addd5c152f068dd5c416b6a4ae217847242d0d1b7f9e64406b671de0ed
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---

# Feature Specification: FEAT-001 - CSV Import and Column Mapping

**Feature ID**: FEAT-001
**Status**: Specified
**Priority**: P0
**Owner**: Product and Engineering

## Overview

CSV Import and Column Mapping implements the PRD requirement to import bank
deposit CSV files and invoice export CSV files for a client. The feature gives
reviewers a dependable way to bring source data into DepositMatch while
preserving the source-row identity needed for matching evidence and audit logs.

## Ideal Future State

Maya uploads bank and invoice exports for a client, confirms the saved column
mapping, and sees a clean import summary before matching begins. If a file is
ambiguous or missing required columns, DepositMatch explains the issue before
any rows enter the review queue. Source rows remain traceable through matching,
exceptions, reports, and corrections.

## Problem Statement

- **Current situation**: Reviewers reconcile deposits from bank exports,
  invoice exports, spreadsheets, and email notes.
- **Pain points**: CSV layouts differ by client and system. A silent mapping
  error can make match suggestions look plausible while pointing to the wrong
  source row.
- **Desired outcome**: Reviewers can import valid files quickly and trust that
  invalid files stop before they pollute the matching workflow.

## Functional Areas

| Area | User question or job | Feature responsibility |
|------|----------------------|------------------------|
| Upload | Can I provide the bank and invoice files for this client? | Accept CSV files and associate them with one client and import session. |
| Mapping | Does DepositMatch understand the columns in these files? | Require mappings for amount, date, identifier, and source-specific optional fields. |
| Validation | Are these files safe to import? | Detect missing columns, duplicate source identifiers, malformed dates, and invalid amounts before import. |
| Import Summary | What happened during import? | Show accepted rows, rejected rows, warnings, and saved mappings. |
| Traceability | Can every later match point back to source data? | Preserve file identity, row number, source identifier, and normalized values. |

## Requirements

### Functional Requirements by Area

#### Upload

UP-01. The system must accept one bank deposit CSV and one invoice export CSV
for a selected client and import session.

UP-02. The system must reject non-CSV files before parsing.

#### Mapping

MAP-01. The system must require mappings for amount, date, and source
identifier in both bank and invoice files.

MAP-02. The system must save a confirmed mapping for reuse on the next import
for the same client and source type.

MAP-03. The system must let the reviewer adjust a saved mapping before rows
are imported.

#### Validation

VAL-01. The system must reject an import when required mapped columns are
missing from either file.

VAL-02. The system must reject rows with invalid amounts, invalid dates, or
duplicate source identifiers within the same file.

VAL-03. The system must show rejected rows with the source row number and a
plain-language reason.

#### Import Summary

SUM-01. The system must show accepted row count, rejected row count, warning
count, and saved mapping status before the reviewer proceeds to matching.

SUM-02. The system must not create match suggestions until the reviewer
confirms the import summary.

#### Traceability

TRC-01. The system must preserve source file name, import session, row number,
source identifier, normalized amount, and normalized date for every accepted
deposit and invoice row.

TRC-02. The system must make preserved source-row fields available to match
evidence, exception records, and reconciliation exports.

### Acceptance Criteria

| Requirement | Scenario | Given | When | Then |
|-------------|----------|-------|------|------|
| UP-01 | Valid bank and invoice exports | Maya selected Acme Dental and chose two valid CSV files | She uploads both files | DepositMatch opens mapping review for the import session |
| MAP-02 | Reused client mapping | Acme Dental has a saved bank mapping | Maya uploads the same source type next week | The saved mapping is preselected and editable before import |
| VAL-01 | Missing required column | The invoice file lacks a mapped amount column | Maya confirms the mapping | The import is rejected before rows are accepted |
| VAL-03 | Row-level validation error | A bank row has `12OO.00` in the amount column | Maya validates the file | The row is rejected with its source row number and reason |
| SUM-02 | Reviewer has not confirmed summary | Validation completed with accepted and rejected rows | Matching would otherwise begin | No match suggestions are created until Maya confirms the summary |
| TRC-02 | Accepted row appears in evidence | A deposit row was accepted during import | Maya later reviews a suggested match | Match evidence includes the source file, row number, amount, date, and identifier |

### Non-Functional Requirements

- **Performance**: Validate and summarize files totaling 10,000 rows in under
  5 seconds on the supported production environment.
- **Security**: Do not send raw financial row values to analytics or logging
  systems.
- **Reliability**: Import confirmation must be atomic; either all accepted rows
  for the session are recorded with traceability fields or none are.
- **Usability**: All validation errors must identify the file, row number, and
  field in plain language.

## User Stories

- [US-001 - Upload CSV files for a client](../user-stories/US-001-upload-csv-files.md)
- [US-002 - Confirm or adjust column mappings](../user-stories/US-002-confirm-column-mappings.md)
- [US-003 - Review import validation results](../user-stories/US-003-review-import-validation.md)

## Edge Cases and Error Handling

- **Duplicate source identifiers**: Reject duplicate identifiers within the
  same file and show each duplicate row.
- **Locale-specific amounts**: Reject ambiguous amount formats unless the
  mapping defines the decimal and thousands separators.
- **Partial upload**: If only one file is uploaded, keep the import session in
  draft and do not validate matching readiness.
- **Saved mapping drift**: If a saved mapping references a missing column,
  require the reviewer to repair the mapping before import.

## Success Metrics

- 95% of valid pilot-firm CSV import sessions reach the import summary without
  support intervention.
- 100% of accepted rows used in match evidence include file name, row number,
  source identifier, amount, and date.
- Fewer than 1% of import sessions require mapping correction after reviewer
  confirmation.

## Constraints and Assumptions

- CSV import is the only v1 ingestion path.
- Pilot firms can provide sample bank and invoice exports before launch.
- Source files may contain customer financial data and must follow the
  `financial-data-security` concern.

## Dependencies

- **Other features**: FEAT-002 Match Suggestion Review depends on accepted
  deposits and invoices from this feature.
- **External services**: None for v1.
- **PRD requirements**: P0-1 import CSV files; P0-4 preserve match evidence;
  P0-5 create exceptions for unmatched deposits.

## Out of Scope

- Bank feed integration.
- Accounting platform API sync.
- Automatic correction of malformed CSV values.
- Matching deposits to invoices before the reviewer confirms import summary.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/features/</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/frame/user-stories/">User Stories</a><br><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/design/contract/">Contract</a><br><a href="../../../artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md"><code>docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Feature Specification Generation Prompt&#10;&#10;Create a feature specification that is precise enough to support design,&#10;user story creation, and test planning. The feature spec owns FR-IDs,&#10;functional areas, and the decomposition test — acceptance criteria live in&#10;user-stories (see ADR-009) and must not be restated here.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/01-frame/features/FEAT-NNN-&lt;name&gt;.md`&#10;&#10;## Purpose&#10;&#10;A feature spec is the **feature-level authority for behavior and boundaries**.&#10;It translates PRD requirements into precise feature behavior, functional areas,&#10;non-functional expectations, edge cases, and feature-specific success measures.&#10;Acceptance criteria belong to user stories (ADR-009) and are not defined here.&#10;&#10;It sits between the PRD (which defines product scope) and user stories (which&#10;define vertical slices through the feature). The feature spec owns feature&#10;behavior. User stories own user journeys. Solution and technical designs own&#10;how the behavior will be built.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/ibm-requirements-management.md` grounds traceable,&#10;  prioritized, verifiable requirements.&#10;- `docs/resources/cucumber-executable-specifications.md` grounds concrete&#10;  examples as readable acceptance specifications without prescribing&#10;  implementation or tooling.&#10;&#10;## Active Concerns&#10;&#10;For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared&#10;`## Artifact Impact` (from `workflows/concerns/&lt;name&gt;/concern.md`) to THIS feature spec — realize the&#10;FEAT-level obligations it names (usage-metering -&gt; which actions are billable; multi-tenancy -&gt; tenant-scoped ACs). A selected concern whose Artifact Impact names FEAT&#10;but leaves no trace here is drift (reconcile-alignment Concern-&gt;Artifact Realization check).&#10;&#10;## Key Principles&#10;&#10;- **Future state before current pain** — describe the desired user-visible&#10;  outcome before optimizing around today&#x27;s broken surface. The problem statement&#10;  explains why the change is needed; it should not be the only organizing frame.&#10;- **Scope, not solution** — describe what the feature must do, not how to&#10;  build it. Implementation details belong in design docs.&#10;- **Behavior, not journey** — specify feature behavior and boundaries.&#10;  Put end-to-end user flow narrative and acceptance criteria in user stories.&#10;- **One feature, one capability** — a feature spec covers exactly one capability&#10;  (≈ one PRD subsystem). If it covers two, split it; apply the Decomposition test&#10;  below to decide. A functional *area* is a sub-part of one capability, not a&#10;  second capability.&#10;- **Functional areas before requirements** — when a feature spans multiple&#10;  surfaces, stages, or domain objects *within the one capability*, name those&#10;  areas before writing requirements and group requirements by area instead of&#10;  producing one flat list. (Areas are subordinate parts of one capability — if an&#10;  &quot;area&quot; would pass the Decomposition test as its own capability, it is a separate&#10;  feature, not an area.)&#10;- **Separate similar domain objects** — if readers might confuse two things,&#10;  define them separately before requirements. For example, &quot;Artifacts&quot; are&#10;  project-specific instances; &quot;Artifact Types&quot; are reusable methodology&#10;  definitions.&#10;- **Stories by reference** — list user story IDs, don&#x27;t duplicate story&#10;  content. Stories are separate files with their own lifecycle.&#10;- **Testable requirements** — every functional requirement should be&#10;  verifiable. If you can&#x27;t describe how to test it, it&#x27;s too vague.&#10;- **Leave unknowns explicit** — use Open Questions at the bottom rather than&#10;  inventing detail you don&#x27;t have.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Product goals, personas, launch priority, or product-level metrics | PRD |&#10;| Feature behavior, boundaries, and edge cases | Feature Specification |&#10;| A vertical user journey through one or more feature requirements, with acceptance criteria | User Story |&#10;| Exact API/CLI/event/schema surface, commands, flags, fields, payloads, status codes, error semantics, or compatibility rules | Contract |&#10;| Feature-level technical approach, component choices, domain/data model, interface usage, or implementation approach | Solution/Technical Design |&#10;| Detailed test cases, fixtures, or automation strategy | Test Plan or Story Test Plan |&#10;| Build sequencing and work slices | Implementation Plan |&#10;&#10;## Decomposition — is it a FEAT or a functional area?&#10;&#10;The brief decomposes into features at one granularity: **one feature per&#10;capability**, anchored to the PRD&#x27;s `### Subsystem:` groupings (~one subsystem →&#10;one `FEAT-NNN`). Use these **layered tests** to place a candidate:&#10;&#10;1. **Primary — ship / cut / metric.** A candidate is its own **feature** if all&#10;   hold:&#10;   - **Ship/cut:** it could be removed or deferred **without making another&#10;     *named* capability incoherent** (it stands alone in the parking-lot).&#10;   - **Metric:** it carries its own **feature-level product/user outcome** as a&#10;     success metric — not a local counter (a button click or a row count is not a&#10;     feature metric).&#10;   If a candidate fails these — it cannot stand alone and has no outcome of its&#10;   own — it is a **functional area** within a feature, not a feature.&#10;2. **Tie-breaker — bounded context.** When ship/cut is genuinely ambiguous, split&#10;   on bounded context / aggregate root: one feature per bounded context; areas are&#10;   views/stages over the *same* aggregate.&#10;&#10;**Anchor:** the PRD names the subsystems; each maps to ~one feature. A&#10;multi-subsystem brief that produces a single mega-feature, or that produces zero&#10;feature specs (PRD → stories directly), has skipped this tier — reconcile-alignment&#10;flags both. A deliberately cross-subsystem feature (the workflow that spans them&#10;*is* the feature) is allowed, but must say so explicitly in the template&#x27;s&#10;**Cross-Subsystem Rationale** field (the &quot;Covered PRD Subsystem(s)&quot; /&#10;&quot;Covered PRD Requirements&quot; fields hold the subsystem names and FR IDs).&#10;## Section-by-Section Guidance&#10;&#10;### Overview&#10;Connect this feature to a specific PRD requirement. &quot;This feature implements&#10;PRD P0-3&quot; is better than &quot;This feature improves the user experience.&quot;&#10;&#10;### Ideal Future State&#10;Describe the target state in user-visible terms. A good future state answers:&#10;&#10;- What can the user understand, decide, or accomplish?&#10;- What does the product surface make clear?&#10;- How should the feature feel when it is working well?&#10;&#10;For IA, documentation, onboarding, workflow, or product-surface features, this&#10;section is mandatory. It should lead the spec toward the desired experience,&#10;not merely away from the current failure mode.&#10;&#10;### Problem Statement&#10;Same standard as the PRD: describe the failure mode, not the absence of your&#10;feature. Quantify where possible. Keep it subordinate to the future state; do&#10;not let the spec become a list of current complaints.&#10;&#10;### Functional Areas&#10;Use this section whenever a feature has more than one surface, stage, or domain&#10;object **within its one capability**. The area map should make clear what belongs&#10;where before requirements are written. Areas are *subordinate parts* of the&#10;feature — each fails the Decomposition test on its own (it cannot ship/cut&#10;independently and has no feature-level outcome of its own).&#10;&#10;Examples (areas *inside one capability*):&#10;&#10;- CSV lead import → field mapping, validation, duplicate handling, confirmation&#10;- Template editor → block palette, variable insertion, live preview, save/version&#10;- Campaign scheduler → recipient selection, send-time rules, blackout handling&#10;&#10;**Caution:** lists of *roles* (&quot;Admin, Operator, Auditor&quot;), *lifecycle stages*&#10;(&quot;Intake, Planning, Execution, Review&quot;), or *distinct domain objects* (&quot;Leads,&#10;Lists, Segments&quot;, &quot;API, CLI, docs&quot;) are usually **separate features**, not areas&#10;of one — each typically passes the Decomposition test as its own capability.&#10;Apply the test before treating them as areas.&#10;&#10;### Functional Requirements&#10;Number each requirement for traceability. Group requirements by functional&#10;area when the feature spans multiple areas. Use stable prefixes that make the&#10;scope clear (`NAV-01`, `TYPE-01`, `ART-01`) or use plain `FR-01` for narrow&#10;single-area features.&#10;&#10;Each requirement should be independently testable. These are what the feature&#10;must do — user stories describe how users interact with these capabilities.&#10;A feature spec may name a high-level interface dependency such as &quot;depends on a&#10;search API&quot;, but exact endpoints, commands, flags, payload fields, status codes,&#10;error semantics, config keys, telemetry fields, event schemas, and adapter&#10;signatures are normative surface and belong in a Contract.&#10;&#10;If a requirement mentions two areas joined by &quot;and&quot;, split it unless the&#10;relationship between those areas is itself the requirement.&#10;&#10;### Non-Functional Requirements&#10;Every NFR needs a specific target. &quot;Must be fast&quot; is not a requirement.&#10;&quot;95th percentile response under 200ms&quot; is. Only include NFRs relevant to&#10;this specific feature, not product-wide NFRs from the PRD.&#10;&#10;### User Stories&#10;Reference by ID and title with a relative link. Do not duplicate story&#10;content — the story file is the source of truth. If stories haven&#x27;t been&#10;written yet, list placeholders with `[TODO: create story]` and note it in&#10;Open Questions.&#10;&#10;### Edge Cases and Error Handling&#10;Feature-level edge cases that span multiple stories. If an edge case is&#10;specific to one story, it belongs in that story&#x27;s file.&#10;&#10;### Success Metrics&#10;Feature-specific metrics, not product-level metrics from the PRD. How do&#10;you know this specific feature is working as intended?&#10;&#10;### Dependencies&#10;Name specific feature IDs, external APIs, and PRD requirement numbers.&#10;&quot;Depends on auth&quot; is too vague. &quot;Depends on FEAT-002 (auth middleware)&#10;and the OAuth2 provider API&quot; is specific.&#10;&#10;### Out of Scope&#10;Each item should prevent a plausible scope question during implementation.&#10;&quot;Not a replacement for the database&quot; is only useful if someone might think&#10;it is.&#10;&#10;## Quality Checklist&#10;&#10;After drafting, verify every item. If any blocking check fails, revise before&#10;committing.&#10;&#10;### Blocking&#10;&#10;- [ ] Overview links to a specific PRD requirement&#10;- [ ] Ideal Future State is present for broad product-surface, workflow, IA, or documentation features&#10;- [ ] Functional Areas is present when the feature spans multiple surfaces, workflows, user modes, or domain objects&#10;- [ ] Similar domain objects are separated before requirements are written&#10;- [ ] Functional requirements are grouped by area when a flat list would mix unrelated scopes&#10;- [ ] Every functional requirement is testable&#10;- [ ] Non-functional requirements have specific numeric targets&#10;- [ ] User stories are referenced by ID (not duplicated inline)&#10;- [ ] Dependencies name specific feature IDs and external systems&#10;- [ ] Exact API/CLI/event/schema/config/telemetry/adapter surface is linked to a Contract, not defined inline&#10;- [ ] No `[NEEDS CLARIFICATION]` markers remain&#10;&#10;### Warning&#10;&#10;- [ ] Problem statement quantifies the pain&#10;- [ ] At least one feature-level edge case documented&#10;- [ ] Success metrics are feature-specific (not product-level)&#10;- [ ] Out of scope excludes something plausible</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: FEAT-XXX&#10;---&#10;&#10;# Feature Specification: FEAT-XXX — [Feature Name]&#10;&#10;**Feature ID**: FEAT-XXX&#10;**Status**: [Draft | Specified | Approved]&#10;**Priority**: [P0 | P1 | P2]&#10;**Owner**: [Team/Person]&#10;**Covered PRD Subsystem(s)**: [Subsystem name(s) from the PRD — normally exactly one]&#10;**Covered PRD Requirements**: [FR-n, FR-m — the PRD FRs this feature owns]&#10;**Cross-Subsystem Rationale**: [None — single subsystem. | If more than one subsystem&#10;is listed above: the rationale that the cross-subsystem workflow IS the feature;&#10;otherwise split it per the Decomposition test.]&#10;&lt;!-- reconcile-alignment reads these three fields: a feature spanning &gt;1 subsystem&#10;with no Cross-Subsystem Rationale is a mega-FEAT finding. --&gt;&#10;&#10;## Overview&#10;&#10;[What this feature is and why it exists. 2-3 sentences connecting this feature&#10;to a specific PRD requirement.]&#10;&#10;## Ideal Future State&#10;&#10;[Describe the future product behavior once this feature is working well. Focus&#10;on what users can understand, decide, or accomplish. For broad product-surface,&#10;workflow, IA, or documentation features, this section should come before the&#10;problem framing so requirements are pulled toward the desired outcome instead&#10;of only reacting to current pain.]&#10;&#10;## Problem Statement&#10;&#10;- **Current situation**: [What exists now — be specific]&#10;- **Pain points**: [What is not working and for whom]&#10;- **Desired outcome**: [What success looks like — measurable]&#10;&#10;## Functional Areas&#10;&#10;[For features with more than one surface or stage **within this one capability**,&#10;map the subordinate areas before writing requirements. Areas are parts of one&#10;capability — each fails the ship/cut/metric test on its own. Lists of roles,&#10;lifecycle stages, or distinct domain objects are usually *separate features*, not&#10;areas (apply the Decomposition test). Omit when the feature is a single narrow&#10;capability.]&#10;&#10;| Area | User question or job | Feature responsibility |&#10;|------|----------------------|------------------------|&#10;| [Area] | [What the user needs to know or do] | [What this feature must provide] |&#10;&#10;## Requirements&#10;&#10;### Functional Requirements by Area&#10;&#10;[Each requirement should be testable. Group requirements by functional area&#10;when the feature has multiple areas. Use stable prefixes that make the scope&#10;clear, such as `HOME-01`, `TYPE-01`, `NAV-01`, or `FR-01` for narrow features.&#10;Name high-level interface dependencies when needed, but do not define exact&#10;API/CLI/event/schema/config/telemetry/adapter surface here; link or request a&#10;Contract for commands, flags, endpoints, fields, payloads, status codes, error&#10;semantics, and compatibility rules.]&#10;&#10;#### [Area Name]&#10;&#10;[PREFIX-01]. [Requirement]&#10;[PREFIX-02]. [Requirement]&#10;&#10;### Non-Functional Requirements&#10;&#10;- **Performance**: [Specific target, e.g., &quot;95th percentile response &lt; 200ms&quot;]&#10;- **Security**: [Specific requirement, not &quot;must be secure&quot;]&#10;- **Scalability**: [Specific target, e.g., &quot;handles 10k concurrent users&quot;]&#10;- **Reliability**: [Specific target, e.g., &quot;99.9% uptime&quot;]&#10;&#10;## User Stories&#10;&#10;[List the user stories that implement this feature. Each story is a separate&#10;file in `docs/helix/01-frame/user-stories/`. Reference by ID — do not&#10;duplicate story content here.]&#10;&#10;- [US-XXX — Story title](../user-stories/US-XXX-slug.md)&#10;- [US-XXX — Story title](../user-stories/US-XXX-slug.md)&#10;&#10;## Edge Cases and Error Handling&#10;&#10;[Feature-level edge cases that span multiple stories. Story-specific edge&#10;cases belong in the story file.]&#10;&#10;- **[Condition]**: [Expected behavior]&#10;&#10;## Success Metrics&#10;&#10;[How do we know this feature is working? Metrics specific to this feature,&#10;not the product-level metrics from the PRD.]&#10;&#10;- [Metric with target]&#10;&#10;## Constraints and Assumptions&#10;&#10;- [Constraint or assumption specific to this feature]&#10;&#10;## Dependencies&#10;&#10;- **Other features**: [FEAT-XXX if this feature depends on another]&#10;- **External services**: [APIs, libraries, or systems this feature requires; exact surface lives in Contract artifacts]&#10;- **PRD requirements**: [Which P0/P1/P2 requirements this addresses]&#10;&#10;## Out of Scope&#10;&#10;[What this feature explicitly does not cover. Each item should prevent a&#10;plausible scope question.]&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing a feature specification:&#10;&#10;- [ ] Covered PRD Subsystem(s) and Requirements (`FR-n`) are listed; a feature spanning &gt;1 subsystem carries an explicit cross-subsystem rationale (else split per the Decomposition test)&#10;- [ ] Functional areas (if any) are subordinate parts of this one capability, not separate capabilities (each fails the ship/cut/metric test on its own)&#10;- [ ] Overview connects this feature to a specific PRD requirement&#10;- [ ] Ideal future state describes the desired user-visible outcome, not only current problems&#10;- [ ] Problem statement describes what exists now and what is broken — not just what is wanted&#10;- [ ] Functional areas are mapped when the feature spans multiple surfaces, workflows, or domain objects&#10;- [ ] Requirements are grouped by functional area when a flat list would mix unrelated scopes&#10;- [ ] Domain objects that sound similar are explicitly separated (for example, artifact instances vs artifact types)&#10;- [ ] Every functional requirement is testable — you can write an assertion for it&#10;- [ ] Acceptance criteria are defined in the user stories that decompose this feature, not here (ADR-009)&#10;- [ ] Non-functional requirements have specific numeric targets, not &quot;must be fast&quot;&#10;- [ ] Edge cases cover realistic failure scenarios, not just happy paths&#10;- [ ] Success metrics are specific to this feature, not product-level metrics&#10;- [ ] Dependencies reference real artifact IDs (FEAT-XXX, external APIs)&#10;- [ ] Out of scope excludes things someone might reasonably assume are in scope&#10;- [ ] No implementation details (&quot;use X library&quot;, &quot;create Y table&quot;) — specify WHAT not HOW&#10;- [ ] No exact API/CLI/event/schema/config/telemetry/adapter surface is defined inline; normative surface links to Contract artifacts&#10;- [ ] Feature is consistent with governing PRD requirements&#10;- [ ] No `[NEEDS CLARIFICATION]` markers remain unresolved for P0 features</code></pre></details></td></tr>
</tbody>
</table>
