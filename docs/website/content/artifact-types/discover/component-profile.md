---
title: "Component Profile"
linkTitle: "Component Profile"
slug: component-profile
activity: "Discover"
artifactRole: "supporting"
weight: 90
generated: true
---

## Purpose

Answers: **What does this component actually do, according to the public
record, and how well does that record fit what this project needs?**

Both halves matter. Without the first, the fit is opinion. Without the
second, the profile is a brochure summary nobody can act on. The fit verdict
is the reason the profile exists; the cited record is what makes the verdict
trustworthy.

## Example

<details open>
<summary>Show a worked example of this artifact</summary>

``````markdown
---
ddx:
  id: component-profile-postgresql
  type: component-profile
  status: draft
  authoring:
    home: repo
---

# Component Profile: PostgreSQL

Desk research on PostgreSQL as a candidate primary relational store for
Ledgerline, measured against Ledgerline's vision, concerns and the open
data-store decision. **This is research, not a decision and not an
experiment.** The choice among candidates lives in ADR-007, which cites this
profile alongside [[component-profile-mysql]] and the managed-provider
profiles; what the record cannot settle is routed to a [[tech-spike]] below.

## Scope

- Component: PostgreSQL, community distribution, 18 release line
- Kind: Technology
- Would fill: primary relational store, `relational-data-modeling` slot
- Feeds: ADR-007 (primary data store), open
- Incumbent: SQLite in the prototype ([[current-state-inventory]], row
  "Prototype store", graded Evidenced)
- Researched: 8–12 September 2026
- Excluded: managed hosting, pricing and certifications of any provider —
  those belong to the provider profiles ([[component-profile-neon]],
  [[component-profile-aws-rds-postgresql]]); extensions other than pgvector

## What It Is

PostgreSQL is an open-source relational database maintained by the PostgreSQL
Global Development Group, a community project with no controlling vendor
[1][6]. It exists to store transactional data with strong integrity
guarantees: full SQL, ACID transactions, declarative constraints and
extensibility through user-defined types, functions and extensions [1].

Use cases it is built for, per its own material and independent coverage:

- General-purpose transactional workloads for applications of any size [1][7]
- Mixed relational and document data through the JSONB type [5]
- Read scale-out and selective data distribution through built-in replication
  [2]

## Capabilities

| Capability | What the record says | Source |
|------------|----------------------|--------|
| Row-level security | Policies restrict which rows a role can see or change, enforced in the database, since 9.5 | [4] |
| Logical replication | Publish/subscribe replication of selected tables to another instance, built in since 10 | [2] |
| Semi-structured data | JSONB type with indexing and containment operators | [5] |
| Vector search | Not part of core; provided by the pgvector extension, a separate project | [9] |
| Multi-tenant sharding | Not published — no native sharding; the record points to extensions and application-level partitioning | — |

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | Self-hosted on any supported platform; managed offerings are provider products, out of scope here | [1] |
| Integrations | Wire protocol with client libraries for every mainstream language; SQL standard conformance | [1] |
| Data handling | Encryption in transit via TLS and at rest via the host; residency is an operator matter | [1] |
| Certifications | Not published — certifications attach to an operator, not to the software | — |
| Maturity and cadence | One major release per year; each major supported for five years from release | [3] |
| Governance | Community project under the PostgreSQL Global Development Group; no single vendor controls the roadmap | [6] |
| Security process | Published security policy with coordinated disclosure and CVE listing | [8] |

## Pricing and Licensing

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Licence | PostgreSQL License, a permissive open-source licence permitting use, modification and redistribution without fee | Published | [1] |
| Software cost | None | Published | [1] |
| Running cost | Not published — depends on hosting; see the provider profiles | Not published | — |

## Positioning

