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

**(kind: data)** When `kind: data`, the PRD is the **data-product-scope
authority for what data to build and why**. Its job is to translate business
intent into data-centric requirements: data sources, consumer personas,
quality contracts, technical constraints (catalog, schema, medallion layer),
and measurable success metrics. It sits between the Product Vision and the
data-architecture artifact. Every data pipeline design choice and quality
expectation should trace back to a Data PRD requirement.

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
| Exact command invocations, CLI flags, endpoints, schemas, payloads, error codes, config keys, or adapter signatures | `02-design/contracts/` |
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
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Frame</strong></a> — Define what the system should do, for whom, and how success will be measured.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/01-frame/prd.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/frame/principles/">Principles</a><br><a href="../../../artifact-types/frame/feature-specification/">Feature Specification</a><br><a href="../../../artifact-types/frame/user-stories/">User Stories</a><br><a href="../../../artifact-types/frame/feature-registry/">Feature Registry</a></td></tr>
<tr><th>Referenced by</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/test/test-plan/">Test Plan</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/01-frame/prd.md"><code>docs/helix/01-frame/prd.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># PRD Generation Prompt&#10;&#10;Create a PRD that frames the problem, product scope, priorities, and success&#10;criteria clearly enough that downstream feature specs, designs, tests, and&#10;implementation work can trace back to it.&#10;&#10;## Variant Selection (`kind`)&#10;&#10;The PRD has two framing variants selected by the `kind` field in `meta.yml`:&#10;&#10;- **`kind: product`** (default) — frames general product requirements.&#10;- **`kind: data`** — frames a data product (pipeline, warehouse, data&#10;  platform, or data service) with data sources, consumers, quality&#10;  contracts, and platform context.&#10;&#10;The shape of the artifact is unified; sections marked **(kind: data)** below&#10;swap in the data-product framing when `kind: data`. Per ADR-008, both&#10;framings share one role and one template — pick the variant that matches the&#10;authored artifact and follow its conditional guidance.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/01-frame/prd.md` (for either variant).&#10;&#10;## Purpose&#10;&#10;The PRD is the **product-scope authority for what to build and why**. Its&#10;unique job is to translate the Product Vision into prioritized, measurable&#10;requirements and boundaries. It sits between the product vision (which defines&#10;direction) and feature specs (which define feature-level detail). Every design&#10;decision and implementation choice should trace back to a PRD requirement.&#10;&#10;**(kind: data)** When `kind: data`, the PRD is the **data-product-scope&#10;authority for what data to build and why**. Its job is to translate business&#10;intent into data-centric requirements: data sources, consumer personas,&#10;quality contracts, technical constraints (catalog, schema, medallion layer),&#10;and measurable success metrics. It sits between the Product Vision and the&#10;data-architecture artifact. Every data pipeline design choice and quality&#10;expectation should trace back to a Data PRD requirement.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/atlassian-prd.md` frames a PRD as shared understanding of purpose, behavior, user needs, assumptions, out-of-scope items, and success criteria.&#10;- `docs/resources/aha-prd-template.md` supports concise cross-functional scope: what is being built, who it is for, and how it delivers value.&#10;- `docs/resources/ibm-requirements-management.md` grounds measurable, prioritized, traceable requirements and validation/verification discipline.&#10;&#10;**(kind: data)** When `kind: data`, also use:&#10;&#10;- `docs/resources/databricks-unity-catalog.md` grounds data governance through unified catalog hierarchies (metastore → catalog → schema → volume/table).&#10;- `docs/resources/databricks-lakehouse-medallion-architecture.md` grounds medallion topology (Bronze/Silver/Gold) and layer responsibilities in a Lakehouse.&#10;- `docs/resources/databricks-sdp.md` grounds Databricks Semantic Data Platform governance, lineage, and quality contracts through `EXPECT ... ON VIOLATION ...` clauses and SDP-aware pipeline patterns.&#10;&#10;If you adopt this on another data platform, substitute Databricks concepts&#10;with the platform equivalent (Snowflake DB/Schema/Table; BigQuery&#10;Project/Dataset/Table; Snowpipe/Streaming Inserts for Auto Loader;&#10;dbt/Great Expectations for SDP `EXPECT` clauses). The medallion pattern&#10;applies universally.&#10;&#10;## Key Principles&#10;&#10;- **Problem first** — the problem section should make someone feel the pain&#10;  before they see the solution.&#10;- **Decision-oriented** — every section should help someone make a build/skip&#10;  decision. If a section doesn&#x27;t inform a decision, it&#x27;s filler.&#10;- **Testable requirements** — every P0 requirement should be verifiable. If&#10;  you can&#x27;t describe how to test it, it&#x27;s too vague.&#10;- **Traceable boundaries** — requirements should connect upward to the Product&#10;  Vision and downward to feature specs, designs, tests, and build work.&#10;- **Honest non-goals** — non-goals should exclude things someone might&#10;  reasonably expect to be in scope. &quot;Not a replacement for X&quot; only matters if&#10;  someone might assume it is.&#10;&#10;## Stay in Your Lane&#10;&#10;Product requirements are for product scope. If you find yourself writing about:&#10;&#10;| This content | Belongs in |&#10;|---|---|&#10;| Market sizing, ROI, investment case | `00-discover/business-case.md` |&#10;| Positioning, target market, long-horizon strategic success | `00-discover/product-vision.md` |&#10;| Detailed feature behavior and edge cases | `01-frame/features/FEAT-*.md` |&#10;| User journey phrasing independent of product-level requirements | `01-frame/user-stories.md` |&#10;| Exact command invocations, CLI flags, endpoints, schemas, payloads, error codes, config keys, or adapter signatures | `02-design/contracts/` |&#10;| Architecture choices or implementation approach | `02-design/` |&#10;| Detailed test cases and fixtures | `03-test/` |&#10;| Build sequencing and execution slices | `04-build/implementation-plan.md` |&#10;&#10;## Section-by-Section Guidance&#10;&#10;### Summary&#10;Write this last. This section must work as a **standalone 1-pager**: what&#10;we&#x27;re building, who uses it, the problem, the solution approach, and the top&#10;2-3 success metrics. Someone who reads only this section should understand the&#10;product well enough to decide whether to invest time in the full PRD. Test:&#10;could a new team member read this alone and explain the product to someone&#10;else?&#10;&#10;### Problem&#10;Describe the failure mode, not the absence of your solution. &quot;Users don&#x27;t have&#10;a X&quot; is weak. &quot;Users spend N hours/week doing Y manually because Z doesn&#x27;t&#10;exist, leading to W failures&quot; is strong. Quantify where possible.&#10;&#10;### Goals&#10;Each goal should describe a state change, not an activity. &quot;Build a dashboard&quot;&#10;is an activity. &quot;Operators can see system health without SSH&quot; is a state&#10;change.&#10;&#10;### Success Metrics&#10;Every metric needs three things: what you&#x27;re measuring, a numeric target, and&#10;how you&#x27;ll measure it. &quot;User satisfaction&quot; is not a metric. &quot;NPS &gt; 40 from&#10;monthly survey of active users&quot; is. Drop the Timeline column — success metrics&#10;should define what success looks like, not when it happens.&#10;&#10;**(kind: data)** When `kind: data`, frame metrics for the data product&#10;itself: throughput (rows/day), latency (max age end-to-end), quality score&#10;(percentage of expectations passing), cost per GB or per DBU, freshness-SLA&#10;compliance, and consumer satisfaction. Each metric still needs a numeric&#10;target and a named measurement method — e.g., &quot;SLA compliance &gt; 95% measured&#10;by on-time delivery vs. promised refresh cadence.&quot;&#10;&#10;### Non-Goals&#10;Each non-goal should prevent scope creep on something plausible. &quot;Not a&#10;general-purpose AI&quot; is only useful if someone might think it is. Test: would&#10;someone on the team argue for including this? If not, it&#x27;s not a useful&#10;non-goal.&#10;&#10;### Personas&#10;Name them. Give them a role, goals, and pain points specific enough to&#10;validate with a real person. &quot;Alex the Developer&quot; with generic goals is a&#10;template, not a persona.&#10;&#10;**(kind: data)** When `kind: data`, frame this section as **Data Consumers**&#10;instead of personas. Name actual teams, systems, or roles that consume the&#10;data, their use case (what decisions they make), their freshness/latency SLA,&#10;the key dimensions they query, and their access level (row, column, full).&#10;Add an inventory of upstream **Data Sources** in a parallel section: source&#10;system, schema/table, owner, update frequency, quality baseline, and notes&#10;on API limits or retry policy. Generic personas are insufficient for a data&#10;product — the consumer and source tables drive every downstream design and&#10;quality decision.&#10;&#10;### Requirements (P0/P1/P2)&#10;P0 = the product is broken without this. P1 = the product is weak without&#10;this. P2 = the product is better with this. If you have more than 7 P0s,&#10;you&#x27;re not prioritizing.&#10;&#10;Each requirement should be stable enough to trace into feature specs and tests.&#10;If a requirement describes a screen, algorithm, API field, command flag,&#10;payload, error code, or implementation sequence in detail, move that detail to&#10;the owning downstream artifact and keep the PRD at product scope. Exact&#10;interface surface belongs in a Contract.&#10;&#10;### Functional Requirements&#10;Functional requirements are product-level capability and outcome requirements&#10;grouped by subsystem. Each one should be testable without defining exact&#10;interface, API, CLI, event, schema, config, telemetry, or adapter surface.&#10;&#10;**(kind: data)** When `kind: data`, the functional requirements describe&#10;**data behavior**: ingestion cadence, deduplication rules, transformation&#10;contracts, freshness windows, schema-evolution policy, and consumer-facing&#10;table or feed definitions. Add a **Data Quality Requirements** subsection&#10;with quality dimensions (completeness, timeliness, accuracy, uniqueness)&#10;each carrying a P0 threshold, a P1 threshold, a measurement method, and an&#10;enforcement strategy (alert, reject, quarantine). Reference the&#10;`data-quality-expectations` artifact for executable `EXPECT` clauses per&#10;medallion layer; the PRD owns the requirement, the expectations artifact&#10;owns the contract.&#10;&#10;**Group requirements under named subsystems.** Organize FRs by subsystem (not by&#10;priority) under canonical, parseable headings: `### Subsystem: &lt;name&gt;`. Each&#10;`FR-n` belongs to **exactly one** subsystem. A subsystem is a cohesive capability&#10;of the product — the unit that becomes a feature: **one subsystem maps to ~one&#10;feature spec** (`FEAT-NNN`). This is the PRD↔FEAT boundary — the PRD owns&#10;*breadth* (it names every subsystem and enumerates all `FR-n` + priorities); the&#10;feature spec owns *depth* (one subsystem&#x27;s behavior, ACs, edge cases). A&#10;multi-subsystem product must not collapse into a single mega-feature, nor should&#10;one subsystem fragment into many tiny features. (The feature spec&#x27;s Decomposition&#10;test resolves borderline cases; reconcile-alignment checks that every subsystem&#10;maps to a feature.)&#10;&#10;Give each functional requirement a **stable `FR-n` ID** (`FR-1`, `FR-2`, …). The&#10;ID is the trace anchor: every `FR-n` must be covered by ≥1 user story, and&#10;reconcile-alignment flags any `FR-n` with no story as a coverage gap. Number&#10;sequentially and never renumber on edit — downstream stories reference the ID by&#10;name.&#10;&#10;**Surface boundary example.** Do not write a PRD requirement as&#10;``FR-1: `tool autotune --gpu-tier high --write-config` writes config.toml``.&#10;Write the product requirement as `FR-1: Operators can generate a validated&#10;runtime profile for the selected hardware tier and persist it for future runs`,&#10;then add a handoff or link to a Contract for the exact command, flags, config&#10;keys, exit codes, and compatibility rules.&#10;&#10;### Acceptance Test Sketches&#10;For each P0 requirement, write a concrete scenario: what the user does, what&#10;input they provide, and what observable result they see. These aren&#x27;t full test&#10;cases — they&#x27;re the minimum an implementer (human or agent) needs to verify&#10;the requirement is met. An AI agent should be able to read a sketch and write&#10;a passing test without asking clarifying questions.&#10;&#10;### Technical Context&#10;Name the stack, key dependencies with versions, API schemas, and platform&#10;targets. Be specific enough that an implementer knows what to install and what&#10;interfaces to code against. &quot;React&quot; is not enough — &quot;React 18 with TypeScript&#10;5.x and Vite 6&quot; is. If there&#x27;s an API schema (OpenAPI, GraphQL SDL), point to&#10;it. This section exists because AI agents need concrete dependency and&#10;interface information to produce correct implementations.&#10;&#10;**Important**: This section records stack decisions — it does not make them.&#10;Stack selection rationale belongs in ADRs (Architecture Decision Records). If&#10;you&#x27;re documenting a choice that doesn&#x27;t have an ADR yet, note it in Open&#10;Questions. If an existing ADR contradicts what you&#x27;d write here, the ADR&#10;governs until it&#x27;s superseded.&#10;&#10;**(kind: data)** When `kind: data`, frame the technical context as the&#10;**data-platform context**: target catalog and schema (e.g., `prod.customer_360`),&#10;medallion layer strategy (Bronze/Silver/Gold scopes and responsibilities),&#10;ingestion pattern (Auto Loader, Streaming Tables, batch), processing model&#10;(streaming vs batch vs incremental), compute tier (all-purpose, jobs,&#10;serverless), storage format (Delta, Parquet), DBU budget assumption, and&#10;governance posture (data classification, retention policy, audit trail,&#10;lineage). Pin the access-control model: row-level security, column masking,&#10;and the catalog policies that enforce it. Same ADR discipline applies — the&#10;PRD records platform decisions, ADRs justify them.&#10;&#10;### Constraints&#10;Name real constraints, not aspirational ones. &quot;Must work on mobile&quot; is a&#10;constraint only if you&#x27;d otherwise skip it. Budget, compliance, and platform&#10;constraints matter most.&#10;&#10;### Assumptions&#10;These are bets. When an assumption is wrong, the plan breaks. Name each one&#10;so the team knows what to watch.&#10;&#10;### Risks&#10;Each risk needs a concrete mitigation, not &quot;monitor closely.&quot; If the&#10;mitigation is monitoring, say what you&#x27;ll monitor and what triggers action.&#10;&#10;### Open Questions&#10;List unresolved items explicitly rather than leaving `[TBD]` markers&#10;scattered through the document. Each question should name who can answer it&#10;and what&#x27;s blocked by it. This section is honest about what you don&#x27;t know&#10;yet — it&#x27;s better to have a clear list of unknowns than a document that&#10;pretends to be complete.&#10;&#10;### Success Criteria&#10;These are the acceptance criteria for the entire initiative. They should be&#10;observable outcomes (&quot;operators can do X without Y&quot;) not activities (&quot;we&#10;shipped Z&quot;).&#10;&#10;## Quality Checklist&#10;&#10;After drafting, verify every item. If any blocking check fails, revise before&#10;committing.&#10;&#10;### Blocking&#10;&#10;- [ ] Problem section quantifies the pain or names a specific failure mode&#10;- [ ] Every P0 requirement is testable (someone could write an acceptance test)&#10;- [ ] Every P0 has an acceptance test sketch with inputs and expected outputs&#10;- [ ] Success metrics have numeric targets and named measurement methods&#10;- [ ] Requirements trace upward to the Product Vision and downward to downstream artifacts&#10;- [ ] No `[TBD]`, `[TODO]`, or `[NEEDS CLARIFICATION]` markers in any section except Open Questions&#10;- [ ] Non-goals exclude something a reasonable person might assume is in scope&#10;- [ ] Personas are specific enough to validate with a real user&#10;&#10;### Warning&#10;&#10;- [ ] Summary works as a standalone 1-pager (problem, solution, metrics)&#10;- [ ] Goals describe state changes, not activities&#10;- [ ] Risk mitigations are concrete actions, not &quot;monitor&quot;&#10;- [ ] P0 requirements number 7 or fewer&#10;- [ ] Assumptions are falsifiable&#10;- [ ] Functional requirements are grouped under canonical `### Subsystem: &lt;name&gt;` headings (each `FR-n` under exactly one subsystem); each subsystem is a capability that maps to ~one feature spec&#10;- [ ] Each functional requirement carries a stable `FR-n` ID for downstream story traceability&#10;- [ ] Technical Context names specific versions, not just library names&#10;- [ ] Open Questions name who can answer and what&#x27;s blocked</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: prd&#10;kind: product  # `product` (default) frames general product requirements; `data` frames a data product (pipeline, warehouse, data platform, or service). See ADR-008.&#10;---&#10;&#10;# Product Requirements Document&#10;&#10;&gt; **Variant guidance.** This template carries both the default `product`&#10;&gt; framing and a `data` framing. Sections marked **(kind: data)** apply when&#10;&gt; `kind: data` and replace the corresponding `product` framing above them.&#10;&gt; When `kind: product`, ignore the **(kind: data)** blocks. The shape of the&#10;&gt; document is the same; the framing is parameterized.&#10;&#10;## Summary&#10;&#10;[This section should work as a standalone 1-pager. Include: what we&#x27;re&#10;building, who uses it, what problem it solves, the solution approach, and the&#10;top 2-3 success metrics. Write this last — it should be a distillation of the&#10;full PRD, not an introduction. Someone who reads only this section should&#10;understand the product well enough to decide whether to read the rest.&#10;&#10;**(kind: data)** Frame this as a standalone 1-pager for the **data product**:&#10;what data we are building, who consumes it, the business problem it solves,&#10;the data solution approach (sources, medallion layer strategy, consumption&#10;shape), and the top 2-3 success metrics (freshness, quality, cost).]&#10;&#10;## Problem and Goals&#10;&#10;### Problem&#10;&#10;[What is broken or missing? Who is affected? Be specific about the failure&#10;mode — not &quot;users struggle with X&quot; but &quot;users spend N hours per week doing X&#10;because Y doesn&#x27;t exist.&quot;&#10;&#10;**(kind: data)** Be specific about the data failure mode — not &quot;users&#10;struggle with reporting&quot; but &quot;sales analysts spend 4 hours per week&#10;reconciling pipeline outputs with source systems because current freshness&#10;is 24 hours and source data changes hourly.&quot;]&#10;&#10;### Goals&#10;&#10;1. [Primary goal — what changes for users]&#10;2. [Secondary goal]&#10;&#10;### Success Metrics&#10;&#10;| Metric | Target | Measurement Method |&#10;|--------|--------|--------------------|&#10;| [Metric] | [Numeric target] | [Named tool or process] |&#10;&#10;**(kind: data)** When `kind: data`, frame metrics for the data product&#10;itself (throughput, latency, quality score, cost per GB). Include a baseline&#10;and cadence column:&#10;&#10;| Metric | Target | Baseline | Measurement Method | Cadence |&#10;|--------|--------|----------|--------------------|---------|&#10;| [Throughput] | [e.g., 1M rows/day] | [Current: 100K rows/day] | [COUNT(*) from production table] | Daily |&#10;| [Latency] | [e.g., ≤1 hour end-to-end] | [Current: 4 hours] | [MAX(ingestion_timestamp) - MAX(source_timestamp)] | Hourly |&#10;| [Quality Score] | [e.g., ≥98%] | [Current: 85%] | [Automated quality checks pass rate] | Daily |&#10;| [Cost per GB] | [e.g., $0.05/GB/month] | [Current: $0.12/GB/month] | [DBU spend / data volume] | Monthly |&#10;&#10;### Non-Goals&#10;&#10;[What we are explicitly not trying to achieve. Each non-goal should exclude&#10;something a reasonable person might assume is in scope.]&#10;&#10;Deferred items tracked in `docs/helix/parking-lot.md`.&#10;&#10;## Users and Scope&#10;&#10;### Primary Persona: [Name]&#10;&#10;**Role**: [Job title/function]&#10;**Goals**: [What they want to achieve]&#10;**Pain Points**: [Current frustrations — specific enough to validate]&#10;&#10;### Secondary Persona: [Name]&#10;&#10;[Same structure]&#10;&#10;### (kind: data) Data Consumers&#10;&#10;[When `kind: data`, replace the persona blocks with concrete data consumers.]&#10;&#10;#### Primary Consumer: [Name/Role]&#10;&#10;**Team**: [Data Engineering, Analytics, Product, Finance, etc.]&#10;**Use Case**: [What they do with the data; what decision it informs]&#10;**Frequency**: [Real-time, daily, weekly, ad-hoc]&#10;**Key Tables/Feeds**: [Which outputs matter most]&#10;&#10;#### Data Consumer Requirements Table&#10;&#10;| Consumer | Use Case | Freshness SLA | Latency Tolerance | Key Dimensions | Access Level |&#10;|----------|----------|---------------|-------------------|----------------|--------------|&#10;| [Team] | [What they do] | [e.g., hourly] | [max delay] | [customer_id, product_id, ...] | [Row-level, Column-level, or Full] |&#10;&#10;### (kind: data) Data Sources&#10;&#10;[Inventory of upstream systems supplying this data product.]&#10;&#10;| Source System | Schema / Table | Owner | Update Frequency | Quality Baseline | Notes |&#10;|---------------|----------------|-------|------------------|------------------|-------|&#10;| [e.g., Salesforce] | [e.g., Accounts, Opportunities] | [Team] | [hourly, daily, on-demand] | [% completeness, freshness] | [Data model version, API limits, retry policy] |&#10;&#10;## Requirements&#10;&#10;Each requirement should trace to the Product Vision and be specific enough to&#10;drive feature specs, designs, tests, and implementation work without embedding&#10;the detailed design here. Exact command invocations, CLI flags, endpoints,&#10;schemas, payloads, error codes, config keys, telemetry fields, event shapes,&#10;and adapter signatures belong in `02-design/contracts/`, not in PRD&#10;requirements.&#10;&#10;### Must Have (P0)&#10;&#10;1. [Core capability — what must be true for the product to be usable]&#10;&#10;### Should Have (P1)&#10;&#10;1. [Important feature — valuable but not blocking launch]&#10;&#10;### Nice to Have (P2)&#10;&#10;1. [Enhancement — improves experience but can be deferred]&#10;&#10;## Functional Requirements&#10;&#10;[Product-level capability and outcome requirements grouped under canonical&#10;`### Subsystem: &lt;name&gt;` headings. Each requirement is testable without defining&#10;exact API, CLI, event, schema, config, telemetry, or adapter surface. Each&#10;`FR-n` belongs to exactly one subsystem. A subsystem is a cohesive product&#10;capability — the unit that maps to ~one feature spec (`FEAT-NNN`). The PRD owns&#10;breadth (all subsystems + `FR-n` + priority); feature specs own each subsystem&#x27;s&#10;depth, and Contracts own exact shared interface surfaces.&#10;&#10;Each functional requirement carries a **stable `FR-n` ID** (e.g. `FR-1`). The ID&#10;survives edits so downstream artifacts trace to a specific requirement by name:&#10;every `FR-n` must map to ≥1 user story `US-n`, and reconcile-alignment checks that&#10;mapping (and that each subsystem maps to a feature) as a coverage floor. Number&#10;them sequentially; do not renumber on edit.]&#10;&#10;### Subsystem: [Name — a cohesive capability that becomes ~one FEAT]&#10;&#10;- **FR-1** — [product capability or outcome requirement, testable]&#10;- **FR-2** — [product capability or outcome requirement, testable]&#10;&#10;### Subsystem: [Name]&#10;&#10;- **FR-3** — [product capability or outcome requirement, testable]&#10;&#10;### (kind: data) Data Quality Requirements&#10;&#10;[When `kind: data`, add this subsection. Quality dimensions with numeric&#10;thresholds and enforcement strategy. Reference `data-quality-expectations`&#10;for executable `EXPECT` clauses per medallion layer.]&#10;&#10;| Dimension | P0 Threshold | P1 Threshold | Measurement Method | Enforcement |&#10;|-----------|--------------|--------------|--------------------|-------------|&#10;| Completeness | [e.g., ≥99%] | [e.g., ≥95%] | [Count NULLs / total rows] | [Alert if below P0] |&#10;| Timeliness | [e.g., ≤1 hour lag] | [e.g., ≤4 hour lag] | [MAX(ingestion_time) - MAX(source_time)] | [Reject data if exceeds P0] |&#10;| Accuracy | [e.g., ≥98% match to source] | [e.g., ≥95% match] | [Row-count reconciliation + sample audit] | [Manual review + auto-reject if P0 fails] |&#10;| Uniqueness | [e.g., PK has no duplicates] | [as P0] | [COUNT(*) = COUNT(DISTINCT PK)] | [Fail ingestion] |&#10;&#10;## Acceptance Test Sketches&#10;&#10;[For each P0 requirement, describe a concrete scenario with inputs and&#10;expected outputs. These aren&#x27;t full test cases — they&#x27;re the minimum needed&#10;for an implementer (human or agent) to verify the requirement is met.]&#10;&#10;| Requirement | Scenario | Input | Expected Output |&#10;|-------------|----------|-------|-----------------|&#10;| [P0 requirement] | [What the user does] | [Specific input or state] | [Observable result] |&#10;&#10;## Technical Context&#10;&#10;[Stack, key dependencies with versions, API schemas, and platform targets.&#10;Be specific enough that an implementer knows what to install and what&#10;interfaces to code against. This section records current stack decisions — it&#10;does not make them. Stack selection rationale belongs in ADRs. If a choice&#10;here isn&#x27;t backed by an ADR yet, note it in Open Questions.]&#10;&#10;- **Language/Runtime**: [e.g., TypeScript 5.x, Node 20+]&#10;- **Key Libraries**: [e.g., React 18, Tailwind CSS 4]&#10;- **Data/Storage**: [e.g., PostgreSQL 16, Redis 7]&#10;- **APIs**: [e.g., OpenAPI spec at docs/api/v2.yaml]&#10;- **Platform Targets**: [e.g., Linux, macOS; browser: Chrome/Firefox/Safari latest]&#10;&#10;### (kind: data) Data Platform Context&#10;&#10;[When `kind: data`, replace the stack list above with platform context.]&#10;&#10;- **Target Catalog**: [e.g., `prod`, `analytics`, or domain-specific catalog]&#10;- **Target Schema**: [e.g., `customer_360`, `payment_events`]&#10;- **Medallion Layers**: Bronze (raw), Silver (validated), Gold (business)&#10;- **Access Control Model**: [UC policies, row-level security, column masking]&#10;&#10;| Feature | Decision | Rationale |&#10;|---------|----------|-----------|&#10;| Ingestion Pattern | [Auto Loader, Streaming Tables, batch] | [Why this choice?] |&#10;| Processing Model | [Streaming, Batch, Incremental] | [Freshness SLA and cost tradeoff] |&#10;| Compute Tier | [All-purpose, Jobs, Serverless] | [Workload characteristics, cost model] |&#10;| Storage Format | [Delta, Parquet, CSV] | [Durability, query performance needs] |&#10;| DBU Budget (Monthly) | [Estimated spend] | [Based on row volume, freshness, complexity] |&#10;&#10;- **Data Classification**: [Public, Internal, Sensitive, PII]&#10;- **Retention Policy**: [e.g., Bronze: 7 days, Silver: 90 days, Gold: 2 years]&#10;- **Audit Trail**: [Who accessed what, when, why]&#10;- **Lineage Tracking**: [Table-to-table dependencies for impact analysis]&#10;&#10;## Constraints, Assumptions, Dependencies&#10;&#10;### Constraints&#10;&#10;- **Technical**: [Platform or technology limits]&#10;- **Business**: [Budget, timeline, resource limits]&#10;- **Legal/Compliance**: [Regulatory requirements]&#10;&#10;### Assumptions&#10;&#10;- [Key assumptions — what must be true for this plan to work]&#10;&#10;### Dependencies&#10;&#10;- [External systems, teams, or artifacts this work depends on]&#10;&#10;## Risks&#10;&#10;| Risk | Probability | Impact | Mitigation |&#10;|------|-------------|--------|------------|&#10;| [Risk] | High/Med/Low | High/Med/Low | [Concrete strategy, not &quot;monitor&quot;] |&#10;&#10;## Open Questions&#10;&#10;[Unresolved items that need answers before or during implementation. Each&#10;should name who can answer it and what&#x27;s blocked by it. Prefer explicit&#10;questions here over `[TBD]` markers scattered through the document.]&#10;&#10;- [ ] [Question] — blocks [what], ask [who]&#10;&#10;## Success Criteria&#10;&#10;[What must be true to call the initiative successful. These should be&#10;observable outcomes, not activities.]&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing a PRD artifact:&#10;&#10;- [ ] Summary works as a standalone 1-pager — someone can decide whether to read the rest&#10;- [ ] Problem statement describes a specific failure mode with concrete cost&#10;- [ ] Goals are outcomes, not activities (&quot;users can X&quot; not &quot;we build Y&quot;)&#10;- [ ] Success metrics have numeric targets and named measurement methods&#10;- [ ] Non-goals exclude things a reasonable person might assume are in scope&#10;- [ ] Personas have specific pain points, not generic descriptions&#10;- [ ] P0 requirements are necessary for launch — removing any one makes the product unusable&#10;- [ ] P1/P2 requirements are correctly prioritized relative to each other&#10;- [ ] Every P0 requirement has an acceptance test sketch&#10;- [ ] Requirements can trace upward to the Product Vision and downward to downstream artifacts&#10;- [ ] Functional requirements are testable — each can be verified with specific inputs and expected outputs&#10;- [ ] Each functional requirement carries a stable `FR-n` ID so user stories can trace to it by name&#10;- [ ] Functional requirements are grouped under canonical `### Subsystem: &lt;name&gt;` headings, each `FR-n` under exactly one subsystem; each subsystem is a capability that maps to ~one feature spec&#10;- [ ] Technical context names specific versions and interfaces, not vague technology areas&#10;- [ ] Risks have concrete mitigations (&quot;we do X&quot;), not vague strategies (&quot;we monitor&quot;)&#10;- [ ] Open questions name who can answer and what is blocked&#10;- [ ] No contradictions between requirements sections&#10;- [ ] PRD is consistent with the governing product vision</code></pre></details></td></tr>
</tbody>
</table>
