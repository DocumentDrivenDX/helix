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
- [ ] Test scenarios include concrete values, not placeholders
- [ ] Story links to parent feature spec by ID
- [ ] Story names the parent feature requirement IDs it exercises
- [ ] Story names the PRD `FR-n` it covers; bundled unrelated `FR-n`s carry recorded justification
- [ ] Exact API/CLI/event/schema/config/telemetry/adapter surface is linked to a Contract, not defined inline

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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/user-stories/</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/test/story-test-plan/">Story Test Plan</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># User Story Generation Prompt&#10;&#10;Create standalone user stories that serve as stable design artifacts — vertical&#10;slices referenced throughout design, implementation, and testing.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/01-frame/user-stories/US-NNN-&lt;slug&gt;.md` (one file per story)&#10;&#10;## Purpose&#10;&#10;User stories are **governing design artifacts**, not throwaway tickets. Each&#10;story defines one persona&#x27;s complete vertical journey through feature behavior&#10;that is independently implementable and testable. Tracker issues reference&#10;stories; stories don&#x27;t reference tracker issues. Stories are more stable than&#10;the implementation work items that fulfill them.&#10;&#10;The feature spec owns behavior and boundaries. A user story owns a journey&#10;through that behavior: who starts it, what they do, what the system shows, and&#10;what outcome proves the slice works.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/atlassian-user-stories.md` grounds persona-goal-value story&#10;  framing and acceptance criteria.&#10;- `docs/resources/cucumber-executable-specifications.md` grounds observable&#10;  Given/When/Then acceptance criteria without requiring BDD tooling.&#10;&#10;## Key Principles&#10;&#10;- **One story, one vertical slice** — one persona completing one goal,&#10;  demonstrable end-to-end in a single flow. If it can&#x27;t be demonstrated&#10;  end-to-end, it&#x27;s not a story yet. The parent feature is the capability&#10;  envelope; it has as many stories as it has distinct persona-goals. This is the&#10;  FEAT↔story boundary.&#10;- **One file per story** — each story is its own `US-NNN-&lt;slug&gt;.md` under&#10;  `docs/helix/01-frame/user-stories/` (never a single monolithic&#10;  `user-stories.md`); reconcile-alignment flags a monolithic stories file.&#10;- **Stable reference** — stories will be referenced by multiple tracker issues&#10;  across design, implementation, and testing. Write them to last.&#10;- **Implementer-sufficient** — an implementer reading only this story and the&#10;  parent feature spec should be able to build it without asking clarifying&#10;  questions.&#10;- **Test-first friendly** — acceptance criteria and test scenarios should be&#10;  concrete enough to write tests before writing code.&#10;- **Traceable to feature behavior** — each story should name the feature&#10;  requirements it exercises. Do not invent behavior outside the parent feature&#10;  spec.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Product-level scope, personas, priorities, or metrics | PRD |&#10;| Complete feature behavior, functional areas, and edge cases | Feature Specification |&#10;| One persona&#x27;s journey through a feature slice | User Story |&#10;| Exact API/CLI/event/schema surface, commands, flags, fields, payloads, status codes, error semantics, or compatibility rules | Contract |&#10;| Component design, data model, interface usage, or build approach | Solution/Technical Design |&#10;| Detailed fixtures, test harnesses, or automation strategy | Story Test Plan |&#10;| Work assignment, status, or execution notes | runtime work item or issue |&#10;&#10;## Section-by-Section Guidance&#10;&#10;### Story (As a / I want / So that)&#10;The &quot;As a&quot; must name a specific persona from the PRD, not a generic role.&#10;The &quot;I want&quot; must describe what the user does, not what the system does&#10;internally. The &quot;So that&quot; must name a measurable outcome or business value —&#10;&quot;so that I can use the feature&quot; is circular.&#10;&#10;### Context&#10;This is the background an implementer needs to make judgment calls. Why does&#10;this story exist? What&#x27;s the user&#x27;s situation? Which parent feature&#10;requirements does it exercise? What pain are they hitting?&#10;2-4 sentences, not a paragraph of filler. Test: would removing this section&#10;force the implementer to ask a question? If not, it&#x27;s too generic.&#10;&#10;### Walkthrough&#10;A step-by-step journey through the vertical slice. Present tense, concrete&#10;actions. This is not a flowchart — it&#x27;s one specific path (the happy path)&#10;from trigger to outcome. Branching and error cases go in Edge Cases.&#10;&#10;Test: could a QA engineer use this walkthrough as a manual test script?&#10;&#10;### Acceptance Criteria&#10;Given/When/Then format. Each criterion must be independently testable — one&#10;clear precondition, one action, one observable outcome. Avoid compound&#10;criteria (&quot;Given A and B and C, when D, then E and F and G&quot;). Split those&#10;into separate criteria.&#10;&#10;Acceptance criteria may reference a Contract ID when exact interface behavior&#10;matters, but they must not define the shared surface inline. Do not put&#10;specific endpoints, command flags, payload fields, status codes, error codes,&#10;event schemas, config keys, telemetry fields, or adapter signatures in ACs; put&#10;that normative detail in a Contract and keep the AC focused on the observable&#10;outcome.&#10;&#10;Each criterion carries a **stable AC ID** of the form `US-&lt;n&gt;-AC&lt;m&gt;` (e.g.&#10;`US-001-AC1`), where `&lt;n&gt;` is this story&#x27;s number. The ID is stable across edits&#10;so downstream artifacts reference a specific criterion by name. The story test&#10;plan (STP) owns the matrix that maps each AC ID to the failing test(s) that&#10;prove it — do **not** duplicate that matrix here; the story just defines the&#10;criteria and their IDs. The project-level test plan (TP) aggregates strategy and&#10;allocates criteria to test layers; it does not restate the per-AC matrix either&#10;(FEAT-008 FR-6).&#10;&#10;### Edge Cases&#10;What happens when the user does something unexpected, inputs are invalid,&#10;or the system is in an unusual state? Each edge case names the condition and&#10;the expected behavior. Don&#x27;t just list failure modes — specify what the system&#10;should do.&#10;&#10;### Test Scenarios&#10;Concrete input/output pairs. An implementer should be able to copy these into&#10;a test file with minimal modification. Include the happy path and at least one&#10;edge case from the section above. Name specific values, not placeholders.&#10;&#10;### Dependencies&#10;Name other stories this one depends on (by ID), the parent feature spec,&#10;and any external systems or APIs. If another story must be done first, say so.&#10;Name Contract IDs for exact interface surfaces instead of restating those&#10;surfaces here.&#10;&#10;### Traceability&#10;Name the parent feature requirement IDs that the story exercises. If the story&#10;needs behavior that is not in the feature spec, update the feature spec first.&#10;&#10;Also name the **PRD functional requirement(s) `FR-n`** this story covers.&#10;**Every PRD `FR-n` must map to ≥1 user story** — this is a coverage floor that&#10;reconcile-alignment checks; a `FR-n` with no story is a blocking gap. A single&#10;story may cover more than one `FR-n`, but **do not bundle unrelated `FR-n`s into&#10;one story without recorded justification** — unrelated requirements belong in&#10;separate vertical slices so each can be tested independently.&#10;&#10;### Out of Scope&#10;What this story explicitly does not cover. Each item should exclude something&#10;an implementer might reasonably try to include. This prevents scope creep&#10;during implementation.&#10;&#10;## Quality Checklist&#10;&#10;After drafting, verify every item. If any blocking check fails, revise before&#10;committing.&#10;&#10;### Blocking&#10;&#10;- [ ] Story names a specific persona from the PRD (not a generic role)&#10;- [ ] &quot;I want&quot; describes a user action, not a system behavior&#10;- [ ] &quot;So that&quot; names a measurable outcome, not a tautology&#10;- [ ] Walkthrough traces a complete path from trigger to outcome&#10;- [ ] Every acceptance criterion is independently testable (one Given/When/Then)&#10;- [ ] Test scenarios include concrete values, not placeholders&#10;- [ ] Story links to parent feature spec by ID&#10;- [ ] Story names the parent feature requirement IDs it exercises&#10;- [ ] Story names the PRD `FR-n` it covers; bundled unrelated `FR-n`s carry recorded justification&#10;- [ ] Exact API/CLI/event/schema/config/telemetry/adapter surface is linked to a Contract, not defined inline&#10;&#10;### Warning&#10;&#10;- [ ] Context would be missed if removed (not generic filler)&#10;- [ ] At least one edge case is documented&#10;- [ ] Test scenarios cover both happy path and at least one edge case&#10;- [ ] Out of scope excludes something plausible&#10;- [ ] No compound acceptance criteria (split into separate items)&#10;- [ ] Story does not invent behavior outside the parent feature spec</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: US-XXX&#10;---&#10;&#10;# US-XXX: [Story Title]&#10;&#10;**Feature**: [FEAT-XXX — Feature Name]&#10;**Feature Requirements**: [REQ-01, REQ-02]&#10;**PRD Requirements**: [FR-n — the PRD functional requirement(s) this story covers]&#10;**Priority**: [P0 | P1 | P2]&#10;**Status**: [Draft | Review | Approved]&#10;&#10;## Story&#10;&#10;**As a** [specific user type from PRD personas]&#10;**I want** [specific functionality — what the user does, not what the system does]&#10;**So that** [measurable business value or user outcome]&#10;&#10;## Context&#10;&#10;[Why this story matters. What&#x27;s the user&#x27;s situation before this works? What&#10;problem are they hitting? Which parent feature requirements does this story&#10;exercise? This should be 2-4 sentences that give an implementer enough&#10;background to make judgment calls without asking.]&#10;&#10;## Walkthrough&#10;&#10;[Step-by-step description of the user&#x27;s journey through this slice. Write in&#10;present tense. Name concrete actions and system responses. This is the&#10;vertical slice — it should cover one complete path from trigger to outcome.]&#10;&#10;1. User [action]&#10;2. System [response]&#10;3. User [action]&#10;4. System [response — the outcome]&#10;&#10;## Acceptance Criteria&#10;&#10;[See the prompt&#x27;s Acceptance Criteria guidance for the canonical AC-ID rule.]&#10;Acceptance criteria describe observable outcomes. If exact API, CLI, event,&#10;schema, config, telemetry, or adapter behavior matters, reference the Contract&#10;ID instead of defining endpoints, commands, flags, payloads, fields, status&#10;codes, or signatures inline.&#10;&#10;- [ ] **US-XXX-AC1** — Given [specific precondition], when [specific action], then [observable outcome]&#10;- [ ] **US-XXX-AC2** — Given [specific precondition], when [specific action], then [observable outcome]&#10;&#10;## Edge Cases&#10;&#10;[What happens when things go wrong or inputs are unexpected? Each edge case&#10;should name the condition and the expected system behavior.]&#10;&#10;- **[Condition]**: [Expected behavior]&#10;- **[Condition]**: [Expected behavior]&#10;&#10;## Test Scenarios&#10;&#10;[Concrete input/output pairs for the acceptance criteria. An implementer&#10;should be able to copy these into a test file.]&#10;&#10;| Scenario | AC ID | Input / State | Action | Expected Result |&#10;|----------|-------|---------------|--------|-----------------|&#10;| Happy path | US-XXX-AC1 | [specific state] | [specific action] | [specific result] |&#10;| [Edge case] | US-XXX-AC2 | [specific state] | [specific action] | [specific result] |&#10;&#10;## Dependencies&#10;&#10;- **Stories**: [US-XXX if this story depends on another being done first]&#10;- **Feature Spec**: [FEAT-XXX]&#10;- **Feature Requirements**: [REQ-01, REQ-02]&#10;- **PRD Requirements**: [FR-n — PRD functional requirement(s) this story covers]&#10;- **External**: [APIs, services, data, or Contract IDs this story requires; exact surface lives in Contract artifacts]&#10;&#10;## Out of Scope&#10;&#10;[What this story explicitly does not cover, to prevent scope creep during&#10;implementation.]&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing a user story:&#10;&#10;- [ ] Stored as its own file `US-NNN-&lt;slug&gt;.md` (one file per story — never a single monolithic `user-stories.md`)&#10;- [ ] Covers one persona completing one goal, demonstrable end-to-end in a single flow&#10;- [ ] Links to its parent `FEAT-NNN` and names the PRD `FR-n` it covers&#10;- [ ] Every acceptance criterion is independently testable and carries a stable `US-NNN-ACm` ID&#10;- [ ] Walkthrough traces a complete path from trigger to outcome; at least one edge case documented&#10;- [ ] No exact API/CLI/event/schema/config/telemetry/adapter surface is defined inline; normative surface links to Contract artifacts</code></pre></details></td></tr>
</tbody>
</table>