| Adjacent candidate | Overlap | Divergence that matters here | Profile |
|--------------------|---------|------------------------------|---------|
| MySQL 8 | Open-source relational store with a large hosting ecosystem | Dual-licensed under GPL with a commercial edition [10]; no native row-level security, which Ledgerline's isolation requirement turns on | [[component-profile-mysql]] |
| Neon | Managed PostgreSQL | Adds branching and scale-to-zero; carries the residency and certification questions this profile excludes | [[component-profile-neon]] |
| Amazon RDS for PostgreSQL | Managed PostgreSQL | Carries the residency and certification questions; region list is the provider's | [[component-profile-aws-rds-postgresql]] |

## Fit Assessment

Measured against Ledgerline's [[product-vision]], [[principles]],
[[concerns]] and ADR-007, read on 8 September 2026.

Verdict vocabulary:

| Verdict | Means |
|---------|-------|
| **Fit** | Every named requirement is met on the public record. |
| **Conditional fit** | Fit if the named conditions hold; each condition is an open question or a spike. |
| **No fit** | A named requirement is contradicted on the public record. |
| **Undetermined** | The public record cannot settle a design-defining requirement; the spike that would is named. |

| Requirement or concern | From | What the record shows | Fit | Source |
|------------------------|------|-----------------------|-----|--------|
| Tenant isolation enforced below the application layer | [[product-vision]] "isolation an accountant would sign off on" | Row-level security policies enforced in the database | Met | [4] |
| Declarative constraints and transactional integrity | [[concerns]] `relational-data-modeling` | Full constraint support, ACID transactions | Met | [1] |
| No single-vendor lock-in on the data layer | [[principles]] P-3 | Permissive licence; community governance | Met | [1][6] |
| Read replica for reporting without blocking writes | ADR-007 open question 2 | Logical replication is built in; lag under Ledgerline's month-end write burst is not establishable from the record | Unknown | [2] |
| EU data residency | [[concerns]] `deployment-topology` | Software is residency-neutral; the question belongs to the provider | Unknown | — |

**Verdict**: Conditional fit — on the record PostgreSQL meets every
requirement the software can meet; replication lag under the month-end burst
needs a spike, and residency is answered by the provider profiles, not here.

## Confidence

| Grade | Means |
|-------|-------|
| **High** | Design-defining claims corroborated by the maker's material *and* at least one independent source. |
| **Medium** | Maker's material, with thin or dated independent coverage. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: High. Licence, governance, release policy and the three
design-defining capabilities are stated in maker documentation [1]–[6] and
corroborated by independent adoption data [7] and the pgvector project's own
material [9]. Weakest area: nothing in the record speaks to row-level
security performance at Ledgerline's tenant count under connection pooling —
that is a spike, not a claim.

## Sources

