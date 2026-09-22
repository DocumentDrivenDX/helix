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
