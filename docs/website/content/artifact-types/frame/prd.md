---
title: "Product Requirements Document"
linkTitle: "PRD"
slug: prd
activity: "Frame"
artifactRole: "core"
weight: 10
generated: true
---

## Purpose

The PRD is the **product-scope authority for what to build and why**. Its
unique job is to translate the Product Vision into prioritized, measurable
requirements and boundaries. It sits between the product vision (which defines
direction) and feature specs (which define feature-level detail). Every design
decision and implementation choice should trace back to a PRD requirement.

## Authoring guidance

- **Problem first** — the problem section should make someone feel the pain
  before they see the solution.
- **Decision-oriented** — every section should help someone make a build/skip
  decision. If a section doesn't inform a decision, it's filler.
- **Testable requirements** — every P0 requirement should be verifiable. If
  you can't describe how to test it, it's too vague.
- **Traceable boundaries** — requirements should connect upward to the Product
  Vision and downward to feature specs, designs, tests, and build work.
- **Honest non-goals** — non-goals should exclude things someone might
  reasonably expect to be in scope. "Not a replacement for X" only matters if
  someone might assume it is.

<details>
<summary>Boundaries: what belongs elsewhere</summary>

Product requirements are for product scope. If you find yourself writing about:

| This content | Belongs in |
|---|---|
| Market sizing, ROI, investment case | `00-discover/business-case.md` |
| Positioning, target market, long-horizon strategic success | `00-discover/product-vision.md` |
| Detailed feature behavior and edge cases | `01-frame/features/FEAT-*.md` |
| User journey phrasing independent of product-level requirements | `01-frame/user-stories.md` |
| Architecture choices or implementation approach | `02-design/` |
| Detailed test cases and fixtures | `03-test/` |
| Build sequencing and execution slices | `04-build/implementation-plan.md` |

</details>

<details>
<summary>Quality checklist from the prompt</summary>

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] Problem section quantifies the pain or names a specific failure mode
- [ ] Every P0 requirement is testable (someone could write an acceptance test)
- [ ] Every P0 has an acceptance test sketch with inputs and expected outputs
- [ ] Success metrics have numeric targets and named measurement methods
- [ ] Requirements trace upward to the Product Vision and downward to downstream artifacts
- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers in any section except Open Questions
- [ ] Non-goals exclude something a reasonable person might assume is in scope
- [ ] Personas are specific enough to validate with a real user

### Warning

- [ ] Summary works as a standalone 1-pager (problem, solution, metrics)
- [ ] Goals describe state changes, not activities
- [ ] Risk mitigations are concrete actions, not "monitor"
- [ ] P0 requirements number 7 or fewer
- [ ] Assumptions are falsifiable

_Additional guidance continues in the full prompt below._

</details>

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.prd.depositmatch
  depends_on:
    - example.product-vision.depositmatch
  review:
    self_hash: c9c24e1694af4548a6deaad8d92059e365da110148bd9adc44d8640dff9770a4
    deps:
      example.product-vision.depositmatch: 8abbb2fcb552b536f07829f57d91ef3ae8dbf52a6066955222e83d196b59b5ae
    reviewed_at: "2026-05-15T04:11:24Z"
---
# Product Requirements Document

## Summary

DepositMatch is a reconciliation workspace for small bookkeeping firms. It
imports bank deposits and invoice exports, suggests likely matches, and gives
reviewers an exception queue for deposits that need human judgment. The first
release targets weekly reconciliation for firms serving recurring
small-business clients. Success means reviewers can close most clients in
minutes, trust the evidence behind accepted matches, and keep unresolved
deposits from disappearing into spreadsheets or email.

## Problem and Goals

### Problem

Bookkeeping firms with growing client rosters spend 4-8 hours each week
matching bank deposits to invoices across accounting exports, bank portals,
spreadsheets, and email threads. The work is repetitive, but mistakes are
expensive: a missed split payment or duplicate invoice can delay monthly close
and trigger client follow-up days later.

### Goals

