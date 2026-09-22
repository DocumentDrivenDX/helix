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

Answers: **What does this project need from the role, what does this
component do on each of those needs according to the public record, and how
do the alternatives compare on the same needs?**

The Need gives the reader a way in and tells the research what to look for.
The cited record makes the fit checkable. The landscape lets the ADR compare
candidates from evidence. The Summary, Need, and Required Capabilities
sections are reused word for word by any brief or deck built from the
profile, so they are written for a reader outside the project.

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

Desk research on PostgreSQL as the system of record for DepositMatch,
measured against the capabilities DepositMatch needs from that role. The
choice lives in ADR-001, which this profile informs; what the record cannot
settle is routed below.

## Scope

- Component: PostgreSQL, community distribution, 16 release line (the line
  [[architecture]] names)
- Kind: Technology
- Would fill: system of record for clients, import sessions, source rows,
  invoices, deposits, match suggestions, reviewer decisions, exceptions, and
  the audit log (`area:data`)
- Feeds: ADR-001 (PostgreSQL as the system of record), accepted 12 May 2026;
  this profile is the desk research the ADR's alternatives table rests on,
  refreshed 22 September 2026 for the read-replica follow-up its risk table
  names
- Incumbent: none in production; pilot firms reconcile in spreadsheets and
  accounting exports today ([[product-vision]] Target Market). DepositMatch
  has no [[current-state-inventory]].
- Researched: 22 September 2026
- Excluded: managed-hosting pricing, regions, and certifications beyond what
  [[architecture]] already fixes (Amazon RDS, us-east-1), which belong to
  [[component-profile-aws-rds-postgresql]]; extensions

## Summary

DepositMatch needs a system of record for CSV imports, source rows,
invoices, deposits, match suggestions, reviewer decisions, exceptions, and
the audit log, so that every accepted match can be explained at month-end,
every unresolved deposit stays owned, and the pilot ships with one store to
operate. The store must commit an import and its derived rows atomically
under declarative constraints, record who decided what and keep the
correction history, restrict financial fields and audit rows by role,
encrypt data in transit and at rest, recover to a point in time within the
project's fifteen-minute recovery target, run the matching worker's job
queue, and take a read replica later without a schema change. On the public
record PostgreSQL 16 meets all seven, six from its own documentation and
encryption at rest from the Amazon RDS hosting the architecture names, so the
verdict is Fit; the restore-time target and replica lag under an import burst
are the two questions only a drill or a spike can answer.

## How to Read This Profile

| Word | Where | Means |
|------|-------|-------|
| **Met** | Capability Alignment status | The public record documents the capability as its Required Capabilities row defines it. |
| **Unmet** | Capability Alignment status | The public record contradicts it, or the maker states it is absent. |
| **Unknown** | Capability Alignment status | The record does not settle it; the Open Questions table routes it. |
| **Fit** | Verdict | Every required capability is Met. |
| **Conditional fit** | Verdict | Every required capability is Met or Unknown, and no Unknown is design-defining; each Unknown is an Open Question with a route. |
| **Undetermined** | Verdict | At least one design-defining capability is Unknown; the spike that would settle it is named. |
| **No fit** | Verdict | At least one required capability is Unmet. |
| **Published** | Figures | The maker states it, with source and date. |
| **Third-party estimate** | Figures | Someone other than the maker estimated it; the estimator is named. |
| **Not published** | Figures and claims | Searched and absent; the search is recorded. |
| **Not researched** | Competitive Landscape cells | Nobody has looked; the Profile column names the sibling profile that would fill it. |
| **High / Medium / Low** | Confidence | Defined in the Confidence section. |
| **maker / vendor / independent / community** | Sources | Defined in the Sources section. |

## Need

DepositMatch needs a system of record for its reconciliation workspace: it
stores each client firm's CSV imports and their source rows, the invoices
and deposits those rows become, the match suggestions the worker generates,
the decisions reviewers take, the exceptions they own, and the audit log
behind all of it. Those uses serve the goals the vision and the decision
record set: a review log that lets a firm explain every accepted match at
month-end, exceptions that stay owned instead of drifting to a spreadsheet,
and a pilot that ships fast with one store to operate ([[product-vision]]
Key Value Propositions; [[principles]] 2 and 5; ADR-001 Decision Drivers).
Today pilot firms reconcile in QuickBooks or Xero exports, bank reports,
spreadsheets, and email, and spreadsheet trails are too fragile for monthly
close ([[product-vision]] Target Market).

## Required Capabilities

| # | Capability | Serves | Comes from | Settled by |
|---|------------|--------|------------|------------|
| C1 | An import session, its source rows, and the rows derived from them commit together or not at all, with constraints that keep invoices, deposits, and matches consistent | a review log a firm can explain | ADR-001 Validation ("import confirmation remains atomic"); [[concerns]] `csv-import-integrity`; [[architecture]] Quality Attributes | Transaction semantics and constraint types in the maker's documentation |
| C2 | Every reviewer decision and correction is recorded with who and when, and history is kept | auditability as usability | [[concerns]] `reviewer-auditability`; [[principles]] 5 | A server-side mechanism that records the acting user and time on data changes |
| C3 | Access is scoped by role down to the column, so analytics roles never read financial fields and audit rows are readable only by audit roles | protecting customer financial records | [[concerns]] `financial-data-security` | Column-level and row-level privilege features in the maker's documentation |
| C4 | Data is encrypted in transit by the software and at rest by the hosting the architecture names | protecting customer financial records | [[concerns]] `financial-data-security`; [[architecture]] Security | TLS in the maker's documentation; at-rest encryption in the hosting provider's documentation |
| C5 | Point-in-time recovery with a recovery point no older than fifteen minutes | the disaster-recovery target | [[architecture]] Disaster Recovery (15-minute RPO) | Continuous archiving in the maker's documentation; the hosting provider's stated log-upload interval |
| C6 | A durable job queue inside the store that several matching workers can consume without contention | one store to operate | [[architecture]] Decisions ("PostgreSQL-backed worker jobs"); ADR-001 Validation (backlog trigger) | A documented row-locking clause suited to queue tables |
| C7 | A read-only replica for firm-level reports can be added later without changing the store or the schema | reports that do not slow imports | ADR-001 Consequences and Risks ("add read replica if reporting load grows") | A documented standby or replica mechanism, from the software and the hosting provider |

