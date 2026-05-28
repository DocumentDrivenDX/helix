---
title: "User Stories"
linkTitle: "User Stories"
slug: user-stories
activity: "Frame"
artifactRole: "core"
weight: 14
generated: true
---

## Purpose

User stories are **governing design artifacts**, not throwaway tickets. Each
story defines one persona's complete vertical journey through feature behavior
that is independently implementable and testable. Tracker issues reference
stories; stories don't reference tracker issues. Stories are more stable than
the implementation work items that fulfill them.

The feature spec owns behavior and boundaries. A user story owns a journey
through that behavior: who starts it, what they do, what the system shows, and
what outcome proves the slice works.

## Authoring guidance

- **One story, one vertical slice** — one persona completing one goal,
  demonstrable end-to-end in a single flow. If it can't be demonstrated
  end-to-end, it's not a story yet. The parent feature is the capability
  envelope; it has as many stories as it has distinct persona-goals. This is the
  FEAT↔story boundary.
- **One file per story** — each story is its own `US-NNN-<slug>.md` under
  `docs/helix/01-frame/user-stories/` (never a single monolithic
  `user-stories.md`); reconcile-alignment flags a monolithic stories file.
- **Stable reference** — stories will be referenced by multiple tracker issues
  across design, implementation, and testing. Write them to last.
- **Implementer-sufficient** — an implementer reading only this story and the
  parent feature spec should be able to build it without asking clarifying
  questions.
- **Test-first friendly** — acceptance criteria and test scenarios should be
  concrete enough to write tests before writing code.

_Additional guidance continues in the full prompt below._

<details>
<summary>Quality checklist from the prompt</summary>

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] Story names a specific persona from the PRD (not a generic role)
- [ ] "I want" describes a user action, not a system behavior
- [ ] "So that" names a measurable outcome, not a tautology
- [ ] Walkthrough traces a complete path from trigger to outcome
- [ ] Every acceptance criterion is independently testable (one Given/When/Then)
- [ ] Every acceptance criterion carries a stable `US-<n>-AC<m>` ID
- [ ] Test scenarios include concrete values, not placeholders
- [ ] Story links to parent feature spec by ID
- [ ] Story names the parent feature requirement IDs it exercises
- [ ] Story names the PRD `FR-n` it covers; bundled unrelated `FR-n`s carry recorded justification

### Warning

- [ ] Context would be missed if removed (not generic filler)
- [ ] At least one edge case is documented
- [ ] Test scenarios cover both happy path and at least one edge case
- [ ] Out of scope excludes something plausible
- [ ] No compound acceptance criteria (split into separate items)
- [ ] Story does not invent behavior outside the parent feature spec

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.user-story.depositmatch.upload-csv
  depends_on:
    - example.feature-specification.depositmatch.csv-import
  review:
    self_hash: b87b259be7a0ac9a75516d5868742aed44b6af05ab12d10aa4535a3cae24e9b6
    deps:
      example.feature-specification.depositmatch.csv-import: d85530eb091209cf9989c9cac3bc1f1063358a5b79964ca0e5e7a384fa77c44a
    reviewed_at: "2026-05-24T23:28:08Z"
---

# US-001: Upload CSV Files for a Client

**Feature**: FEAT-001 - CSV Import and Column Mapping
**Feature Requirements**: UP-01, UP-02
**Priority**: P0
**Status**: Approved

## Story

**As a** Maya, the reconciliation lead
**I want** to upload bank and invoice CSV files for one client
**So that** I can start weekly reconciliation from the client's current source
data without rebuilding the import context by hand.

## Context

Maya receives weekly bank and invoice exports from each client she manages. This
story covers the first step of FEAT-001: associating one bank deposit CSV and
one invoice export CSV with the selected client and import session. It exercises
UP-01 and UP-02 only; mapping, validation, and import summary behavior are
covered by follow-on stories.

## Walkthrough

1. Maya opens Acme Dental's reconciliation workspace and chooses to start a new
   import session.
2. DepositMatch shows bank deposit and invoice export upload controls for Acme
   Dental.