1. Reviewers can reconcile routine deposits from one workspace.
2. Every accepted match has visible evidence and reviewer attribution.
3. Unclear deposits become owned exceptions with a next action.

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Median reconciliation time | Under 3 minutes per client per week | In-product workflow timing |
| Suggestion acceptance accuracy | 95% of accepted suggestions remain accepted in weekly audit sample | Reviewer audit |
| Exception ownership | 90% of unresolved deposits have owner and next action within one business day | Exception queue report |

### Non-Goals

- Replacing QuickBooks, Xero, or the firm's general ledger.
- Automatically posting journal entries.
- Supporting payroll, inventory, or tax workflows.
- Making irreversible match decisions without reviewer approval.

Deferred items tracked in `docs/helix/parking-lot.md`.

## Users and Scope

### Primary Persona: Maya, Reconciliation Lead

**Role**: Senior bookkeeper responsible for weekly reconciliation across 10-20
small-business clients.
**Goals**: Finish routine matching quickly, catch exceptions early, and leave a
clear audit trail for month-end review.
**Pain Points**: Rebuilding context across exports, losing client follow-up in
email, and repeating the same manual comparisons every week.

### Secondary Persona: Andre, Firm Owner

**Role**: Owner of a 12-person bookkeeping firm.
**Goals**: Increase client capacity without hiring another reviewer and reduce
month-end surprises.
**Pain Points**: Spreadsheet-based processes do not scale, and quality depends
too heavily on individual reviewer habits.

## Requirements

Each requirement traces to the Product Vision goal of reducing routine weekly
reconciliation time while preserving reviewer trust and exception ownership.

### Must Have (P0)

1. Import bank deposit CSV files and invoice export CSV files for a client.
2. Generate match suggestions using amount, date, payer, and invoice metadata.
3. Require reviewer approval before a suggested match becomes accepted.
4. Preserve match evidence, reviewer, timestamp, and source rows.
5. Create an exception for every unmatched or low-confidence deposit.

### Should Have (P1)

1. Support split deposits that pay multiple invoices.
2. Export a client-level reconciliation report.
3. Assign exception owners and due dates.

### Nice to Have (P2)

1. Bank feed integration.
2. Accounting platform API sync.
3. Client-facing question portal.

## Functional Requirements

### Import

- The system accepts CSV uploads for bank deposits and invoice exports.
- The user maps required columns on first import for each client.
- The system rejects files missing amount, date, and identifier columns.

### Match Review

- The system suggests matches with a confidence label and evidence summary.
- The reviewer can accept, reject, split, or flag each suggestion.
- Accepted matches are immutable except through a recorded correction.

### Exceptions

- The system creates an exception for every deposit without an accepted match.
- Each exception has status, owner, next action, and due date.
- Reviewers can export exceptions by client.

## Acceptance Test Sketches

| Requirement | Scenario | Input | Expected Output |
|-------------|----------|-------|-----------------|
| Import CSV files | Reviewer uploads bank and invoice exports | Two valid CSV files for one client | Imported deposits and invoices appear in review queue |
| Generate suggestions | Deposit amount and payer match open invoice | Deposit for 1200.00 from Acme Dental; invoice INV-104 for 1200.00 | High-confidence suggestion links deposit to invoice |
| Require approval | Reviewer views suggested match | Suggested match with evidence | Match remains pending until reviewer accepts |
| Preserve evidence | Reviewer accepts suggestion | Accepted match | Audit log records source rows, reviewer, timestamp, and evidence |
| Create exceptions | Deposit has no likely invoice | Deposit for 847.13 with no matching invoice | Exception is created with status `needs-review` |

## Technical Context

- **Language/Runtime**: TypeScript 5.x on Node 20+
- **Key Libraries**: React 18 for UI, Fastify 5 for API, Papa Parse for CSV
- **Data/Storage**: PostgreSQL 16
- **APIs**: Internal REST API; no external accounting API in v1
- **Platform Targets**: Modern desktop browsers; Chrome, Edge, Firefox, Safari

## Constraints, Assumptions, Dependencies

### Constraints

- **Technical**: CSV import is the only v1 data ingestion path.
- **Business**: First release must support a firm with up to 25 active clients.
- **Legal/Compliance**: Customer financial data must be encrypted at rest and
  excluded from analytics events.

### Assumptions

