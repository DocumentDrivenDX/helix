# Feature Specification Generation Prompt

Create a feature specification that is precise enough to support design,
user story creation, and test planning. The feature spec owns FR-IDs,
functional areas, and the decomposition test — acceptance criteria live in
user-stories (see ADR-009) and must not be restated here.

## Storage Location

Store at: `docs/helix/01-frame/features/FEAT-NNN-<name>.md`

## Purpose

A feature spec is the **feature-level authority for behavior and boundaries**.
It translates PRD requirements into precise feature behavior, functional areas,
non-functional expectations, edge cases, and feature-specific success measures.
Acceptance criteria belong to user stories (ADR-009) and are not defined here.

It sits between the PRD (which defines product scope) and user stories (which
define vertical slices through the feature). The feature spec owns feature
behavior. User stories own user journeys. Solution and technical designs own
how the behavior will be built.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/ibm-requirements-management.md` grounds traceable,
  prioritized, verifiable requirements.
- `docs/resources/cucumber-executable-specifications.md` grounds concrete
  examples as readable acceptance specifications without prescribing
  implementation or tooling.

## Active Concerns

For each concern selected in `docs/helix/01-frame/concerns.md`, apply its declared
`## Artifact Impact` (from `workflows/concerns/<name>/concern.md`) to THIS feature spec — realize the
FEAT-level obligations it names (usage-metering -> which actions are billable; multi-tenancy -> tenant-scoped ACs). A selected concern whose Artifact Impact names FEAT
but leaves no trace here is drift (reconcile-alignment Concern->Artifact Realization check).

## Key Principles

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
  areas before writing requirements and group requirements by area instead of
  producing one flat list. (Areas are subordinate parts of one capability — if an
  "area" would pass the Decomposition test as its own capability, it is a separate
  feature, not an area.)
- **Separate similar domain objects** — if readers might confuse two things,
  define them separately before requirements. For example, "Artifacts" are
  project-specific instances; "Artifact Types" are reusable methodology
  definitions.
- **Stories by reference** — list user story IDs, don't duplicate story
  content. Stories are separate files with their own lifecycle.
- **Testable requirements** — every functional requirement should be
  verifiable. If you can't describe how to test it, it's too vague.
- **Leave unknowns explicit** — use Open Questions at the bottom rather than
  inventing detail you don't have.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Product goals, personas, launch priority, or product-level metrics | PRD |
| Feature behavior, boundaries, and edge cases | Feature Specification |
| A vertical user journey through one or more feature requirements, with acceptance criteria | User Story |
| Exact API/CLI/event/schema surface, commands, flags, fields, payloads, status codes, error semantics, or compatibility rules | Contract |
| Feature-level technical approach, component choices, domain/data model, interface usage, or implementation approach | Solution/Technical Design |
| Detailed test cases, fixtures, or automation strategy | Test Plan or Story Test Plan |
| Build sequencing and work slices | Implementation Plan |

## Decomposition — is it a FEAT or a functional area?

The brief decomposes into features at one granularity: **one feature per
capability**, anchored to the PRD's `### Subsystem:` groupings (~one subsystem →
one `FEAT-NNN`). Use these **layered tests** to place a candidate:

1. **Primary — ship / cut / metric.** A candidate is its own **feature** if all
   hold:
   - **Ship/cut:** it could be removed or deferred **without making another
     *named* capability incoherent** (it stands alone in the parking-lot).
   - **Metric:** it carries its own **feature-level product/user outcome** as a
     success metric — not a local counter (a button click or a row count is not a
     feature metric).
   If a candidate fails these — it cannot stand alone and has no outcome of its
   own — it is a **functional area** within a feature, not a feature.
2. **Tie-breaker — bounded context.** When ship/cut is genuinely ambiguous, split
   on bounded context / aggregate root: one feature per bounded context; areas are
   views/stages over the *same* aggregate.

**Anchor:** the PRD names the subsystems; each maps to ~one feature. A
multi-subsystem brief that produces a single mega-feature, or that produces zero
feature specs (PRD → stories directly), has skipped this tier — reconcile-alignment
flags both. A deliberately cross-subsystem feature (the workflow that spans them
*is* the feature) is allowed, but must say so explicitly in the template's
**Cross-Subsystem Rationale** field (the "Covered PRD Subsystem(s)" /
"Covered PRD Requirements" fields hold the subsystem names and FR IDs).
## Section-by-Section Guidance

### Overview
Connect this feature to a specific PRD requirement. "This feature implements
PRD P0-3" is better than "This feature improves the user experience."

### Ideal Future State
Describe the target state in user-visible terms. A good future state answers:

- What can the user understand, decide, or accomplish?
- What does the product surface make clear?
- How should the feature feel when it is working well?

For IA, documentation, onboarding, workflow, or product-surface features, this
section is mandatory. It should lead the spec toward the desired experience,
not merely away from the current failure mode.

### Problem Statement
Same standard as the PRD: describe the failure mode, not the absence of your
feature. Quantify where possible. Keep it subordinate to the future state; do
not let the spec become a list of current complaints.

### Functional Areas
Use this section whenever a feature has more than one surface, stage, or domain
object **within its one capability**. The area map should make clear what belongs
where before requirements are written. Areas are *subordinate parts* of the
feature — each fails the Decomposition test on its own (it cannot ship/cut
independently and has no feature-level outcome of its own).

Examples (areas *inside one capability*):

- CSV lead import → field mapping, validation, duplicate handling, confirmation
- Template editor → block palette, variable insertion, live preview, save/version
- Campaign scheduler → recipient selection, send-time rules, blackout handling

**Caution:** lists of *roles* ("Admin, Operator, Auditor"), *lifecycle stages*
("Intake, Planning, Execution, Review"), or *distinct domain objects* ("Leads,
Lists, Segments", "API, CLI, docs") are usually **separate features**, not areas
of one — each typically passes the Decomposition test as its own capability.
Apply the test before treating them as areas.

### Functional Requirements
Number each requirement for traceability. Group requirements by functional
area when the feature spans multiple areas. Use stable prefixes that make the
scope clear (`NAV-01`, `TYPE-01`, `ART-01`) or use plain `FR-01` for narrow
single-area features.

Each requirement should be independently testable. These are what the feature
must do — user stories describe how users interact with these capabilities.
A feature spec may name a high-level interface dependency such as "depends on a
search API", but exact endpoints, commands, flags, payload fields, status codes,
error semantics, config keys, telemetry fields, event schemas, and adapter
signatures are normative surface and belong in a Contract.

If a requirement mentions two areas joined by "and", split it unless the
relationship between those areas is itself the requirement.

### Non-Functional Requirements
Every NFR needs a specific target. "Must be fast" is not a requirement.
"95th percentile response under 200ms" is. Only include NFRs relevant to
this specific feature, not product-wide NFRs from the PRD.

### User Stories
Reference by ID and title with a relative link. Do not duplicate story
content — the story file is the source of truth. If stories haven't been
written yet, list placeholders with `[TODO: create story]` and note it in
Open Questions.

### Edge Cases and Error Handling
Feature-level edge cases that span multiple stories. If an edge case is
specific to one story, it belongs in that story's file.

### Success Metrics
Feature-specific metrics, not product-level metrics from the PRD. How do
you know this specific feature is working as intended?

### Dependencies
Name specific feature IDs, external APIs, and PRD requirement numbers.
"Depends on auth" is too vague. "Depends on FEAT-002 (auth middleware)
and the OAuth2 provider API" is specific.

### Out of Scope
Each item should prevent a plausible scope question during implementation.
"Not a replacement for the database" is only useful if someone might think
it is.

## Quality Checklist

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