3. Maya selects `acme-bank-2026-05-08.csv` and
   `acme-invoices-2026-05-08.csv`.
4. DepositMatch accepts both CSV files, associates them with the Acme Dental
   import session, and opens the mapping review step.

## Acceptance Criteria

- [ ] **US-001-AC1** — Given Maya is viewing Acme Dental, when she uploads one
  valid bank CSV and one valid invoice CSV, then DepositMatch creates one draft
  import session for Acme Dental and opens mapping review.
- [ ] **US-001-AC2** — Given Maya is viewing Acme Dental, when she uploads a PDF
  instead of a CSV for either required file, then DepositMatch rejects the file
  before parsing and keeps the import session in draft.
- [ ] **US-001-AC3** — Given Maya has uploaded both required CSV files, when the
  files are accepted, then the import session records the client, file names,
  upload time, and source type for each file.

## Edge Cases

- **Wrong file type**: Reject non-CSV files before parsing and identify which
  file slot failed.
- **Missing second file**: Keep the import session in draft until both bank and
  invoice files are present.
- **Client changed mid-upload**: Associate accepted files only with the client
  selected at upload confirmation time.

## Test Scenarios

| Scenario | AC ID | Input / State | Action | Expected Result |
|----------|-------|---------------|--------|-----------------|
| Happy path | US-001-AC1 | Client `Acme Dental`; files `acme-bank-2026-05-08.csv` and `acme-invoices-2026-05-08.csv` | Maya uploads both files | Draft import session is created for Acme Dental and mapping review opens |
| Wrong file type | US-001-AC2 | Client `Acme Dental`; bank file `statement.pdf`; invoice file `acme-invoices-2026-05-08.csv` | Maya uploads both files | PDF is rejected before parsing; session remains draft |
| Missing invoice file | US-001-AC2 | Client `Acme Dental`; bank file only | Maya uploads the bank file | Bank file is attached to draft session; mapping review does not open |

## Dependencies

- **Stories**: None.
- **Feature Spec**: FEAT-001 - CSV Import and Column Mapping.
- **Feature Requirements**: UP-01, UP-02.
- **External**: Browser file upload support; no external APIs for v1.

## Out of Scope

- Column mapping.
- Row-level validation.
- Match suggestion generation.
- Saving accepted rows into the review queue.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/user-stories/</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br>Test Cases<br>Tracker Issues</td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># User Story Generation Prompt

Create standalone user stories that serve as stable design artifacts — vertical
slices referenced throughout design, implementation, and testing.

## Storage Location

Store at: `docs/helix/01-frame/user-stories/US-NNN-&lt;slug&gt;.md` (one file per story)

## Purpose

User stories are **governing design artifacts**, not throwaway tickets. Each
story defines one persona&#x27;s complete vertical journey through feature behavior
that is independently implementable and testable. Tracker issues reference
stories; stories don&#x27;t reference tracker issues. Stories are more stable than
the implementation work items that fulfill them.