- Firms can export invoice data from their current accounting system.
- Weekly reconciliation is the first workflow worth optimizing.
- Reviewers will trust suggestions only when evidence is visible.

### Dependencies

- Sample CSV exports from at least three accounting systems.
- Security review for financial-data handling.
- Firm owner approval of audit-log retention policy.

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CSV formats vary too much across clients | High | Medium | Add per-client column mapping and save mappings after first import |
| Suggestions look opaque and reviewers reject them | Medium | High | Show amount, date, payer, and invoice evidence beside every suggestion |
| Split payments are common enough to block adoption | Medium | Medium | Include split deposit support as P1 before paid launch |

## Open Questions

- [ ] Which three accounting exports define the v1 CSV compatibility set? - ask pilot firms.
- [ ] What audit-log retention period do firms require? - ask firm owners and legal reviewer.
- [ ] Should low-confidence suggestions appear in review or go straight to exceptions? - ask pilot reviewers.

## Success Criteria

DepositMatch is successful when pilot firms reconcile routine weekly deposits
from one workspace, reviewers accept at least 95% of audited suggestions, and
unresolved deposits consistently leave a named owner and next action.
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/prd.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/frame/principles/">Principles</a><br><a href="/artifact-types/frame/feature-specification/">Feature Specification</a><br><a href="/artifact-types/frame/user-stories/">User Stories</a><br><a href="/artifact-types/frame/feature-registry/">Feature Registry</a></td></tr>
<tr><th>Referenced by</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/prd.md"><code>docs/helix/01-frame/prd.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># PRD Generation Prompt

Create a PRD that frames the problem, product scope, priorities, and success
criteria clearly enough that downstream feature specs, designs, tests, and
implementation work can trace back to it.

## Storage Location

Store at: `docs/helix/01-frame/prd.md`

## Purpose

