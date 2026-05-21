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
<tr><th>Activity</th><td><a href="/reference/glossary/activities/"><strong>Design</strong></a> — Decide how to build it. Capture trade-offs, contracts, and architecture decisions.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/02-design/adrs/ADR-{id}-{name}.md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="/artifact-types/design/solution-design/">Solution Design</a><br><a href="/artifact-types/design/technical-design/">Technical Design</a></td></tr>
<tr><th>HELIX documents</th><td><a href="https://github.com/DocumentDrivenDX/helix/blob/main/docs/helix/02-design/adr/ADR-002-tracker-write-safety-model.md"><code>docs/helix/02-design/adr/ADR-002-tracker-write-safety-model.md</code></a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Architecture Decision Record (ADR) Generation Prompt

Write a compact ADR that captures one architecture-significant decision, the
alternatives, and the consequences.

## Purpose

An ADR is the **single-decision record** for architecture-significant choices.
Its unique job is to preserve why a decision was made, what alternatives were
considered, what tradeoffs were accepted, and when the decision should be
revisited.

ADRs are not architecture documents. Architecture owns the overall structural
model. ADRs are not solution designs or technical designs; those apply accepted
decisions to narrower scopes. ADRs are not meeting notes; keep only the context
that changes how future readers should evaluate the decision.

## Reference Anchors

Use these local resource summaries as grounding:

- `docs/resources/adr-github-organization.md` grounds ADRs as
  single-decision records with rationale, tradeoffs, and consequences.
- `docs/resources/google-cloud-architecture-decision-records.md` grounds ADR
  traceability to architecture evolution, code, and infrastructure context.

## Focus
- State the context and decision plainly.
- Keep alternatives and tradeoffs honest but brief.
- Note validation and references only if they affect the decision.
- Use one ADR per decision. If the decision has independent parts, split it.
- Treat accepted ADRs as history. New decisions supersede old records instead
  of rewriting them.

## Boundary Test

| If you are writing... | Put it in... |
|---|---|
| Overall system structure or deployment topology | Architecture |
| One architecture-significant decision and rationale | ADR |
| Feature-specific design applying accepted architecture | Solution Design |
| Story-level component or code plan | Technical Design |
| API schema, event payload, or file format | Contract |
| Work steps or sequencing | Implementation Plan |

## Completion Criteria
- The decision is unambiguous.
- Alternatives are compared clearly.
- Consequences are explicit.
- Status and supersession state are clear.
- Reconsideration triggers are concrete when the decision has uncertainty.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---
ddx:
  id: ADR-XXX
---

# ADR-[NUMBER]: [Title]

| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| [YYYY-MM-DD] | [Proposed/Accepted/Deprecated/Superseded] | [Names] | [FEAT-XXX] | [High/Med/Low] |

## Context

| Aspect | Description |
|--------|-------------|
| Problem | [Specific problem] |
| Current State | [Existing situation] |
| Requirements | [Key requirements driving this] |
| Decision Drivers | [Forces that make this architecture-significant] |

## Decision

We will [decision statement].

**Key Points**: [Point 1] | [Point 2] | [Point 3]

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| [Option 1] | [Advantages] | [Disadvantages] | [Rejected: reason] |
| [Option 2] | [Advantages] | [Disadvantages] | [Rejected: reason] |
| **[Selected]** | [Advantages] | [Disadvantages + mitigations] | **Selected: reason** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | [Good outcomes] |
| Negative | [Trade-offs, technical debt] |
| Neutral | [Side effects] |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk 1] | H/M/L | H/M/L | [Strategy] |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| [Metric 1] | [Condition for reconsideration] |

## Supersession

- **Supersedes**: [ADR-XXX or None]
- **Superseded by**: [ADR-YYY or None]

## Concern Impact

If this decision affects the project&#x27;s active concerns or overrides a
library practice, note the impact here:

- **Concern selection**: [Does this ADR select, change, or constrain a concern?]
- **Practice override**: [Does this ADR override a library concern practice? If so,
  update `docs/helix/01-frame/concerns.md` Project Overrides with this ADR ref.]
- **No concern impact**: [Delete this section if the ADR has no concern relevance.]

## References

- [PRD section link]
- [Related ADRs]

## Review Checklist

Use this checklist when reviewing an ADR:

- [ ] Context names a specific problem — not &quot;we need to decide about X&quot;
- [ ] Decision statement is actionable — &quot;we will&quot; not &quot;we should consider&quot;
- [ ] At least two alternatives were evaluated
- [ ] Each alternative has concrete pros and cons, not vague assessments
- [ ] Selected option&#x27;s rationale explains why it wins over the best alternative
- [ ] Consequences include both positive and negative impacts
- [ ] Negative consequences have documented mitigations
- [ ] Risks are specific with probability and impact assessments
- [ ] Validation section defines how we&#x27;ll know if the decision was right
- [ ] Review triggers define conditions for reconsidering the decision
- [ ] Concern impact section is complete (or explicitly marked as no impact)
- [ ] ADR is consistent with governing feature spec and PRD requirements</code></pre></details></td></tr>
</tbody>
</table>