Nice to have: semi-structured storage for raw CSV rows without a second
store; partitioning of import sessions once a retention policy exists
(ADR-001 Risks).

## What It Is

PostgreSQL is an open-source object-relational database system that uses
and extends the SQL language [11]. It is maintained by the PostgreSQL Global
Development Group, a community of volunteer committers and a core team that
coordinates work through CommitFests; the project states that it does not
hire programmers and draws contributors across the Internet [8]. Its origins
date to the POSTGRES project at the University of California, Berkeley, in
1986, and it has been ACID-compliant since 2001 [11]. In the 2025 Stack
Overflow Developer Survey of developers worldwide it was the most-used
database, named by 55.6% of all respondents and 58.2% of professional
developers [20].

- Category and purpose: open-source object-relational database for
  transactional workloads; SQL, ACID transactions, declarative constraints,
  and extensibility through user-defined types and functions [11]
- Maker or governing body: the PostgreSQL Global Development Group, with no
  controlling vendor; committers, a core team, and CommitFests [8]
- Adoption: first among databases in the 2025 Stack Overflow Developer
  Survey, 55.6% of respondents [20]
- Release cadence and support window: one major version a year, each
  supported for five years after its initial release; as of 22 September
  2026 versions 14 through 18 are supported, and version 16 is supported
  until 9 November 2028 [6]
- Licence: the PostgreSQL Licence, a liberal open-source licence similar to
  BSD or MIT, permitting use, copy, modification, and distribution without
  fee; the project states it has no plans to change it [1]
- Built-for use cases: general transactional applications [11]; mixed
  relational and document data through the JSONB type [9]; sending
  incremental changes to subscribers and consolidating databases for
  analysis through built-in logical replication [4]

## Capability Alignment

### C1. Atomic import commit under constraints

A PostgreSQL transaction is atomic: from the point of view of other
transactions it either happens completely or not at all, its updates are
logged to permanent storage before it is reported complete, and its
intermediate states are invisible to other transactions until it commits
[12]. Declarative constraints cover check, not-null, unique, primary key,
foreign key, and exclusion constraints; a foreign key constraint maintains
referential integrity between two related tables [13]. An import session,
its source rows, and the invoices and deposits derived from them can
therefore commit in one transaction with the row identities the matching
evidence needs enforced by the schema.

**Settled by**: transaction semantics found in [12]; constraint types found in [13]
**Status**: Met

### C2. Reviewer attribution and kept history

Row-level trigger functions run before or after an insert, update, or
delete and see both the old and new row; the documentation's own example
writes an audit row carrying the operation, `now()`, `current_user`, and the
changed row into a separate table [14]. That gives the store a server-side
way to record who changed a decision and when, and to keep the prior state,
independent of the application code path. The design of the audit tables is
the application's; the record settles that the mechanism exists.

**Settled by**: a server-side mechanism recording user and time on data changes, found in [14]
**Status**: Met

### C3. Role-scoped access to the column

Table privileges (`SELECT`, `INSERT`, `UPDATE`, `DELETE`, `TRUNCATE`,
`REFERENCES`, `TRIGGER`) can be granted on specific columns, so an analytics
role can read a deposits table without its amount column, and only the
object's owner or a superuser can grant or revoke [15]. Row security
policies, added in PostgreSQL 9.5 [3], restrict per role which rows a query
returns or a command touches; a table with row security enabled and no
policy denies all rows by default, superusers and roles with `BYPASSRLS`
always bypass the policies, and table owners bypass them unless the table is
set to `FORCE ROW LEVEL SECURITY` [2]. A 2026 QueryPlane post names an
application connecting as the owning role, with policies silently ignored,
as the most common production pitfall, and reports that a tenant set with
plain `SET` instead of `SET LOCAL` persists across a pooled connection into
the next request [21]. Both mechanisms are in core; the API service in
[[architecture]] connects through a pool, so the `SET LOCAL` caveat applies
if row security is adopted.

**Settled by**: column-level privileges found in [15]; row-level privileges found in [2][3], with pooled-connection behaviour in [21]
**Status**: Met

### C4. Encryption in transit and at rest

PostgreSQL has native support for SSL connections to encrypt client and
server communication, enabled with the `ssl` parameter and a server
certificate and key, and it can require client certificates through
`clientcert=verify-ca` or `verify-full` [16]. Encryption at rest is not a
feature of the software; the hosting [[architecture]] names, Amazon RDS,
states that data at rest in the underlying storage, automated backups, read
replicas, and snapshots are encrypted with AES-256 through keys managed in
AWS Key Management Service, and that connections use SSL/TLS [29].

**Settled by**: TLS found in [16]; at-rest encryption found in the hosting provider's documentation [29]
**Status**: Met

### C5. Point-in-time recovery within fifteen minutes

Continuous archiving combines a file-system-level backup with archived
write-ahead log files; replay can stop at any point, so the database can be
restored to its state at any time since the base backup, and the technique
restores an entire cluster, never a subset [17]. On Amazon RDS, transaction
logs are uploaded every five minutes and an instance can be restored to any
point within the backup retention period, which bounds the recovery point
at five minutes against the fifteen-minute target [32]. How long a restore
takes is a measured result the record does not carry; the architecture's
quarterly restore drill owns it.

**Settled by**: continuous archiving found in [17]; the provider's five-minute log interval found in [32]
**Status**: Met

### C6. A job queue inside the store

`SELECT ... FOR UPDATE SKIP LOCKED` skips any selected row that cannot be
locked immediately; the documentation says the resulting view is
inconsistent and unsuitable for general work, and names its use as avoiding
lock contention with multiple consumers accessing a queue-like table [18].
That is the matching worker's pattern in [[architecture]]: jobs persist in
PostgreSQL and a restarted task picks up where the failed one stopped. The
backlog trigger in ADR-001 (100 jobs for five minutes) is the point at which
this capability is re-examined.

**Settled by**: a row-locking clause for queue tables found in [18]
**Status**: Met

