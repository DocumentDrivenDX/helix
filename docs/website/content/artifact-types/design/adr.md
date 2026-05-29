---
title: "Architecture Decision Record"
linkTitle: "ADR"
slug: adr
activity: "Design"
artifactRole: "core"
weight: 11
generated: true
---

## Purpose

An ADR is the **single-decision record** for architecture-significant choices.
Its unique job is to preserve why a decision was made, what alternatives were
considered, what tradeoffs were accepted, and when the decision should be
revisited.

ADRs are not architecture documents. Architecture owns the overall structural
model. ADRs are not solution designs or technical designs; those apply accepted
decisions to narrower scopes. ADRs are not meeting notes; keep only the context
that changes how future readers should evaluate the decision.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: example.adr.depositmatch.postgresql-system-of-record
  depends_on:
    - example.architecture.depositmatch
  review:
    self_hash: d068dcadcfb1b7b4cfa6842e63e078f711128e78d5c2dd7e1666506a7c59d9ad
    deps:
      example.architecture.depositmatch: 64b7297158175ff16812e401fe093f7624b5ba70b11265a7a4bdf324e50a6bff
    reviewed_at: "2026-05-15T04:11:24Z"
---

# ADR-001: Use PostgreSQL as the System of Record

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| 2026-05-12 | Accepted | Product and Engineering | FEAT-001, Architecture | High |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | DepositMatch must preserve imports, source rows, match suggestions, reviewer decisions, exceptions, and audit evidence consistently. |
| Current State | v1 starts from CSV imports and does not use external accounting APIs or bank feeds. |
| Requirements | PRD P0-1 import CSV files; P0-3 require reviewer approval; P0-4 preserve match evidence; P0-5 create exceptions for unmatched deposits. |
| Decision Drivers | Auditability, transactional consistency, simple v1 operations, and fast pilot delivery matter more than independent scaling of each data type. |

## Decision

We will use PostgreSQL 16 as the system of record for DepositMatch v1 data,
including clients, import sessions, source rows, invoices, deposits, match
suggestions, reviewer decisions, exceptions, and audit-log records.

**Key Points**: one transactional store | source-row traceability | no separate
search or document store in v1

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| PostgreSQL 16 | Strong transactions, relational constraints, straightforward audit queries, mature backups, simple v1 operations | Less specialized for full-text search or high-volume event streaming | **Selected**: best fit for consistency and pilot simplicity |
| Document database | Flexible import payload storage, fewer joins for nested evidence | Harder relational integrity for invoices, deposits, matches, and corrections | Rejected: flexibility is less important than audit consistency |
| Separate event store plus read models | Excellent history and replay model | More infrastructure, more operational complexity, slower pilot delivery | Rejected for v1: event sourcing may be revisited if audit replay needs exceed relational history |

## Consequences

| Type | Impact |
|------|--------|
| Positive | Imports, matches, exceptions, and audit records can commit atomically and be queried together. |
| Negative | Future high-volume matching or analytics may need read replicas or separate derived stores. |
| Neutral | Uploaded CSV originals still live in encrypted object storage; PostgreSQL stores metadata and normalized rows. |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| Import and match tables grow faster than expected | M | M | Partition or archive import sessions after retention policy is defined; add read replica if reporting load grows. |
| Analytics needs pressure the transactional schema | M | L | Keep analytics derived; do not put raw financial fields into analytics events. |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| 100% of accepted rows used in match evidence include source file, row number, identifier, amount, and date | Any accepted match lacks source-row evidence |
| Import confirmation remains atomic under validation and worker failures | Any partial import commit is observed in testing or production |
| Pilot workload stays below PostgreSQL performance targets | Matching backlog exceeds 100 jobs for 5 minutes repeatedly |

## Supersession

- **Supersedes**: None
- **Superseded by**: None

## Concern Impact

- **Concern selection**: Reinforces `reviewer-auditability`,
  `csv-import-integrity`, and `financial-data-security`.
- **Practice override**: None.

## References