The PRD is the **product-scope authority for what to build and why**. Its
unique job is to translate the Product Vision into prioritized, measurable
requirements and boundaries. It sits between the product vision (which defines
direction) and feature specs (which define feature-level detail). Every design
decision and implementation choice should trace back to a PRD requirement.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/atlassian-prd.md` frames a PRD as shared understanding of purpose, behavior, user needs, assumptions, out-of-scope items, and success criteria.
- `docs/resources/aha-prd-template.md` supports concise cross-functional scope: what is being built, who it is for, and how it delivers value.
- `docs/resources/ibm-requirements-management.md` grounds measurable, prioritized, traceable requirements and validation/verification discipline.

## Key Principles

- **Problem first** — the problem section should make someone feel the pain
  before they see the solution.
- **Decision-oriented** — every section should help someone make a build/skip
  decision. If a section doesn&#x27;t inform a decision, it&#x27;s filler.
- **Testable requirements** — every P0 requirement should be verifiable. If
  you can&#x27;t describe how to test it, it&#x27;s too vague.
- **Traceable boundaries** — requirements should connect upward to the Product
  Vision and downward to feature specs, designs, tests, and build work.
- **Honest non-goals** — non-goals should exclude things someone might
  reasonably expect to be in scope. &quot;Not a replacement for X&quot; only matters if
  someone might assume it is.

## Stay in Your Lane

Product requirements are for product scope. If you find yourself writing about:

| This content | Belongs in |
|---|---|
| Market sizing, ROI, investment case | `00-discover/business-case.md` |
| Positioning, target market, long-horizon strategic success | `00-discover/product-vision.md` |
| Detailed feature behavior and edge cases | `01-frame/features/FEAT-*.md` |
| User journey phrasing independent of product-level requirements | `01-frame/user-stories.md` |
| Architecture choices or implementation approach | `02-design/` |
| Detailed test cases and fixtures | `03-test/` |
| Build sequencing and execution slices | `04-build/implementation-plan.md` |

## Section-by-Section Guidance

### Summary
Write this last. This section must work as a **standalone 1-pager**: what
we&#x27;re building, who uses it, the problem, the solution approach, and the top
2-3 success metrics. Someone who reads only this section should understand the
product well enough to decide whether to invest time in the full PRD. Test:
could a new team member read this alone and explain the product to someone
else?

### Problem
Describe the failure mode, not the absence of your solution. &quot;Users don&#x27;t have
a X&quot; is weak. &quot;Users spend N hours/week doing Y manually because Z doesn&#x27;t
exist, leading to W failures&quot; is strong. Quantify where possible.

### Goals
Each goal should describe a state change, not an activity. &quot;Build a dashboard&quot;
is an activity. &quot;Operators can see system health without SSH&quot; is a state
change.

### Success Metrics
Every metric needs three things: what you&#x27;re measuring, a numeric target, and
how you&#x27;ll measure it. &quot;User satisfaction&quot; is not a metric. &quot;NPS &gt; 40 from
monthly survey of active users&quot; is. Drop the Timeline column — success metrics
should define what success looks like, not when it happens.

### Non-Goals
Each non-goal should prevent scope creep on something plausible. &quot;Not a
general-purpose AI&quot; is only useful if someone might think it is. Test: would
someone on the team argue for including this? If not, it&#x27;s not a useful
non-goal.

### Personas
Name them. Give them a role, goals, and pain points specific enough to
validate with a real person. &quot;Alex the Developer&quot; with generic goals is a
template, not a persona.

### Requirements (P0/P1/P2)
P0 = the product is broken without this. P1 = the product is weak without
this. P2 = the product is better with this. If you have more than 7 P0s,
you&#x27;re not prioritizing.

Each requirement should be stable enough to trace into feature specs and tests.
If a requirement describes a screen, algorithm, API field, or implementation
sequence in detail, move that detail downstream and keep the PRD at product
scope.

### Functional Requirements
These are the detailed behavioral specs. Each one should be testable — someone
reading it should know how to write an acceptance test.

**Group requirements under named subsystems.** Organize FRs by subsystem (not by
priority) under canonical, parseable headings: `### Subsystem: &lt;name&gt;`. Each
`FR-n` belongs to **exactly one** subsystem. A subsystem is a cohesive capability
of the product — the unit that becomes a feature: **one subsystem maps to ~one
feature spec** (`FEAT-NNN`). This is the PRD↔FEAT boundary — the PRD owns
*breadth* (it names every subsystem and enumerates all `FR-n` + priorities); the
feature spec owns *depth* (one subsystem&#x27;s behavior, ACs, edge cases). A
multi-subsystem product must not collapse into a single mega-feature, nor should
one subsystem fragment into many tiny features. (The feature spec&#x27;s Decomposition
test resolves borderline cases; reconcile-alignment checks that every subsystem
maps to a feature.)

Give each functional requirement a **stable `FR-n` ID** (`FR-1`, `FR-2`, …). The
ID is the trace anchor: every `FR-n` must be covered by ≥1 user story, and
reconcile-alignment flags any `FR-n` with no story as a coverage gap. Number
sequentially and never renumber on edit — downstream stories reference the ID by
name.

### Acceptance Test Sketches
For each P0 requirement, write a concrete scenario: what the user does, what
input they provide, and what observable result they see. These aren&#x27;t full test
cases — they&#x27;re the minimum an implementer (human or agent) needs to verify
the requirement is met. An AI agent should be able to read a sketch and write
a passing test without asking clarifying questions.

### Technical Context
Name the stack, key dependencies with versions, API schemas, and platform
targets. Be specific enough that an implementer knows what to install and what
interfaces to code against. &quot;React&quot; is not enough — &quot;React 18 with TypeScript
5.x and Vite 6&quot; is. If there&#x27;s an API schema (OpenAPI, GraphQL SDL), point to
it. This section exists because AI agents need concrete dependency and
interface information to produce correct implementations.

**Important**: This section records stack decisions — it does not make them.
Stack selection rationale belongs in ADRs (Architecture Decision Records). If
you&#x27;re documenting a choice that doesn&#x27;t have an ADR yet, note it in Open
Questions. If an existing ADR contradicts what you&#x27;d write here, the ADR
governs until it&#x27;s superseded.

### Constraints
Name real constraints, not aspirational ones. &quot;Must work on mobile&quot; is a
constraint only if you&#x27;d otherwise skip it. Budget, compliance, and platform
constraints matter most.

### Assumptions
These are bets. When an assumption is wrong, the plan breaks. Name each one
so the team knows what to watch.

### Risks
Each risk needs a concrete mitigation, not &quot;monitor closely.&quot; If the
mitigation is monitoring, say what you&#x27;ll monitor and what triggers action.

### Open Questions
List unresolved items explicitly rather than leaving `[TBD]` markers
scattered through the document. Each question should name who can answer it
and what&#x27;s blocked by it. This section is honest about what you don&#x27;t know
yet — it&#x27;s better to have a clear list of unknowns than a document that
pretends to be complete.

### Success Criteria
These are the acceptance criteria for the entire initiative. They should be
observable outcomes (&quot;operators can do X without Y&quot;) not activities (&quot;we
shipped Z&quot;).

## Quality Checklist

After drafting, verify every item. If any blocking check fails, revise before
committing.

### Blocking

- [ ] Problem section quantifies the pain or names a specific failure mode
- [ ] Every P0 requirement is testable (someone could write an acceptance test)
- [ ] Every P0 has an acceptance test sketch with inputs and expected outputs
- [ ] Success metrics have numeric targets and named measurement methods
- [ ] Requirements trace upward to the Product Vision and downward to downstream artifacts
- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers in any section except Open Questions
- [ ] Non-goals exclude something a reasonable person might assume is in scope
- [ ] Personas are specific enough to validate with a real user

### Warning

- [ ] Summary works as a standalone 1-pager (problem, solution, metrics)
- [ ] Goals describe state changes, not activities
- [ ] Risk mitigations are concrete actions, not &quot;monitor&quot;
- [ ] P0 requirements number 7 or fewer
- [ ] Assumptions are falsifiable
- [ ] Functional requirements are grouped under canonical `### Subsystem: &lt;name&gt;` headings (each `FR-n` under exactly one subsystem); each subsystem is a capability that maps to ~one feature spec
- [ ] Each functional requirement carries a stable `FR-n` ID for downstream story traceability
- [ ] Technical Context names specific versions, not just library names
- [ ] Open Questions name who can answer and what&#x27;s blocked</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: prd
---

# Product Requirements Document

## Summary

[This section should work as a standalone 1-pager. Include: what we&#x27;re
building, who uses it, what problem it solves, the solution approach, and the
top 2-3 success metrics. Write this last — it should be a distillation of the
full PRD, not an introduction. Someone who reads only this section should
understand the product well enough to decide whether to read the rest.]

## Problem and Goals

### Problem

[What is broken or missing? Who is affected? Be specific about the failure
mode — not &quot;users struggle with X&quot; but &quot;users spend N hours per week doing X
because Y doesn&#x27;t exist.&quot;]

### Goals

1. [Primary goal — what changes for users]
2. [Secondary goal]

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| [Metric] | [Numeric target] | [Named tool or process] |

### Non-Goals

[What we are explicitly not trying to achieve. Each non-goal should exclude
something a reasonable person might assume is in scope.]

Deferred items tracked in `docs/helix/parking-lot.md`.

## Users and Scope

### Primary Persona: [Name]

**Role**: [Job title/function]
**Goals**: [What they want to achieve]
**Pain Points**: [Current frustrations — specific enough to validate]

### Secondary Persona: [Name]

[Same structure]

## Requirements

Each requirement should trace to the Product Vision and be specific enough to
drive feature specs, designs, tests, and implementation work without embedding
the detailed design here.

### Must Have (P0)

1. [Core capability — what must be true for the product to be usable]

### Should Have (P1)

1. [Important feature — valuable but not blocking launch]

### Nice to Have (P2)

1. [Enhancement — improves experience but can be deferred]

## Functional Requirements

[Detailed behavioral requirements grouped under canonical `### Subsystem: &lt;name&gt;`
headings. Each requirement is testable, and each `FR-n` belongs to exactly one
subsystem. A subsystem is a cohesive product capability — the unit that maps to
~one feature spec (`FEAT-NNN`). The PRD owns breadth (all subsystems + `FR-n` +
priority); feature specs own each subsystem&#x27;s depth.

Each functional requirement carries a **stable `FR-n` ID** (e.g. `FR-1`). The ID
survives edits so downstream artifacts trace to a specific requirement by name:
every `FR-n` must map to ≥1 user story `US-n`, and reconcile-alignment checks that
mapping (and that each subsystem maps to a feature) as a coverage floor. Number
them sequentially; do not renumber on edit.]

### Subsystem: [Name — a cohesive capability that becomes ~one FEAT]

- **FR-1** — [behavioral requirement, testable]
- **FR-2** — [behavioral requirement, testable]

### Subsystem: [Name]

- **FR-3** — [behavioral requirement, testable]

## Acceptance Test Sketches

[For each P0 requirement, describe a concrete scenario with inputs and
expected outputs. These aren&#x27;t full test cases — they&#x27;re the minimum needed
for an implementer (human or agent) to verify the requirement is met.]

| Requirement | Scenario | Input | Expected Output |
|-------------|----------|-------|-----------------|
| [P0 requirement] | [What the user does] | [Specific input or state] | [Observable result] |

## Technical Context

[Stack, key dependencies with versions, API schemas, and platform targets.
Be specific enough that an implementer knows what to install and what
interfaces to code against. This section records current stack decisions — it
does not make them. Stack selection rationale belongs in ADRs. If a choice
here isn&#x27;t backed by an ADR yet, note it in Open Questions.]

- **Language/Runtime**: [e.g., TypeScript 5.x, Node 20+]
- **Key Libraries**: [e.g., React 18, Tailwind CSS 4]
- **Data/Storage**: [e.g., PostgreSQL 16, Redis 7]
- **APIs**: [e.g., OpenAPI spec at docs/api/v2.yaml]
- **Platform Targets**: [e.g., Linux, macOS; browser: Chrome/Firefox/Safari latest]

## Constraints, Assumptions, Dependencies

### Constraints

- **Technical**: [Platform or technology limits]
- **Business**: [Budget, timeline, resource limits]
- **Legal/Compliance**: [Regulatory requirements]

### Assumptions

- [Key assumptions — what must be true for this plan to work]

### Dependencies

- [External systems, teams, or artifacts this work depends on]

## Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk] | High/Med/Low | High/Med/Low | [Concrete strategy, not &quot;monitor&quot;] |

## Open Questions

[Unresolved items that need answers before or during implementation. Each
should name who can answer it and what&#x27;s blocked by it. Prefer explicit
questions here over `[TBD]` markers scattered through the document.]

- [ ] [Question] — blocks [what], ask [who]

## Success Criteria

[What must be true to call the initiative successful. These should be
observable outcomes, not activities.]

## Review Checklist

Use this checklist when reviewing a PRD artifact:

- [ ] Summary works as a standalone 1-pager — someone can decide whether to read the rest
- [ ] Problem statement describes a specific failure mode with concrete cost
- [ ] Goals are outcomes, not activities (&quot;users can X&quot; not &quot;we build Y&quot;)
- [ ] Success metrics have numeric targets and named measurement methods
- [ ] Non-goals exclude things a reasonable person might assume are in scope
- [ ] Personas have specific pain points, not generic descriptions
- [ ] P0 requirements are necessary for launch — removing any one makes the product unusable
- [ ] P1/P2 requirements are correctly prioritized relative to each other
- [ ] Every P0 requirement has an acceptance test sketch
- [ ] Requirements can trace upward to the Product Vision and downward to downstream artifacts
- [ ] Functional requirements are testable — each can be verified with specific inputs and expected outputs
- [ ] Each functional requirement carries a stable `FR-n` ID so user stories can trace to it by name
- [ ] Functional requirements are grouped under canonical `### Subsystem: &lt;name&gt;` headings, each `FR-n` under exactly one subsystem; each subsystem is a capability that maps to ~one feature spec
- [ ] Technical context names specific versions and interfaces, not vague technology areas
- [ ] Risks have concrete mitigations (&quot;we do X&quot;), not vague strategies (&quot;we monitor&quot;)
- [ ] Open questions name who can answer and what is blocked
- [ ] No contradictions between requirements sections
- [ ] PRD is consistent with the governing product vision</code></pre></details></td></tr>
</tbody>
</table>