### C7. A read replica later, without a schema change

Hot standby lets clients connect to a standby server and run read-only
queries while it replays the primary's write-ahead log; the documentation
states that data on the standby takes some time to arrive, so there is a
measurable delay and the standby is eventually consistent with the primary
[19]. Amazon RDS for PostgreSQL adds read-only replicas on that native
replication with a reported replica-lag metric [28]; the Multi-AZ standby
the architecture already runs is a synchronous failover copy that cannot
serve reads, so a reporting replica is a separate instance [33]. A Percona
post updated in April 2024 names long transactions, network congestion,
slow disk, and too few WAL senders under heavy transaction load as the
causes of lag [22]. Adding a replica is a deployment change; the schema stays as it is.

**Settled by**: a standby mechanism found in [19]; the provider's replica feature found in [28][33]
**Status**: Met

Other notable capabilities the record documents and no criterion requires:

| Capability | What the record says | Source |
|------------|----------------------|--------|
| Semi-structured data | `jsonb` stores JSON in a decomposed binary form that is faster to process than `json`, supports indexing, and adds containment and existence operators | [9] |
| Declarative partitioning | Range, list, and hash partitioning of one table within one server; foreign tables may serve as partitions at the user's own risk; no cross-server sharding is described | [10] |
| Logical replication | Publish-and-subscribe replication of selected tables in commit order, built in since version 10 | [4][5] |
| Security process | Coordinated disclosure through security@postgresql.org; the project assigns its own CVEs; fixes ship in minor releases | [7] |

**Verdict**: Fit. Every required capability is Met on the public record,
six from the software's own documentation and C4's at-rest half from the
hosting provider the architecture names. The two measured results the record
cannot carry, restore time and replica lag under an import burst, are Open
Questions with routes and change no status.

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | Runs on all major operating systems; the architecture hosts it on Amazon RDS in us-east-1, Multi-AZ | [11]; [[architecture]] Deployment |
| Integrations | SQL:2023 Core conformance to at least 170 of 177 mandatory features as of version 18; the API service and worker connect over TLS SQL | [11]; [[architecture]] Containers |
| Data handling | TLS in transit from the software; at-rest encryption, backups, and retention are the operator's | [16][29] |
| Certifications | Not published for the software (searched [7][11], 22 Sep 2026); Amazon RDS is in scope for SOC 1, 2, and 3 | [30] |
| Maturity and cadence | Origins 1986; one major release a year; each supported for five years; version 16 supported until 9 November 2028 | [6][11] |
| Governance | Community project under the PostgreSQL Global Development Group; committers and a core team; no company named as controlling the roadmap | [8] |
| Security process | Coordinated disclosure; the project is its own CVE Numbering Authority; fixes in minor releases | [7] |

## Pricing and Licensing

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Licence | PostgreSQL Licence: use, copy, modify, and distribute for any purpose, without fee | Published | [1] |
| Software cost | None | Published | [1] |
| Running cost | Not published by the maker (searched [1][11], 22 Sep 2026); the business case carries $12,000 of year-one infrastructure for the whole system | Not published | [[business-case]] Investment Required |

## Competitive Landscape

| Candidate | C1 Atomic commit and constraints | C2 Attribution and history | C3 Role scope to the column | C4 Encryption | C5 PITR within 15 minutes | C6 In-store job queue | C7 Read replica later | Profile |
|-----------|----------------------------------|----------------------------|-----------------------------|---------------|---------------------------|-----------------------|-----------------------|---------|
| PostgreSQL 16 | Met [12][13] | Met [14] | Met [2][15] | Met, at rest via hosting [16][29] | Met via hosting [17][32] | Met [18] | Met [19][28] | this profile |
| MySQL 8.4 Community | InnoDB adheres to the ACID model [25]; constraint semantics Not researched | Not researched | No native row-level security; views and triggers are the documented workaround [23]; column privileges Not researched | Not researched | Not researched | Not researched | Not researched | [[component-profile-mysql]] |
| Document database (MongoDB) | Multi-document ACID transactions since 4.0 on replica sets and 4.2 on sharded clusters; the maker cautions that a distributed transaction costs more than single-document writes and is no substitute for schema design [26]; declarative constraints Not researched | Not researched | Not researched | Not researched | Not researched | Not researched | Not researched | *none yet* |
| Amazon RDS for PostgreSQL 16 | Inherits: runs PostgreSQL 13 through 17 as of 22 Sep 2026 [27] | Inherits [27] | Inherits [27] | AES-256 at rest, TLS in transit [29] | Logs uploaded every five minutes; restore to any point in the retention period [32] | Inherits [27] | Read-only replicas with a lag metric [28]; the Multi-AZ standby cannot serve reads [33] | [[component-profile-aws-rds-postgresql]] |

- MySQL 8.4 shares the open-source relational category and a large hosting
  ecosystem; the divergence DepositMatch would care about is C3, where MySQL
  has no native row-level security and the documented alternative is views
  with `WHERE` clauses plus triggers [23]. Its Community Edition is under the
  GPL alongside Oracle's Standard, Enterprise, and Cluster editions [24].
- A document database is the alternative ADR-001 rejected for weaker
  relational integrity across invoices, deposits, matches, and corrections;
  MongoDB's own material supports multi-document transactions and cautions
  against relying on them in place of schema design [26]. No sibling profile
  exists.
- ADR-001's third alternative, a separate event store plus read models, is
  an architecture pattern and has no single component to profile.
- Amazon RDS for PostgreSQL is the hosting the architecture names; it adds
  the at-rest encryption, the five-minute log interval, the failover standby,
  and the compliance scope the software cannot supply [29][30][32][33], with
  endpoints in eight EU regions should residency ever matter [31].

## Confidence