1. [About PostgreSQL and the PostgreSQL License](https://www.postgresql.org/about/licence/) — maker material, accessed 10 Sep 2026
2. [Logical Replication](https://www.postgresql.org/docs/current/logical-replication.html) — maker material, accessed 10 Sep 2026
3. [Versioning Policy](https://www.postgresql.org/support/versioning/) — maker material, accessed 10 Sep 2026
4. [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) — maker material, accessed 10 Sep 2026
5. [JSON Types](https://www.postgresql.org/docs/current/datatype-json.html) — maker material, accessed 10 Sep 2026
6. [PostgreSQL Developer Information](https://www.postgresql.org/developer/) — maker material, accessed 10 Sep 2026
7. [DB-Engines: PostgreSQL System Properties](https://db-engines.com/en/system/PostgreSQL) — independent, accessed 11 Sep 2026
8. [PostgreSQL Security Information](https://www.postgresql.org/support/security/) — maker material, accessed 11 Sep 2026
9. [pgvector](https://github.com/pgvector/pgvector) — community, accessed 11 Sep 2026
10. [MySQL Open Source License](https://www.mysql.com/about/legal/licensing/oss-license/) — maker material (MySQL), accessed 12 Sep 2026

## Open Questions

| # | Question | Design-defining because | Route |
|---|----------|-------------------------|-------|
| 1 | Does row-level security hold its throughput at ~2,000 tenants behind a connection pool that switches role per request? | Decides whether isolation lives in the database or the application | [[tech-spike]] SPIKE-004 |
| 2 | What replication lag does the reporting replica see during the month-end invoicing burst? | ADR-007 open question 2; decides whether reporting reads can be served off-primary | [[tech-spike]] SPIKE-005 |
| 3 | Which managed provider satisfies EU residency with a published SOC 2 report? | Residency is a `deployment-topology` constraint the software cannot answer | provider profiles |

## Review Checklist

- [x] Every factual claim cites a numbered source or is marked Not published / Third-party estimate
- [x] Every figure is labelled Published, Third-party estimate or Not published
- [x] Every fit row names the project artifact or decision it is measured against
- [x] Fit Assessment closes with exactly one verdict from the declared vocabulary
- [x] Confidence grade is justified by naming corroborating and missing sources
- [x] Every source carries an access date
- [x] No benchmark, prototype or integration result is claimed
- [x] No choice among candidates is made here
``````

</details>

## Reference

<table class="helix-reference-table">
<tbody>
<tr><th>Activity</th><td><a href="../../../reference/glossary/activities/"><strong>Discover</strong></a> — Validate that an opportunity is worth pursuing before committing to a development cycle.</td></tr>
<tr><th>Default location</th><td><code>docs/helix/00-discover/component-profile-[component-name].md</code></td></tr>
<tr><th>Requires</th><td><em>None</em></td></tr>
<tr><th>Enables</th><td><em>None</em></td></tr>
<tr><th>Informs</th><td><a href="../../../artifact-types/design/tech-spike/">Tech Spike</a><br><a href="../../../artifact-types/design/adr/">ADR</a><br><a href="../../../artifact-types/design/architecture/">Architecture</a><br><a href="../../../artifact-types/frame/concerns/">Concerns</a></td></tr>
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Component Profile Generation Prompt&#10;&#10;Consolidate what is publicly known about one candidate stack component, cite&#10;every claim, and measure it against this project&#x27;s own vision and concerns —&#10;before anyone spikes it or decides on it.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/component-profile-[component-name].md`&#10;&#10;One file per candidate. A decision with six candidates — say PostgreSQL,&#10;MySQL and four managed Postgres providers — is six profiles, not one long&#10;file. Separate files let candidates be researched in parallel, added late,&#10;and revised independently when one maker changes its pricing; a shared file&#10;grows past the point anyone reads it and takes one confidence grade for&#10;claims of very different strength.&#10;&#10;## Purpose&#10;&#10;Answers: **What does this component actually do, according to the public&#10;record, and how well does that record fit what this project needs?**&#10;&#10;Both halves matter. Without the first, the fit is opinion. Without the&#10;second, the profile is a brochure summary nobody can act on. The fit verdict&#10;is the reason the profile exists; the cited record is what makes the verdict&#10;trustworthy.&#10;&#10;## Role Boundary&#10;&#10;A Component Profile is not a [[tech-spike]]. A spike runs something — a&#10;prototype, a benchmark, an integration — to answer one narrow question with&#10;hands-on evidence. A profile reads. It comes first, so the spike is spent&#10;only on what reading cannot settle. When the record alone settles the&#10;question, the profile feeds the ADR directly and no spike is needed.&#10;&#10;It is not a [[competitive-analysis]]. That positions *our* product against&#10;rivals in a market. This asks whether *someone else&#x27;s* component belongs in&#10;our stack. Nothing here is being sold.&#10;&#10;It is not a [[current-state-inventory]]. The inventory records what the&#10;organization already runs, graded for evidence. A profile covers a candidate&#10;that may never be adopted. The inventory supplies the profile&#x27;s incumbent.&#10;&#10;It is not a [[resource-summary]]. That summarizes a source that grounds HELIX&#10;guidance. A profile synthesizes many sources about a thing.&#10;&#10;It is not an ADR. The profile assesses one candidate&#x27;s fit. The choice among&#10;candidates, with its consequences, lives in the ADR that cites the profiles.&#10;&#10;## Ownership and Reuse&#10;&#10;A profile belongs to the project whose decision it feeds, and lives in that&#10;project&#x27;s Discover directory. Its factual sections — What It Is,&#10;Capabilities, Technology and Operations, Pricing and Licensing, Positioning,&#10;Sources — are portable: another project may copy them. Scope and Fit&#10;Assessment are not: they name this project&#x27;s artifacts and open decisions, and&#10;a copy that keeps them asserts a fit nobody measured. A project that reuses a&#10;profile rewrites Scope and Fit Assessment, re-grades Confidence, and re-dates&#10;every source it keeps. The graph has no cross-project edge for this; the copy&#10;is the mechanism.&#10;&#10;## Method&#10;&#10;1. **Read the project before the component.** Open [[product-vision]],&#10;   [[principles]], [[concerns]], [[architecture]] and any ADR or spike this&#10;   profile will feed. Write down, as questions, what they require of the role&#10;   this component would fill. These questions become the Fit Assessment rows.&#10;   A profile written before this step assesses fit against nothing.&#10;2. **Fix the scope.** Name the exact component — edition, version line,&#10;   hosting form — and what the profile excludes. &quot;Postgres&quot; is not a scope;&#10;   &quot;PostgreSQL 18, community distribution, self-hosted or managed&quot; is.&#10;3. **Gather the record.** Maker material first, then independent coverage&#10;   (analysts, comparisons, conference talks, issue trackers, post-mortems),&#10;   then community sources. Record each source with its URL and the date you&#10;   read it, and classify it as maker, independent or community.&#10;4. **Write one claim at a time, with its number.** Every capability, every&#10;   operational fact, every figure cites a source. A claim you cannot source&#10;   is written as **Not published**, and that is a finding, not a gap in your&#10;   work.&#10;5. **Label every figure.** Published, with source and date. Third-party&#10;   estimate, naming the estimator. Or Not published. Never derive a price.&#10;6. **Position against the adjacent candidates.** Name what a reader will ask&#10;   &quot;why not X?&quot; about, and state the divergence *this project* cares about.&#10;   Link sibling profiles where they exist.&#10;7. **Assess fit, row by row, against the questions from step 1.** Each row&#10;   names the artifact it comes from. Then write exactly one verdict from the&#10;   declared vocabulary and one sentence of conditions or deciding gap.&#10;8. **Grade confidence honestly.** One grade from the rubric, then say which&#10;   claims are corroborated, which rest on the maker alone, and which have&#10;   none. Name the weakest area.&#10;9. **Route what the record cannot answer.** Every unknown that bears on a&#10;   design-defining decision becomes an Open Question with a route: a spike, a&#10;   question to the maker, or operator guidance.&#10;&#10;## Researching Honestly&#10;&#10;The pressure on this artifact is toward fluency: the model already knows the&#10;component, the maker&#x27;s site is persuasive, and a confident profile reads as&#10;finished. Resist all three.&#10;&#10;- **Familiarity is not a source.** A fact you know about the component still&#10;  needs a citation. If you cannot find one, it is Not published.&#10;- **Maker material is one voice.** A profile with no independent source is&#10;  Medium at best, however thorough the documentation.&#10;- **&quot;Not published&quot; beats a plausible guess.** A guessed price, a guessed&#10;  region list, a guessed certification becomes a fact in the ADR.&#10;- **The verdict is not the decision.** Conditional fit with named conditions&#10;  is a complete, useful result. Do not round it up to Fit to look decisive,&#10;  and do not recommend a candidate — that is the ADR&#x27;s job.&#10;- **A fit row without an artifact is an opinion.** If nothing in the&#10;  project&#x27;s own documents requires it, it is not a requirement.&#10;- **Hands-on claims do not belong here.** If you find yourself writing &quot;in&#10;  our test&quot;, stop and open a spike.&#10;&#10;## Inputs&#10;&#10;- The project&#x27;s [[product-vision]], [[principles]], [[concerns]],&#10;  [[architecture]] and the ADR or spike this profile feeds — read first&#10;- [[current-state-inventory]], for the incumbent&#10;- Maker documentation, pricing pages, licence texts, security and trust pages,&#10;  release notes and roadmaps&#10;- Independent coverage: analyst notes, comparisons, conference talks,&#10;  incident reports, issue trackers&#10;- Sibling profiles for adjacent candidates&#10;&#10;## Quality Checks&#10;&#10;- Every factual claim cites a numbered source or is marked Not published or&#10;  Third-party estimate&#10;- Every figure is labelled Published, Third-party estimate or Not published&#10;- Every fit row names the project artifact or decision it is measured against&#10;- Fit Assessment closes with exactly one verdict from the declared vocabulary&#10;- The confidence grade is justified by naming corroborating and missing&#10;  sources&#10;- Every source carries an access date&#10;- No benchmark, prototype or integration result is claimed&#10;- No choice among candidates is made</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: component-profile&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Component Profile: [Component Name]&#10;&#10;Desk research on one candidate stack component — a technology, a product, or a&#10;managed provider — consolidated from the public record and measured against&#10;this project&#x27;s vision, concerns and open decisions. **This is research, not a&#10;decision and not an experiment.** The choice among candidates lives in an ADR&#10;that cites the profiles; anything the public record cannot settle is a&#10;[[tech-spike]].&#10;&#10;One instance per candidate. When one decision has several candidates, write&#10;one profile each and let the ADR compare them. The factual sections travel&#10;between projects; Scope and Fit Assessment do not — a project reusing another&#10;project&#x27;s profile rewrites both and re-dates every source.&#10;&#10;## Scope&#10;&#10;- Component: [Name, edition or version line researched]&#10;- Kind: [Technology | Product | Managed provider]&#10;- Would fill: [The capability, concern slot or architectural role it is a candidate for]&#10;- Feeds: [The ADR, spike or slot decision this profile informs, by id or path]&#10;- Incumbent: [What fills the role today, citing [[current-state-inventory]] where one exists, or *None*]&#10;- Researched: [Date range]&#10;- Excluded: [What this profile deliberately does not cover, and why]&#10;&#10;## What It Is&#10;&#10;[Two or three sentences a reader can repeat: what the component is, who makes&#10;or maintains it, and the problem it exists to solve. [n]]&#10;&#10;Use cases it is built for, per its own material and independent coverage:&#10;&#10;- [Use case] [n]&#10;&#10;## Capabilities&#10;&#10;Features that bear on the role it would fill. Omit the marketing list; keep&#10;what the Fit Assessment will need.&#10;&#10;| Capability | What the record says | Source |&#10;|------------|----------------------|--------|&#10;| [Capability] | [Specific, checkable statement] | [n] |&#10;| [Capability] | Not published | — |&#10;&#10;## Technology and Operations&#10;&#10;| Aspect | What the record says | Source |&#10;|--------|----------------------|--------|&#10;| Hosting model | [Self-hosted, managed, or both; regions] | [n] |&#10;| Integrations | [Protocols, ecosystems and clients that matter for the role] | [n] |&#10;| Data handling | [Residency, encryption, retention, whether customer data trains models] | [n] |&#10;| Certifications | [SOC 2, ISO 27001, HIPAA and the like — as published, with date] | [n] |&#10;| Maturity and cadence | [First release, release cadence, support window] | [n] |&#10;| Governance | [Who controls the roadmap: single vendor, foundation, community] | [n] |&#10;&#10;## Pricing and Licensing&#10;&#10;Label every figure. **Published** means the maker states it, with source and&#10;date. **Third-party estimate** names who estimated. Otherwise write **Not&#10;published** — never infer a price.&#10;&#10;| Item | Figure | Label | Source |&#10;|------|--------|-------|--------|&#10;| Licence | [Licence name and what it permits] | Published | [n] |&#10;| [Tier or unit] | [Figure] | Published / Third-party estimate / Not published | [n] |&#10;&#10;## Positioning&#10;&#10;The adjacent candidates a reader will ask about, and where this component&#10;overlaps with or diverges from each. Link sibling profiles where they exist.&#10;&#10;| Adjacent candidate | Overlap | Divergence that matters here | Profile |&#10;|--------------------|---------|------------------------------|---------|&#10;| [Name] | [Shared ground] | [The difference this project cares about] | [[component-profile-name]] or *none yet* |&#10;&#10;## Fit Assessment&#10;&#10;Measured against **this project&#x27;s** artifacts, read before this section was&#10;written. Name each one. A row with no named artifact is an opinion, not a fit.&#10;&#10;Verdict vocabulary:&#10;&#10;| Verdict | Means |&#10;|---------|-------|&#10;| **Fit** | Every named requirement is met on the public record. |&#10;| **Conditional fit** | Fit if the named conditions hold; each condition is an open question or a spike. |&#10;| **No fit** | A named requirement is contradicted on the public record. |&#10;| **Undetermined** | The public record cannot settle a design-defining requirement; the spike that would is named. |&#10;&#10;| Requirement or concern | From | What the record shows | Fit | Source |&#10;|------------------------|------|-----------------------|-----|--------|&#10;| [Requirement] | [[product-vision]] / [[concerns]] / [[principles]] / ADR-nnn | [Specific finding] | Met / Unmet / Unknown | [n] |&#10;&#10;**Verdict**: [Fit | Conditional fit | No fit | Undetermined] — [one sentence&#10;naming the conditions or the deciding gap].&#10;&#10;## Confidence&#10;&#10;One grade for the profile, from this rubric:&#10;&#10;| Grade | Means |&#10;|-------|-------|&#10;| **High** | Design-defining claims corroborated by the maker&#x27;s material *and* at least one independent source. |&#10;| **Medium** | Maker&#x27;s material, with thin or dated independent coverage. |&#10;| **Low** | Thin public footprint; claims rest on one source or on none. |&#10;&#10;**Grade**: [High | Medium | Low]. [Which claims are corroborated, which rest&#10;on the maker alone, and which have no source. Name the weakest area.]&#10;&#10;## Sources&#10;&#10;Numbered; cited by number above. Each carries the date accessed.&#10;&#10;1. [Title](URL) — [maker material | independent | community], accessed [date]&#10;&#10;## Open Questions&#10;&#10;What the public record cannot answer. Each is a spike candidate, a question for&#10;the maker, or a call for operator guidance — never an assumption carried into&#10;the ADR.&#10;&#10;| # | Question | Design-defining because | Route |&#10;|---|----------|-------------------------|-------|&#10;| 1 | [Question] | [Which decision turns on it] | [[tech-spike]] / ask maker / operator guidance |&#10;&#10;## Review Checklist&#10;&#10;- [ ] Every factual claim cites a numbered source or is marked Not published / Third-party estimate&#10;- [ ] Every figure is labelled Published, Third-party estimate or Not published&#10;- [ ] Every fit row names the project artifact or decision it is measured against&#10;- [ ] Fit Assessment closes with exactly one verdict from the declared vocabulary&#10;- [ ] Confidence grade is justified by naming corroborating and missing sources&#10;- [ ] Every source carries an access date&#10;- [ ] No benchmark, prototype or integration result is claimed&#10;- [ ] No choice among candidates is made here</code></pre></details></td></tr>
</tbody>
</table>