- Architecture: `example.architecture.depositmatch`
- Feature Specification: `example.feature-specification.depositmatch.csv-import`
- PRD requirements: P0-1, P0-3, P0-4, P0-5
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/adr/ADR-{number}-{decision-name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/solution-design/">Solution Design</a><br><a href="../../../artifact-types/design/technical-design/">Technical Design</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/adr/ADR-002-tracker-write-safety-model.md"><code>docs/helix/02-design/adr/ADR-002-tracker-write-safety-model.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Architecture Decision Record (ADR) Generation Prompt&#10;&#10;Write a compact ADR that captures one architecture-significant decision, the&#10;alternatives, and the consequences.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/02-design/adr/ADR-NNN-&lt;decision-name&gt;.md` — **one decision&#10;per file**. Naming is canonical and checkable: uppercase `ADR`, a **zero-padded&#10;3-digit** sequential number, then a kebab-case decision name (e.g.&#10;`ADR-001-modular-monolith.md`, `ADR-007-auth-tenant-isolation.md`). Do **not** use&#10;lowercase `adr-` or 4-digit numbers, and do **not** lump multiple decisions into&#10;one record. reconcile-alignment flags non-canonical names and lumped ADRs.&#10;&#10;## Purpose&#10;&#10;An ADR is the **single-decision record** for architecture-significant choices.&#10;Its unique job is to preserve why a decision was made, what alternatives were&#10;considered, what tradeoffs were accepted, and when the decision should be&#10;revisited.&#10;&#10;ADRs are not architecture documents. Architecture owns the overall structural&#10;model. ADRs are not solution designs or technical designs; those apply accepted&#10;decisions to narrower scopes. ADRs are not meeting notes; keep only the context&#10;that changes how future readers should evaluate the decision.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/adr-github-organization.md` grounds ADRs as&#10;  single-decision records with rationale, tradeoffs, and consequences.&#10;- `docs/resources/google-cloud-architecture-decision-records.md` grounds ADR&#10;  traceability to architecture evolution, code, and infrastructure context.&#10;&#10;## Focus&#10;- State the context and decision plainly.&#10;- Keep alternatives and tradeoffs honest but brief.&#10;- Note validation and references only if they affect the decision.&#10;- Use one ADR per decision. If the decision has independent parts, split it.&#10;- Treat accepted ADRs as history. New decisions supersede old records instead&#10;  of rewriting them.&#10;- **Do not accept a decision whose design-defining facts are assumed.** A&#10;  decision&#x27;s design-defining facts (API shape, data model, pricing/cost&#10;  semantics, security/permissions, operational guarantees, or work decomposition)&#10;  must be **evidenced** — by an operator statement, a governing artifact, an&#10;  existing implementation, a docs/API proof, or a completed spike — not by model&#10;  familiarity, and not because a mechanism was picked or a provider named.&#10;  Choosing a provider and deferring its live integration does **not** evidence the&#10;  decision. If a design-defining fact is assumed, the ADR must cite **spike&#10;  evidence**, record a **blocked-spike rationale**, or carry an explicit&#10;  **provisional-risk** note (what is assumed, what could invalidate it, and that&#10;  the assumption is reversible/non-blocking). See the anti-reframe check in&#10;  `workflows/references/concern-resolution.md` (step 3a). An operator-marked&#10;  &quot;spike/unknown&quot; may not be accepted as a settled ADR without **spike evidence, a&#10;  blocked-spike rationale, or an explicit provisional-risk note**. A&#10;  **business/product** unknown a technical spike can&#x27;t answer (e.g. a pricing&#10;  model) → record **guidance-needed** or a blocked spike rather than forcing a&#10;  technical spike or accepting an assumed decision.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Overall system structure or deployment topology | Architecture |&#10;| One architecture-significant decision and rationale | ADR |&#10;| Feature-specific design applying accepted architecture | Solution Design |&#10;| Story-level component or code plan | Technical Design |&#10;| API schema, event payload, or file format | Contract |&#10;| Work steps or sequencing | Implementation Plan |&#10;&#10;## Completion Criteria&#10;- The decision is unambiguous.&#10;- Alternatives are compared clearly.&#10;- Consequences are explicit.&#10;- Status and supersession state are clear.&#10;- Reconsideration triggers are concrete when the decision has uncertainty.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: ADR-XXX&#10;---&#10;&#10;# ADR-NNN: [Title]&#10;&lt;!-- Filename: ADR-NNN-&lt;decision-name&gt;.md — uppercase ADR, zero-padded 3-digit, one decision per file. --&gt;&#10;&#10;&#10;| Date | Status | Deciders | Related | Confidence |&#10;|------|--------|----------|---------|------------|&#10;| [YYYY-MM-DD] | [Proposed/Accepted/Deprecated/Superseded] | [Names] | [FEAT-XXX] | [High/Med/Low] |&#10;&#10;## Context&#10;&#10;| Aspect | Description |&#10;|--------|-------------|&#10;| Problem | [Specific problem] |&#10;| Current State | [Existing situation] |&#10;| Requirements | [Key requirements driving this] |&#10;| Decision Drivers | [Forces that make this architecture-significant] |&#10;&#10;## Decision&#10;&#10;We will [decision statement].&#10;&#10;**Key Points**: [Point 1] | [Point 2] | [Point 3]&#10;&#10;## Alternatives&#10;&#10;| Option | Pros | Cons | Evaluation |&#10;|--------|------|------|------------|&#10;| [Option 1] | [Advantages] | [Disadvantages] | [Rejected: reason] |&#10;| [Option 2] | [Advantages] | [Disadvantages] | [Rejected: reason] |&#10;| **[Selected]** | [Advantages] | [Disadvantages + mitigations] | **Selected: reason** |&#10;&#10;## Consequences&#10;&#10;| Type | Impact |&#10;|------|--------|&#10;| Positive | [Good outcomes] |&#10;| Negative | [Trade-offs, technical debt] |&#10;| Neutral | [Side effects] |&#10;&#10;## Risks&#10;&#10;| Risk | Prob | Impact | Mitigation |&#10;|------|------|--------|------------|&#10;| [Risk 1] | H/M/L | H/M/L | [Strategy] |&#10;&#10;## Validation&#10;&#10;| Success Metric | Review Trigger |&#10;|----------------|----------------|&#10;| [Metric 1] | [Condition for reconsideration] |&#10;&#10;## Supersession&#10;&#10;- **Supersedes**: [ADR-XXX or None]&#10;- **Superseded by**: [ADR-YYY or None]&#10;&#10;## Concern Impact&#10;&#10;If this decision affects the project&#x27;s active concerns or overrides a&#10;library practice, note the impact here:&#10;&#10;- **Concern selection**: [Does this ADR select, change, or constrain a concern?]&#10;- **Practice override**: [Does this ADR override a library concern practice? If so,&#10;  update `docs/helix/01-frame/concerns.md` Project Overrides with this ADR ref.]&#10;- **No concern impact**: [Delete this section if the ADR has no concern relevance.]&#10;&#10;## References&#10;&#10;- [PRD section link]&#10;- [Related ADRs]&#10;&#10;## Review Checklist&#10;&#10;Use this checklist when reviewing an ADR:&#10;&#10;- [ ] Context names a specific problem — not &quot;we need to decide about X&quot;&#10;- [ ] Decision statement is actionable — &quot;we will&quot; not &quot;we should consider&quot;&#10;- [ ] At least two alternatives were evaluated&#10;- [ ] Each alternative has concrete pros and cons, not vague assessments&#10;- [ ] Selected option&#x27;s rationale explains why it wins over the best alternative&#10;- [ ] Consequences include both positive and negative impacts&#10;- [ ] Negative consequences have documented mitigations&#10;- [ ] Risks are specific with probability and impact assessments&#10;- [ ] Validation section defines how we&#x27;ll know if the decision was right&#10;- [ ] Review triggers define conditions for reconsidering the decision&#10;- [ ] Concern impact section is complete (or explicitly marked as no impact)&#10;- [ ] ADR is consistent with governing feature spec and PRD requirements</code></pre></details></td></tr>
</tbody>
</table>