| Grade | Means |
|-------|-------|
| **High** | Every design-defining claim is corroborated by the maker's material *and* at least one independent source, and no design-defining capability is Unknown. |
| **Medium** | Design-defining claims rest on the maker alone, or a design-defining capability is Unknown, or the independent coverage is older than two major versions. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: Medium. Adoption [20] and row-security practice [21] are
independently corroborated, and licence, governance, and release policy are
stated by the maker [1][6][8]. The design-defining claims behind C1, C2, C5,
and C6 (transactions, constraints, triggers, continuous archiving, `SKIP
LOCKED`) rest on the maker's documentation alone [12][13][14][17][18], and
the only independent replication coverage [22] is a vendor post that
predates version 17. The MySQL and MongoDB cells rest on one vendor post
[23] and the makers' own pages [24][25][26]. Weakest area: nothing in the
record measures a restore's duration or a replica's lag under DepositMatch's
import bursts.

## Open Questions

| # | Question | Design-defining because | Route |
|---|----------|-------------------------|-------|
| 1 | Does a point-in-time restore of the production instance complete within the four-hour recovery-time target? | [[architecture]] Disaster Recovery names a 4-hour RTO; the record carries the recovery point and no restore duration | [[architecture]] verification: quarterly restore drill before paid launch |
| 2 | What replica lag would a reporting replica see during an import burst, should reporting load grow? | ADR-001 Risks route reporting load to a read replica; lag decides whether firm-level reports can leave the primary | ADR-001 review trigger, then a [[tech-spike]] |
| 3 | If per-firm isolation moves from application filters into row security, does throughput hold behind the API's connection pool? | Decides whether isolation lives in the database or the application; today [[architecture]] scopes access by role at the application boundary | [[tech-spike]] if row security is adopted |

## Sources

Classes: **maker** (the component's maker or governing body), **vendor** (a
company selling hosting or support for the component or a rival),
**independent** (no commercial interest; named author or organisation and a
date), **community** (a project or forum around the component).

