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
considered, and what tradeoffs were accepted.

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
  authoring:
    home: repo
  depends_on:
    - example.architecture.depositmatch
---

# ADR-001: Use PostgreSQL as the System of Record

## Problem

DepositMatch must keep imports, source rows, match suggestions, reviewer decisions, exceptions, and audit evidence consistent with each other (PRD P0-1, P0-3, P0-4, P0-5). v1 starts from CSV imports with no external accounting APIs or bank feeds, so auditability and a fast pilot matter more than independent scaling of each data type.

## Decision

We will use PostgreSQL 16 as the single system of record for all DepositMatch v1 data, including audit-log records. Uploaded CSV originals stay in encrypted object storage; PostgreSQL holds their metadata and the normalized rows.

## Why We Chose This

### Over a document database
Flexible import payloads and fewer joins do not outweigh weaker relational integrity across invoices, deposits, matches, and corrections. Audit consistency is the point of the product.

### Over a separate event store plus read models
Event replay is attractive for audit history, but it costs more infrastructure and slows the pilot. Revisit if audit replay needs outgrow relational history.

## Consequences

**Good**: Imports, matches, exceptions, and audit records commit atomically and can be queried together.

**Trade-offs**: High-volume matching or analytics may later need read replicas or separate derived stores. Keep analytics derived and keep raw financial fields out of analytics events.

**Drift signals to watch**: An accepted match without source-row evidence. A partial import commit. A second store quietly becoming a source of truth.

## Concern Impact

- **Affects concerns**: Reinforces `reviewer-auditability`, `csv-import-integrity`, and `financial-data-security`. No practice override.
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
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Architecture Decision Record (ADR) Generation Prompt&#10;&#10;Write a compact ADR that captures one architecture-significant decision, the&#10;alternatives, and the consequences.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/02-design/adr/ADR-NNN-&lt;decision-name&gt;.md` — **one decision&#10;per file**. Naming is canonical and checkable: uppercase `ADR`, a **zero-padded&#10;3-digit** sequential number, then a kebab-case decision name (e.g.&#10;`ADR-001-modular-monolith.md`, `ADR-007-auth-tenant-isolation.md`). Do **not** use&#10;lowercase `adr-` or 4-digit numbers, and do **not** lump multiple decisions into&#10;one record. reconcile-alignment flags non-canonical names and lumped ADRs.&#10;&#10;## Purpose&#10;&#10;An ADR is the **single-decision record** for architecture-significant choices.&#10;Its unique job is to preserve why a decision was made, what alternatives were&#10;considered, and what tradeoffs were accepted.&#10;&#10;ADRs are not architecture documents. Architecture owns the overall structural&#10;model. ADRs are not solution designs or technical designs; those apply accepted&#10;decisions to narrower scopes. ADRs are not meeting notes; keep only the context&#10;that changes how future readers should evaluate the decision.&#10;&#10;## Reference Anchors&#10;&#10;Use these local resource summaries as grounding:&#10;&#10;- `docs/resources/adr-github-organization.md` grounds ADRs as&#10;  single-decision records with rationale, tradeoffs, and consequences.&#10;- `docs/resources/google-cloud-architecture-decision-records.md` grounds ADR&#10;  traceability to architecture evolution, code, and infrastructure context.&#10;&#10;## Focus&#10;- State the problem and decision plainly. If the operator has not stated the&#10;  intent behind the decision, confirm it before drafting (see `modes/design.md`).&#10;- State the chosen direction without claiming implementation completion.&#10;  Record implementation gaps and observed results in the relevant plan,&#10;  selected work item, or factual report; do not add progress banners here.&#10;- For each alternative, say why this choice beats it; keep it brief and honest.&#10;- Name drift signals only when they would reveal the decision being abandoned.&#10;- Omit dates, status, deciders, and risk or metric tables; git and the tracker hold them.&#10;- Use one ADR per decision. If the decision has independent parts, split it.&#10;- Keep one current record of the chosen direction and useful rationale. When&#10;  the decision changes, even to a reversal, rewrite it in place and move the&#10;  replaced option to the alternatives with the reason it lost. Do not add a&#10;  change log; source control keeps the history.&#10;- **Do not accept a decision whose design-defining facts are assumed.** A&#10;  decision&#x27;s design-defining facts (API shape, data model, pricing/cost&#10;  semantics, security/permissions, operational guarantees, or work decomposition)&#10;  must be **evidenced** — by an operator statement, a governing artifact, an&#10;  existing implementation, a docs/API proof, or a completed spike — not by model&#10;  familiarity, and not because a mechanism was picked or a provider named.&#10;  Choosing a provider and deferring its live integration does **not** evidence the&#10;  decision. If a design-defining fact is assumed, the ADR must cite **spike&#10;  evidence**, record a **blocked-spike rationale**, or carry an explicit&#10;  **provisional-risk** note (what is assumed, what could invalidate it, and that&#10;  the assumption is reversible/non-blocking). See the anti-reframe check in&#10;  `workflows/references/concern-resolution.md` (step 3a). An operator-marked&#10;  &quot;spike/unknown&quot; may not be accepted as a settled ADR without **spike evidence, a&#10;  blocked-spike rationale, or an explicit provisional-risk note**. A&#10;  **business/product** unknown a technical spike can&#x27;t answer (e.g. a pricing&#10;  model) → record **guidance-needed** or a blocked spike rather than forcing a&#10;  technical spike or accepting an assumed decision.&#10;&#10;## Boundary Test&#10;&#10;| If you are writing... | Put it in... |&#10;|---|---|&#10;| Overall system structure or deployment topology | Architecture |&#10;| One architecture-significant decision and rationale | ADR |&#10;| Feature-specific design applying accepted architecture | Solution Design |&#10;| Story-level component or code plan | Technical Design |&#10;| API schema, event payload, or file format | Contract |&#10;| Work steps or sequencing | Implementation Plan |&#10;&#10;## Completion Criteria&#10;- The decision is unambiguous.&#10;- Alternatives are compared clearly.&#10;- Consequences are explicit.&#10;- The decision states current working intent; no lifecycle stamp is required.&#10;- Drift signals are concrete when the decision has uncertainty.</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: ADR-XXX&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# ADR-NNN: [Title]&#10;&#10;## Problem&#10;&#10;[What constraint or tension prompted this decision? What&#x27;s broken or at risk?]&#10;&#10;## Decision&#10;&#10;We will [decision statement].&#10;&#10;## Why We Chose This&#10;&#10;### Over [Alternative 1]&#10;[Why this beats the alternative — what matters more: trade-off, risk, intent.]&#10;&#10;### Over [Alternative 2]&#10;[Why this beats the alternative — what matters more: trade-off, risk, intent.]&#10;&#10;## Consequences&#10;&#10;**Good**: [Outcomes that enable the PRD / reduce risk / unblock work]&#10;&#10;**Trade-offs**: [What we give up, defer, or constrain]&#10;&#10;**Drift signals to watch**: [Anti-patterns in review that signal this decision is being abandoned]&#10;&#10;## Concern Impact&#10;&#10;- **Override / deviation**: [Does this ADR override or deviate from a library concern constraint or practice? If so, add this ADR to Project Overrides in `docs/helix/01-frame/concerns.md`. Selecting a concern needs no ADR; `concerns.md` records it.]&#10;- **No concern impact**: [Delete if not relevant.]</code></pre></details></td></tr>
</tbody>
</table>
