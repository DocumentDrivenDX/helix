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