1. [About PostgreSQL and the PostgreSQL Licence](https://www.postgresql.org/about/licence/), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
2. [Row Security Policies, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/ddl-rowsecurity.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
3. [PostgreSQL 9.5.0 release notes](https://www.postgresql.org/docs/release/9.5.0/), maker, PostgreSQL Global Development Group, published 7 Jan 2016, accessed 22 Sep 2026
4. [Logical Replication, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/logical-replication.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
5. [PostgreSQL 10.0 release notes](https://www.postgresql.org/docs/release/10.0/), maker, PostgreSQL Global Development Group, published 5 Oct 2017, accessed 22 Sep 2026
6. [Versioning Policy](https://www.postgresql.org/support/versioning/), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
7. [PostgreSQL Security Information](https://www.postgresql.org/support/security/), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
8. [PostgreSQL Developer Information](https://www.postgresql.org/developer/), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
9. [JSON Types, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/datatype-json.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
10. [Table Partitioning, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/ddl-partitioning.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
11. [About PostgreSQL](https://www.postgresql.org/about/), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
12. [Transactions, PostgreSQL 16 tutorial](https://www.postgresql.org/docs/16/tutorial-transactions.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
13. [Constraints, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/ddl-constraints.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
14. [Trigger Functions, PostgreSQL 16 PL/pgSQL documentation](https://www.postgresql.org/docs/16/plpgsql-trigger.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
15. [Privileges, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/ddl-priv.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
16. [Secure TCP/IP Connections with SSL, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/ssl-tcp.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
17. [Continuous Archiving and Point-in-Time Recovery, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/continuous-archiving.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
18. [SELECT, PostgreSQL 16 documentation, locking clause](https://www.postgresql.org/docs/16/sql-select.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
19. [Hot Standby, PostgreSQL 16 documentation](https://www.postgresql.org/docs/16/hot-standby.html), maker, PostgreSQL Global Development Group, accessed 22 Sep 2026
20. [Stack Overflow Developer Survey 2025: Technology](https://survey.stackoverflow.co/2025/technology), independent, Stack Overflow, published 2025, accessed 22 Sep 2026
21. [Postgres Row-Level Security: Multi-Tenant Patterns That Hold Up](https://queryplane.com/blog/postgres-row-level-security-in-practice/), vendor, QueryPlane (a Postgres tooling company; author unnamed), published 30 Apr 2026, updated 23 Aug 2026, accessed 22 Sep 2026
22. [Replication Lag in PostgreSQL](https://www.percona.com/blog/replication-lag-in-postgresql/), vendor, Percona, Naveed Shaikh, published Apr 2023, updated Apr 2024, accessed 22 Sep 2026
23. [Implement row-level security in Amazon Aurora MySQL and Amazon RDS for MySQL](https://aws.amazon.com/blogs/database/implement-row-level-security-in-amazon-aurora-mysql-and-amazon-rds-for-mysql), vendor, Amazon Web Services, published 16 Jun 2025, accessed 22 Sep 2026
24. [MySQL Community Edition](https://www.mysql.com/products/community/), maker (MySQL), Oracle, accessed 22 Sep 2026
25. [InnoDB and the ACID Model, MySQL 8.4 Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/mysql-acid.html), maker (MySQL), Oracle, accessed 22 Sep 2026
26. [Transactions, MongoDB Manual](https://www.mongodb.com/docs/manual/core/transactions/), maker (MongoDB), MongoDB Inc., accessed 22 Sep 2026
27. [Amazon RDS for PostgreSQL FAQs](https://aws.amazon.com/rds/postgresql/faqs/), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
28. [Working with read replicas for Amazon RDS for PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.Replication.ReadReplicas.html), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
29. [Amazon RDS Security](https://aws.amazon.com/rds/features/security/), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
30. [AWS Services in Scope: SOC](https://aws.amazon.com/compliance/services-in-scope/SOC/), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
31. [Amazon RDS endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/rds-service.html), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
32. [Restoring a DB instance to a specified time for Amazon RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PIT.html), maker (AWS), Amazon Web Services, accessed 22 Sep 2026
33. [Amazon RDS Multi-AZ](https://aws.amazon.com/rds/features/multi-az/), maker (AWS), Amazon Web Services, accessed 22 Sep 2026

**Searched**: "postgresql row level security performance multi-tenant connection pooling" (found [21]); "postgresql logical replication lag high write load" (found [22]; no measurement under a comparable import burst, hence Open Question 2); "mysql 8 row-level security" (found [23]; no native feature); "postgresql certifications SOC 2" (nothing for the software, hence Certifications Not published); "postgresql running cost" (nothing from the maker, hence Running cost Not published); MySQL constraint semantics, attribution, encryption, PITR, queueing, and replicas, and every MongoDB cell beyond transactions, were not searched, hence Not researched.

## Review Checklist

Reviewed by: unreviewed

- [x] Need and Required Capabilities cite project artifacts only; no `[n]` appears in them
- [x] Every required capability has a "Settled by" line and a status from How to Read This Profile
- [x] Every claim cites at the clause or is marked Not published (with the search) or Not researched (with the sibling profile)
- [x] Every figure carries a label, and every mutable fact an as-of date
- [x] The verdict follows the definitions in How to Read This Profile
- [x] The Competitive Landscape scores every named alternative on the same capabilities
- [x] The confidence grade follows the rubric; a design-defining Unknown caps it at Medium
- [x] Every source carries class, author or organisation, publication date where shown, and access date; scoped-version docs are version-pinned
- [x] No benchmark, prototype, or integration result is claimed
- [x] No owner, date, duration, or figure appears that a project artifact does not state
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
<tr><th>Generation prompt</th><td><details><summary>Show the full generation prompt</summary><pre><code># Component Profile Generation Prompt&#10;&#10;Consolidate what is publicly known about one candidate stack component, cite&#10;every claim, and measure it against this project&#x27;s own vision and concerns,&#10;before anyone spikes it or decides on it.&#10;&#10;## Storage Location&#10;&#10;Store at: `docs/helix/00-discover/component-profile-[component-name].md`&#10;&#10;One file per candidate. A decision with six candidates: say PostgreSQL,&#10;MySQL and four managed Postgres providers, is six profiles in six files. Separate files let candidates be researched in parallel, added late,&#10;and revised independently when one maker changes its pricing; a shared file&#10;grows past the point anyone reads it and takes one confidence grade for&#10;claims of very different strength.&#10;&#10;## Purpose&#10;&#10;Answers: **What does this project need from the role, what does this&#10;component do on each of those needs according to the public record, and how&#10;do the alternatives compare on the same needs?**&#10;&#10;The Need gives the reader a way in and tells the research what to look for.&#10;The cited record makes the fit checkable. The landscape lets the ADR compare&#10;candidates from evidence. The Summary, Need, and Required Capabilities&#10;sections are reused word for word by any brief or deck built from the&#10;profile, so they are written for a reader outside the project.&#10;&#10;## Role Boundary&#10;&#10;A profile reads the public record; a [[tech-spike]] runs something and comes&#10;after it, so the spike is spent only on what reading cannot settle. A&#10;[[competitive-analysis]] positions our product in a market; a profile asks&#10;whether someone else&#x27;s component belongs in our stack. A&#10;[[current-state-inventory]] records what already runs and supplies the&#10;incumbent. A [[resource-summary]] summarizes one source; a profile&#10;synthesizes many. The ADR that cites the profiles makes the choice among&#10;candidates.&#10;&#10;## Ownership and Reuse&#10;&#10;A profile belongs to the project whose decision it feeds and lives in that&#10;project&#x27;s Discover directory. Its factual sections (What It Is,&#10;Technology and Operations, Pricing and Licensing, the evidence paragraphs in&#10;Capability Alignment, Sources) are portable: another project may copy them.&#10;Scope, Need, Required Capabilities, the status words, the verdict, and the&#10;Competitive Landscape are not: they name this project&#x27;s artifacts and&#10;decisions, and a copy that keeps them asserts a fit nobody measured. A project&#10;that reuses a profile rewrites those, re-grades Confidence, and re-dates every&#10;source it keeps. The graph has no cross-project edge for this; a project copies the file.&#10;&#10;## Method&#10;&#10;The order matters. Steps 1 to 3 happen before any candidate material is&#10;opened; a profile that starts from the maker&#x27;s site assesses fit against&#10;whatever the maker chose to advertise.&#10;&#10;1. **Write the Need.** Open [[product-vision]], [[business-case]],&#10;   [[principles]], [[concerns]], [[architecture]], and the ADR or spike this&#10;   profile will feed. Write, in a reader&#x27;s words, the system and the role to&#10;   fill, the use cases the role serves, and the goals those use cases&#10;   accomplish, each goal cited to its artifact after the sentence. Name the&#10;   incumbent from [[current-state-inventory]] and why it no longer serves.&#10;   Cite project artifacts only; a `[n]` in this section means the criteria&#10;   were written after the research.&#10;2. **Derive the Required Capabilities.** From the Need and the same&#10;   artifacts, list the capabilities the role must have. Each row names the&#10;   goal it serves, the artifact it comes from, and what evidence in a public&#10;   record would settle it: a documented feature, a published limit, a licence&#10;   clause, an audit report. This &quot;Settled by&quot; column is the research plan.&#10;   A capability no artifact requires goes under Nice to Have or is dropped.&#10;   When several candidates feed one decision, write these two sections once&#10;   and copy them into every profile unchanged.&#10;3. **Fix the scope.** Name the exact component, edition, version line, and&#10;   hosting form, and what the profile excludes. &quot;Postgres&quot; is not a scope;&#10;   &quot;PostgreSQL 18, community distribution, self-hosted or managed&quot; is.&#10;4. **Research capability by capability.** For each row, search the maker&#x27;s&#10;   documentation for the feature, the version that introduced it, and its&#10;   documented limits; then search independent coverage (analysts,&#10;   comparisons, conference talks, issue trackers, post-mortems) for how it&#10;   behaves in practice under the conditions the Need names (a pooled&#10;   connection, a write burst, a region). Record each source with its URL,&#10;   its class (maker, vendor, independent, community), its author or&#10;   organisation, its publication date when shown, and the date you read it.&#10;   Cite the versioned documentation URL for the scoped version. Record the&#10;   search strings you used under Sources, so a Not published cell shows&#10;   where you looked. When two sources disagree, keep both with their dates.&#10;5. **Write the lead.** What It Is gives category, maker or governing body,&#10;   purpose, adoption from an independent source, cadence and support window,&#10;   licence, and built-for use cases, each sentence cited. A reader who stops&#10;   here should be able to say what the thing is.&#10;6. **Write Capability Alignment, one subsection per capability.** State&#10;   what the record shows, citing at the clause, with the version, the&#10;   caveats, and the independent coverage attributed inline by organisation&#10;   and year. Close the row&#x27;s &quot;Settled by&quot; plan (found in [n], or not found&#10;   with the search recorded) and give the status: Met, Unmet, or Unknown.&#10;   Then the verdict, exactly one, by the definitions in How to Read This&#10;   Profile: a design-defining Unknown makes it Undetermined.&#10;7. **Fill the operational and pricing tables.** Every cell cites or says Not&#10;   published. Label every figure. Never derive a price.&#10;8. **Research the alternatives on the same capabilities.** For each&#10;   alternative a reader will ask &quot;why not X?&quot; about, fill one row of the&#10;   Competitive Landscape from that alternative&#x27;s own record, capability by&#10;   capability. Spend a search on each cell before writing Not researched; a&#10;   licence page, a region list, or a docs page is one fetch. A cell you&#10;   still cannot fill says Not researched and names the sibling profile.&#10;   Below the table, one line per alternative: shared ground and the&#10;   divergence this project cares about.&#10;9. **Grade confidence by the rubric.** A design-defining capability left&#10;   Unknown caps the grade at Medium. Say which claims are corroborated, which&#10;   rest on the maker alone, and which have none. Name the weakest area.&#10;10. **Route what the record cannot answer.** Every Unknown that bears on a&#10;    design-defining decision becomes an Open Question with a route: a spike,&#10;    a question to the maker, operator guidance, or a sibling profile. An&#10;    owner, date, duration, or figure appears only when a project artifact&#10;    states it; a scale the project has not set is written as &quot;the project&#x27;s&#10;    tenant count&quot;.&#10;11. **Write the Summary last.** Three sentences a brief can lift: the need,&#10;    the capabilities in one clause each, the verdict with its conditions.&#10;&#10;## Researching Honestly&#10;&#10;The model already knows the component, the maker&#x27;s site is persuasive, and a&#10;confident profile reads as finished. Each of those produces a claim without a&#10;source.&#10;&#10;- **Familiarity is not a source.** A fact you know about the component still&#10;  needs a citation. If you cannot find one, it is Not published, with the&#10;  search recorded.&#10;- **A citation supports the clause next to it.** A licence page cited for a&#10;  feature list, or a security page cited for encryption the page does not&#10;  mention, is a mis-cite; the reader who follows the number finds nothing.&#10;  Cite at the clause and check each number against its page once more&#10;  before closing.&#10;- **Maker material is one voice.** A profile with no independent source is&#10;  Medium at best, however thorough the documentation.&#10;- **&quot;Not published&quot; beats a plausible guess.** A guessed price, a guessed&#10;  region list, a guessed certification becomes a fact in the ADR.&#10;- **The verdict is not the decision.** Conditional fit with named conditions&#10;  is a complete, useful result. Do not round it up to Fit to look decisive,&#10;  and do not recommend a candidate: that is the ADR&#x27;s job.&#10;- **A fit row without an artifact is an opinion.** If nothing in the&#10;  project&#x27;s own documents requires it, it is not a requirement.&#10;- **Hands-on claims do not belong here.** If you find yourself writing &quot;in&#10;  our test&quot;, stop and open a spike.&#10;- **Owners, dates, durations, and scales come from project artifacts.** &quot;The&#10;  platform team needs two weeks&quot; is a plan, and a plan belongs to the&#10;  artifact that owns it. &quot;About 2,000 tenants&quot; is a scale, and it belongs to&#10;  the vision or the business case. A profile names the route.&#10;- **An alternative&#x27;s cell comes from the alternative&#x27;s record.** A&#10;  competitor&#x27;s row filled from memory is a comparison nobody can check.&#10;  Write Not researched when a search found nothing, and record the search.&#10;- **Write the Need for the reader of the brief.** The Need and Required&#10;  Capabilities will be lifted into any deck, brief, or one-pager built from&#10;  this profile. Plain words, no artifact IDs in the sentences, the citation&#10;  after.&#10;&#10;## Inputs&#10;&#10;- The project&#x27;s [[product-vision]], [[business-case]], [[principles]],&#10;  [[concerns]], [[architecture]], and the ADR or spike this profile feeds,&#10;  read first&#10;- [[current-state-inventory]], for the incumbent&#10;- Maker documentation, pricing pages, licence texts, security and trust pages,&#10;  release notes and roadmaps&#10;- Independent coverage: analyst notes, comparisons, conference talks,&#10;  incident reports, issue trackers&#10;- Sibling profiles for adjacent candidates&#10;&#10;## Quality Checks&#10;&#10;- Need and Required Capabilities cite project artifacts only, and every&#10;  capability names its artifact and what would settle it&#10;- Every required capability has a Capability Alignment subsection with a&#10;  Settled by line and a status from How to Read This Profile&#10;- Every claim cites at the clause, or is marked Not published with the&#10;  search recorded, or Not researched with the sibling profile named&#10;- Every figure is labelled, and every mutable fact carries an as-of date&#10;- The verdict follows the definitions in How to Read This Profile; a&#10;  design-defining Unknown makes it Undetermined&#10;- The Competitive Landscape scores every named alternative on the same&#10;  capabilities&#10;- The confidence grade follows the rubric; a design-defining Unknown caps it&#10;  at Medium&#10;- Every source carries class, author or organisation, publication date where&#10;  shown, and access date; scoped-version documentation is version-pinned&#10;- No benchmark, prototype, or integration result is claimed&#10;- No owner, date, duration, or figure appears that a project artifact does&#10;  not state&#10;- No choice among candidates is made</code></pre></details></td></tr>
<tr><th>Template</th><td><details><summary>Show the template structure</summary><pre><code>---&#10;ddx:&#10;  id: component-profile&#10;  authoring:&#10;    home: repo&#10;---&#10;&#10;# Component Profile: [Component Name]&#10;&#10;Desk research on one candidate stack component (a technology, a product, or&#10;a managed provider), consolidated from the public record and measured&#10;against the capabilities this project needs from the role it would fill.&#10;This is research. The choice among candidates lives in an ADR that cites&#10;the profiles; anything the public record cannot settle is a [[tech-spike]].&#10;&#10;One instance per candidate. When one decision has several candidates, write&#10;one profile each and let the ADR compare them. Need and Required Capabilities&#10;are shared by every profile for the same decision and are written once,&#10;before any candidate is researched. The factual sections travel between&#10;projects; Scope, Need, Required Capabilities, Capability Alignment, and the&#10;Competitive Landscape do not.&#10;&#10;## Scope&#10;&#10;- Component: [Name, edition or version line researched]&#10;- Kind: [Technology | Product | Managed provider]&#10;- Would fill: [The role, capability slot, or architectural position it is a candidate for]&#10;- Feeds: [The ADR, spike, or slot decision this profile informs, by id or path]&#10;- Incumbent: [What fills the role today, citing [[current-state-inventory]] where one exists, or *None*]&#10;- Researched: [Date range]&#10;- Excluded: [What this profile deliberately does not cover, and why]&#10;&#10;## Summary&#10;&#10;Three sentences a brief can lift word for word: the need, the required&#10;capabilities in one clause each, and the verdict with its conditions. Written&#10;last, from the sections below, in the words of a reader outside the project.&#10;&#10;[We need a [role] for [use cases] so that [goals]. It must [C1], [C2], and&#10;[C3]. On the public record [component] meets [which], and [which] stay open&#10;pending [what].]&#10;&#10;## How to Read This Profile&#10;&#10;The vocabularies used below, in one place.&#10;&#10;| Word | Where | Means |&#10;|------|-------|-------|&#10;| **Met** | Capability Alignment status | The public record documents the capability as its Required Capabilities row defines it. |&#10;| **Unmet** | Capability Alignment status | The public record contradicts it, or the maker states it is absent. |&#10;| **Unknown** | Capability Alignment status | The record does not settle it; the Open Questions table routes it. |&#10;| **Fit** | Verdict | Every required capability is Met. |&#10;| **Conditional fit** | Verdict | Every required capability is Met or Unknown, and no Unknown is design-defining; each Unknown is an Open Question with a route. |&#10;| **Undetermined** | Verdict | At least one design-defining capability is Unknown; the spike that would settle it is named. |&#10;| **No fit** | Verdict | At least one required capability is Unmet. |&#10;| **Published** | Figures | The maker states it, with source and date. |&#10;| **Third-party estimate** | Figures | Someone other than the maker estimated it; the estimator is named. |&#10;| **Not published** | Figures and claims | Searched and absent; the search is recorded (which pages, which date). |&#10;| **Not researched** | Competitive Landscape cells | Nobody has looked; the sibling profile that would fill the cell is named. |&#10;| **High / Medium / Low** | Confidence | Defined in the Confidence section. |&#10;| **maker / vendor / independent / community** | Sources | Defined in the Sources section. |&#10;&#10;## Need&#10;&#10;Written before the component is researched, from the project&#x27;s own&#10;artifacts, in the words a reader outside the project would use: the system&#10;and the role to fill, the use cases it serves, and the goals those use cases&#10;accomplish, each goal cited to its artifact. Then the incumbent and why it no&#10;longer serves. Cite artifacts after the sentence; keep IDs out of the&#10;sentences themselves.&#10;&#10;[We need a [role] for [use cases] so that [goals]. The role is filled today&#10;by [incumbent], which [why it no longer serves]. [[product-vision]]&#10;§[section]; [[business-case]] §[section].]&#10;&#10;## Required Capabilities&#10;&#10;The criteria. One row per capability the role must have, derived from the&#10;Need and the project&#x27;s artifacts before any candidate is read. Each row says&#10;what evidence in a public record would settle it, so the research has a&#10;target and the reader can check the work. A row cites project artifacts only;&#10;a `[n]` source here means the criteria were written after the research, which&#10;is the failure this order prevents. A capability with no artifact behind it&#10;is a preference and goes under Nice to Have or is dropped.&#10;&#10;| # | Capability | Serves | Comes from | Settled by |&#10;|---|------------|--------|------------|------------|&#10;| C1 | [Capability, in one plain sentence] | [Goal from the Need] | [[product-vision]] / [[concerns]] / [[principles]] / ADR-nnn | [The documented fact or independent measurement that would show it: a feature in the maker&#x27;s docs, a published limit, a licence clause, an audit report] |&#10;&#10;Nice to have: [capabilities the project would welcome and no artifact requires, or *None*]&#10;&#10;## What It Is&#10;&#10;An encyclopedia lead a reader can repeat. First sentence: what the component&#10;is, in its category. Then who makes or governs it, the problem it exists to&#10;solve, and how widely it is used. Then the facts a lead carries: first&#10;release, release cadence and support window, licence in one clause, and the&#10;use cases its own material and independent coverage say it is built for.&#10;Every sentence cites, and a sentence about adoption names the survey and its&#10;population. [n]&#10;&#10;- Category and purpose: [n]&#10;- Maker or governing body: [n]&#10;- Adoption, from an independent source, or Not published: [n]&#10;- Release cadence and support window: [n]&#10;- Licence: [n]&#10;- Built-for use cases: [n]&#10;&#10;## Capability Alignment&#10;&#10;One subsection per required capability, in C-number order. Each states what&#10;the record shows, with the evidence, then closes the &quot;Settled by&quot; plan from&#10;the criteria row and gives the status. Cite at the clause: a version, a&#10;limit, a figure, or a quoted phrase carries its own `[n]`. Mutable facts&#10;(supported versions, regions, prices) carry &quot;as of [date]&quot;. When the maker&#10;and independent coverage disagree, record both with dates; the status is&#10;Unknown unless a later maker statement supersedes.&#10;&#10;### C1. [Capability]&#10;&#10;[What the record shows, two to five sentences, each cited at the clause. Name&#10;the version that introduced the feature, the documented limits and caveats,&#10;and independent coverage of how it behaves in practice, attributed inline&#10;(&quot;a 2026 QueryPlane post reports ...&quot;). If a caveat bears on the Need (pooled&#10;connections, a write burst, a region), say so here.] [n]&#10;&#10;**Settled by**: [the criteria row&#x27;s evidence] found in [n] / not found (searched [pages], [date])&#10;**Status**: Met | Unmet | Unknown&#10;&#10;Other notable capabilities the record documents and no criterion requires:&#10;&#10;| Capability | What the record says | Source |&#10;|------------|----------------------|--------|&#10;| [Capability] | [Specific, checkable statement] | [n] |&#10;| [Capability] | Not published (searched [n], [date]) | none |&#10;&#10;**Verdict**: [Fit | Conditional fit | No fit | Undetermined]. [One sentence&#10;naming the conditions or the deciding gap, using the definitions in How to&#10;Read This Profile.]&#10;&#10;## Technology and Operations&#10;&#10;| Aspect | What the record says | Source |&#10;|--------|----------------------|--------|&#10;| Hosting model | [Self-hosted, managed, or both; regions, as of date] | [n] |&#10;| Integrations | [Protocols, ecosystems and clients that matter for the role] | [n] |&#10;| Data handling | [Residency, encryption, retention, whether customer data trains models] | [n] |&#10;| Certifications | [SOC 2, ISO 27001, HIPAA and the like, as published, with date; or Not published (searched [n], [date])] | [n] |&#10;| Maturity and cadence | [First release, release cadence, support window] | [n] |&#10;| Governance | [Who controls the roadmap: single vendor, foundation, community] | [n] |&#10;| Security process | [Disclosure policy, CVE handling, patch cadence] | [n] |&#10;&#10;## Pricing and Licensing&#10;&#10;Label every figure. Never infer a price.&#10;&#10;| Item | Figure | Label | Source |&#10;|------|--------|-------|--------|&#10;| Licence | [Licence name and what it permits] | Published | [n] |&#10;| [Tier or unit] | [Figure, as of date] | Published / Third-party estimate / Not published (searched [n], [date]) | [n] |&#10;&#10;## Competitive Landscape&#10;&#10;The alternatives a reader will ask about, scored on the same required&#10;capabilities. One column per capability, one row per alternative, the&#10;candidate itself in the first row. A cell the record fills gets the finding&#10;and its source, from that alternative&#x27;s own record. A cell nobody has&#10;researched says **Not researched** and the Profile column names the sibling&#10;profile that would fill it. For a managed service running the same software,&#10;a capability the software supplies is &quot;Inherits [n]&quot; with the provider&#x27;s&#10;page that says which software it runs.&#10;&#10;| Candidate | C1 | C2 | C3 | ... | Profile |&#10;|-----------|----|----|----|-----|---------|&#10;| [This component] | Met [n] | ... | | | this profile |&#10;| [Alternative] | [Finding] [n] / Not researched | ... | | | [[component-profile-name]] or *none yet* |&#10;&#10;Below the table, one line per alternative: the shared ground and the&#10;divergence this project cares about. [n]&#10;&#10;## Confidence&#10;&#10;One grade for the profile:&#10;&#10;| Grade | Means |&#10;|-------|-------|&#10;| **High** | Every design-defining claim is corroborated by the maker&#x27;s material *and* at least one independent source, and no design-defining capability is Unknown. |&#10;| **Medium** | Design-defining claims rest on the maker alone, or a design-defining capability is Unknown, or the independent coverage is older than two major versions. |&#10;| **Low** | Thin public footprint; claims rest on one source or on none. |&#10;&#10;**Grade**: [High | Medium | Low]. [Which claims are corroborated, which rest&#10;on the maker alone, and which have no source. Name the weakest area.]&#10;&#10;## Open Questions&#10;&#10;What the public record cannot answer. Each is a spike candidate, a question&#10;for the maker, a call for operator guidance, or a sibling profile&#x27;s job. An&#10;open question carries no owner, date, duration, or figure that a project&#10;artifact does not state; a scale the project has not set is written as &quot;the&#10;project&#x27;s tenant count&quot;, not as a number.&#10;&#10;| # | Question | Design-defining because | Route |&#10;|---|----------|-------------------------|-------|&#10;| 1 | [Question] | [Which decision turns on it] | [[tech-spike]] / ask maker / operator guidance / [[component-profile-name]] |&#10;&#10;## Sources&#10;&#10;Numbered; cited by number above. Each carries its class, its author or&#10;organisation, its publication or update date when the page shows one, and&#10;the date accessed. For the scoped version, cite the versioned documentation&#10;URL (`/docs/18/`, not `/docs/current/`). Classes:&#10;&#10;- **maker**: the component&#x27;s maker or governing body&#10;- **vendor**: a company that sells hosting or support for the component or a rival&#10;- **independent**: no commercial interest in the component; a named author or organisation and a date&#10;- **community**: a project or forum around the component&#10;&#10;A source with no named author or organisation and no date supports a&#10;descriptive claim only, never a design-defining one.&#10;&#10;1. [Title](URL), class, author or organisation, published [date], accessed [date]&#10;&#10;**Searched**: [the search strings and pages consulted, and which Not&#10;published or Not researched cells each produced]&#10;&#10;## Review Checklist&#10;&#10;Ticked by a named reviewer, recorded on the line; an author ticking their own&#10;boxes is a draft.&#10;&#10;Reviewed by: [name and role from a project artifact, or *unreviewed*]&#10;&#10;- [ ] Need and Required Capabilities cite project artifacts only; no `[n]` appears in them&#10;- [ ] Every required capability has a &quot;Settled by&quot; line and a status from How to Read This Profile&#10;- [ ] Every claim cites at the clause or is marked Not published (with the search) or Not researched (with the sibling profile)&#10;- [ ] Every figure carries a label, and every mutable fact an as-of date&#10;- [ ] The verdict follows the definitions in How to Read This Profile&#10;- [ ] The Competitive Landscape scores every named alternative on the same capabilities&#10;- [ ] The confidence grade follows the rubric; a design-defining Unknown caps it at Medium&#10;- [ ] Every source carries class, author or organisation, publication date where shown, and access date; scoped-version docs are version-pinned&#10;- [ ] No benchmark, prototype, or integration result is claimed&#10;- [ ] No owner, date, duration, or figure appears that a project artifact does not state&#10;- [ ] No choice among candidates is made here</code></pre></details></td></tr>
</tbody>
</table>