The feature spec owns behavior and boundaries. A user story owns a journey
through that behavior: who starts it, what they do, what the system shows, and
what outcome proves the slice works.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/atlassian-user-stories.md` grounds persona-goal-value story
  framing and acceptance criteria.
- `docs/resources/cucumber-executable-specifications.md` grounds observable
  Given/When/Then acceptance criteria without requiring BDD tooling.

## Key Principles

- **One story, one vertical slice** — one persona completing one goal,
  demonstrable end-to-end in a single flow. If it can&#x27;t be demonstrated
  end-to-end, it&#x27;s not a story yet. The parent feature is the capability
  envelope; it has as many stories as it has distinct persona-goals. This is the
  FEAT↔story boundary.
- **One file per story** — each story is its own `US-NNN-&lt;slug&gt;.md` under
  `docs/helix/01-frame/user-stories/` (never a single monolithic
  `user-stories.md`); reconcile-alignment flags a monolithic stories file.
- **Stable reference** — stories will be referenced by multiple tracker issues
  across design, implementation, and testing. Write them to last.
- **Implementer-sufficient** — an implementer reading only this story and the
  parent feature spec should be able to build it without asking clarifying
  questions.
- **Test-first friendly** — acceptance criteria and test scenarios should be
  concrete enough to write tests before writing code.
- **Traceable to feature behavior** — each story should name the feature
  requirements it exercises. Do not invent behavior outside the parent feature
  spec.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Product-level scope, personas, priorities, or metrics | PRD |
| Complete feature behavior, functional areas, and edge cases | Feature Specification |
| One persona&#x27;s journey through a feature slice | User Story |
| Component design, data model, API shape, or build approach | Solution/Technical Design |
| Detailed fixtures, test harnesses, or automation strategy | Story Test Plan |
| Work assignment, status, or execution notes | runtime work item or issue |

## Section-by-Section Guidance

### Story (As a / I want / So that)
The &quot;As a&quot; must name a specific persona from the PRD, not a generic role.
The &quot;I want&quot; must describe what the user does, not what the system does
internally. The &quot;So that&quot; must name a measurable outcome or business value —
&quot;so that I can use the feature&quot; is circular.

### Context
This is the background an implementer needs to make judgment calls. Why does
this story exist? What&#x27;s the user&#x27;s situation? Which parent feature
requirements does it exercise? What pain are they hitting?
2-4 sentences, not a paragraph of filler. Test: would removing this section
force the implementer to ask a question? If not, it&#x27;s too generic.

### Walkthrough
A step-by-step journey through the vertical slice. Present tense, concrete
actions. This is not a flowchart — it&#x27;s one specific path (the happy path)
from trigger to outcome. Branching and error cases go in Edge Cases.

Test: could a QA engineer use this walkthrough as a manual test script?

### Acceptance Criteria
Given/When/Then format. Each criterion must be independently testable — one
clear precondition, one action, one observable outcome. Avoid compound
criteria (&quot;Given A and B and C, when D, then E and F and G&quot;). Split those
into separate criteria.

Each criterion carries a **stable AC ID** of the form `US-&lt;n&gt;-AC&lt;m&gt;` (e.g.
`US-001-AC1`), where `&lt;n&gt;` is this story&#x27;s number. The ID is stable across edits
so downstream artifacts reference a specific criterion by name. The story test
plan (STP) owns the matrix that maps each AC ID to the failing test(s) that
prove it — do **not** duplicate that matrix here; the story just defines the
criteria and their IDs. The project-level test plan (TP) aggregates strategy and
allocates criteria to test layers; it does not restate the per-AC matrix either
(FEAT-008 FR-6).

### Edge Cases
What happens when the user does something unexpected, inputs are invalid,
or the system is in an unusual state? Each edge case names the condition and
the expected behavior. Don&#x27;t just list failure modes — specify what the system
should do.

### Test Scenarios
Concrete input/output pairs. An implementer should be able to copy these into
a test file with minimal modification. Include the happy path and at least one
edge case from the section above. Name specific values, not placeholders.

### Dependencies
Name other stories this one depends on (by ID), the parent feature spec,
and any external systems or APIs. If another story must be done first, say so.

### Traceability
Name the parent feature requirement IDs that the story exercises. If the story
needs behavior that is not in the feature spec, update the feature spec first.

Also name the **PRD functional requirement(s) `FR-n`** this story covers.
**Every PRD `FR-n` must map to ≥1 user story** — this is a coverage floor that
reconcile-alignment checks; a `FR-n` with no story is a blocking gap. A single
story may cover more than one `FR-n`, but **do not bundle unrelated `FR-n`s into
one story without recorded justification** — unrelated requirements belong in
separate vertical slices so each can be tested independently.

### Out of Scope
What this story explicitly does not cover. Each item should exclude something
an implementer might reasonably try to include. This prevents scope creep
during implementation.

## Quality Checklist

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] Story names a specific persona from the PRD (not a generic role)
- [ ] &quot;I want&quot; describes a user action, not a system behavior
- [ ] &quot;So that&quot; names a measurable outcome, not a tautology
- [ ] Walkthrough traces a complete path from trigger to outcome
- [ ] Every acceptance criterion is independently testable (one Given/When/Then)
- [ ] Every acceptance criterion carries a stable `US-&lt;n&gt;-AC&lt;m&gt;` ID
- [ ] Test scenarios include concrete values, not placeholders
- [ ] Story links to parent feature spec by ID
- [ ] Story names the parent feature requirement IDs it exercises
- [ ] Story names the PRD `FR-n` it covers; bundled unrelated `FR-n`s carry recorded justification

### Warning

- [ ] Context would be missed if removed (not generic filler)
- [ ] At least one edge case is documented
- [ ] Test scenarios cover both happy path and at least one edge case
- [ ] Out of scope excludes something plausible
- [ ] No compound acceptance criteria (split into separate items)
- [ ] Story does not invent behavior outside the parent feature spec</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: US-XXX
---

# US-XXX: [Story Title]

**Feature**: [FEAT-XXX — Feature Name]
**Feature Requirements**: [REQ-01, REQ-02]
**PRD Requirements**: [FR-n — the PRD functional requirement(s) this story covers]
**Priority**: [P0 | P1 | P2]
**Status**: [Draft | Review | Approved]

## Story

**As a** [specific user type from PRD personas]
**I want** [specific functionality — what the user does, not what the system does]
**So that** [measurable business value or user outcome]

## Context

[Why this story matters. What&#x27;s the user&#x27;s situation before this works? What
problem are they hitting? Which parent feature requirements does this story
exercise? This should be 2-4 sentences that give an implementer enough
background to make judgment calls without asking.]

## Walkthrough

[Step-by-step description of the user&#x27;s journey through this slice. Write in
present tense. Name concrete actions and system responses. This is the
vertical slice — it should cover one complete path from trigger to outcome.]

1. User [action]
2. System [response]
3. User [action]
4. System [response — the outcome]

## Acceptance Criteria

[Each criterion must be testable and carry a **stable AC ID** of the form
`US-&lt;n&gt;-AC&lt;m&gt;` (matching this story&#x27;s number). Use Given/When/Then format — one
precondition, one action, one observable outcome. The ID is stable: it survives
edits so the story test plan and tests can reference a specific criterion by
name. An implementer should be able to write a passing test from each criterion
alone.]

- [ ] **US-XXX-AC1** — Given [specific precondition], when [specific action], then [observable outcome]
- [ ] **US-XXX-AC2** — Given [specific precondition], when [specific action], then [observable outcome]

## Edge Cases

[What happens when things go wrong or inputs are unexpected? Each edge case
should name the condition and the expected system behavior.]

- **[Condition]**: [Expected behavior]
- **[Condition]**: [Expected behavior]

## Test Scenarios

[Concrete input/output pairs for the acceptance criteria. An implementer
should be able to copy these into a test file.]

| Scenario | AC ID | Input / State | Action | Expected Result |
|----------|-------|---------------|--------|-----------------|
| Happy path | US-XXX-AC1 | [specific state] | [specific action] | [specific result] |
| [Edge case] | US-XXX-AC2 | [specific state] | [specific action] | [specific result] |

## Dependencies

- **Stories**: [US-XXX if this story depends on another being done first]
- **Feature Spec**: [FEAT-XXX]
- **Feature Requirements**: [REQ-01, REQ-02]
- **PRD Requirements**: [FR-n — PRD functional requirement(s) this story covers]
- **External**: [APIs, services, or data this story requires]

## Out of Scope

[What this story explicitly does not cover, to prevent scope creep during
implementation.]

## Review Checklist

Use this checklist when reviewing a user story:

- [ ] Stored as its own file `US-NNN-&lt;slug&gt;.md` (one file per story — never a single monolithic `user-stories.md`)
- [ ] Covers one persona completing one goal, demonstrable end-to-end in a single flow
- [ ] Links to its parent `FEAT-NNN` and names the PRD `FR-n` it covers
- [ ] Every acceptance criterion is independently testable and carries a stable `US-NNN-ACm` ID
- [ ] Walkthrough traces a complete path from trigger to outcome; at least one edge case documented</code></pre></details></td></tr>
</tbody>
</table>
