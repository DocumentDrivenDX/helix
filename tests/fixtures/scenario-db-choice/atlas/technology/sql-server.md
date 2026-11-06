---
ddx:
  id: component-profile-sql-server-reusable
  type: component-profile
  scope: reusable
  status: draft
  authoring:
    home: repo
---

# Technology Brief: Microsoft SQL Server

Desk research on Microsoft SQL Server consolidated from the public record,
independent of any project. Other documents cite it by pinned revision; it
carries no verdict.

## Scope

- Component: Microsoft SQL Server, self-managed (Windows and Linux), 2025
  (17.x) release line; SQL Server 2022 appears only where a lifecycle or
  price figure is stated for it
- Kind: Technology
- Researched: 6 November 2026
- Excluded: Azure SQL Database, Azure SQL Managed Instance, and other
  managed-hosting pricing, regions, and certifications; extensions and tooling
  beyond the database engine; comparison with other databases

## Summary

SQL Server is a commercial relational database from Microsoft, sold in
Enterprise, Standard, Developer, and Express editions, with per-core
licensing and a ten-year support window per release. The public record
documents ACID transactions, row-level security, transparent data encryption,
Always Encrypted, point-in-time restore, Always On availability groups, a
native `json` type, and a `vector` type. Edition limits and preview status
matter: Standard supports only basic availability groups, and the vector index
is a preview feature in SQL Server 2025. Confidence is Medium: design-defining
claims rest on the maker's documentation, with thin independent coverage.

## How to Read This Profile

| Word | Where | Means |
|------|-------|-------|
| **Published** | Figures | The maker states it, with source and date. |
| **Third-party estimate** | Figures | Someone other than the maker reported it; the reporter is named. |
| **Not published** | Figures and claims | Searched and absent; the search is recorded. |
| **High / Medium / Low** | Confidence | Defined in the Confidence section. |
| **maker / vendor / independent / community** | Sources | Defined in the Sources section. |

## What It Is

SQL Server is a relational database engine developed and sold by Microsoft.
The 2025 release (17.x) is described by its maker as a platform offering a
choice of development languages, data types, on-premises or cloud
environments, and operating systems [1]. In the 2025 Stack Overflow Developer
Survey of developers worldwide, Microsoft SQL Server was named by 30.1% of all
respondents and 30.9% of professional developers [24].

- Category and purpose: relational database engine for transactional and
  mixed workloads; the Database Engine covers storing, processing, and
  securing data, replication, full-text search, and tools for relational, XML,
  and JSON data [2]
- Maker or governing body: Microsoft; proprietary product sold by edition [2][19]
- Adoption: 30.1% of all respondents and 30.9% of professional developers in
  the 2025 Stack Overflow Developer Survey [24]
- Release cadence and support window: SQL Server 2025 started 18 November
  2025, mainstream support ends 7 January 2031, extended support ends 7
  January 2036; SQL Server 2022 started 16 November 2022, mainstream ends 12
  January 2028, extended ends 12 January 2033 [3][4]
- Licence: commercial; Enterprise and Standard under a per-core model, with
  Enterprise also in a server-plus-CAL model that is not available for new
  agreements [2][20]
- Built-for use cases: the maker lists transactional processing with ACID
  properties [10], in-database message queuing through Service Broker [17],
  JSON documents beside relational columns [13], and vector similarity search
  alongside other data [14]

## Capabilities and Limits

### Transactions and integrity

A transaction is a logical unit of work that must show atomicity,
consistency, isolation, and durability; once a fully durable transaction
completes, its effects are permanently in place [10]. Supported isolation
levels are `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`,
`SERIALIZABLE`, and the row-versioning levels `READ COMMITTED` with
`READ_COMMITTED_SNAPSHOT` and `SNAPSHOT`; `READ COMMITTED` is the default,
and `READ_COMMITTED_SNAPSHOT` and `ALLOW_SNAPSHOT_ISOLATION` are off by default
for user databases in SQL Server [10]. By default an `INSERT` checks unique,
check, primary key, and foreign key constraints [16]. SQL Server 2025 adds
optimized locking, which the maker says reduces blocking and lock memory
consumption and avoids lock escalation [1].

### Auditing

SQL Server Audit combines a server audit, server audit specifications, and
database audit specifications; targets are a file, the Windows Security event
log, or the Windows Application event log [8]. All editions support
server-level audits, and since SQL Server 2016 SP1 all editions support
database-level audits [8]. The maker cautions that principals in the
`sysadmin` role can tamper with any audit component and `db_owner` members
can tamper with database audit specifications [8]. Changes to TDE status are
tracked under the `DATABASE_OBJECT_CHANGE_GROUP` audit action group [6]. Ledger
for SQL Server is listed in all editions [2]; its mechanics are not described
in the cited pages.

### Access control

Row-level security uses filter predicates and block predicates, defined as
inline table-valued functions and enforced by a security policy created with
`CREATE SECURITY POLICY`; it was first introduced in SQL Server 2016 [5].
Policies apply to `dbo`, `db_owner`, and table owners; if sysadmin or
`db_owner` users need to see all rows, the policy must be written to allow it
[5]. The maker documents side-channel leakage through carefully crafted
queries that use errors, and through collusion with a malicious policy
manager [5]. For applications connecting through a shared login, the
documented pattern sets a user id in `SESSION_CONTEXT` and uses
`@read_only` so the value cannot change until the connection returns to the
pool [5]. Row-level security is listed in all editions, including Express [2].
Column-level permissions are shown with `DENY UPDATE` on a column in the same
page [5]. Microsoft Entra authentication on SQL Server 2022 and later
requires the instance to be enabled by Azure Arc, or to run on an Azure
virtual machine [2][21].

### Encryption in transit

SQL Server uses TLS to encrypt data between an instance and a client; with
TDS 7.x encryption can be optional, while TDS 8.0 (`Encrypt=Strict`) requires
encryption and supports TLS 1.3, which depends on the operating system
version [18]. TDS 8.0 and strict encryption are available from SQL Server
2022; SQL Server 2025 extends TDS 8.0 and TLS 1.3 to components including
availability groups, failover cluster instances, log shipping, linked
servers, and replication, and the maker notes breaking changes for some of
them [1][18].

### Encryption at rest

Transparent data encryption (TDE) encrypts data and log files at the page
level using a database encryption key protected by a certificate or an
extensible key management module; it does not encrypt communication channels
[6]. Backups of a TDE database are encrypted with the same key, so the
certificate must be kept or data is lost; `tempdb` is encrypted automatically
when any user database uses TDE; FILESTREAM data is not encrypted; instant
file initialization is unavailable while TDE is enabled [6]. TDE is listed in
Enterprise and Standard, not Express [2]. Always Encrypted encrypts on the
client so keys are never exposed to the Database Engine; without secure
enclaves, randomized encryption supports no computations, and deterministic
encryption supports only equality operations [7]. The `vector` type is not
supported with Always Encrypted [7][15]. Always Encrypted and Always Encrypted
with secure enclaves are listed in all editions; encrypted backup in Enterprise
and Standard [2].

### Backup and recovery

A point-in-time restore applies a full backup, an optional differential
backup, and each log backup in order, with a `STOPAT` clause on each
`RESTORE LOG`; it applies to the full and bulk-logged recovery models, and in
the bulk-logged model recovery to a point inside a log backup that contains
bulk-logged changes is not possible [9]. The restore point is the latest
transaction commit at or before the stated time [9]. SQL Server 2025 adds the
ZSTD backup compression algorithm and backup to immutable blob storage when
backing up to URL [1]. Online page and file restore is listed in Enterprise
only [2].

### Queue-like workloads

The `READPAST` table hint skips rows locked by other transactions; the maker
states it is primarily used to reduce locking contention when implementing a
work queue that uses a table [16]. It applies only at `READ COMMITTED` or
`REPEATABLE READ`, cannot be combined with `READ_COMMITTED_SNAPSHOT` ON at
`READ COMMITTED` unless `READCOMMITTEDLOCK` is used, and skips row-level but
not page-level locks [16]. Service Broker provides in-database messaging
with queues, `SEND`, and `RECEIVE`, handled within transactions [17]; it is
listed in Enterprise and Standard, and client-only in Express [2].

### Replication and scale-out

An availability group has one primary replica and one to eight secondary
replicas, with up to five synchronous-commit replicas including the primary;
asynchronous commit allows secondaries to lag and some data loss, and
secondary databases are not backups [11]. Secondaries can allow read-only
access, with read-intent routing through a listener [11]. On Windows the
group requires a Windows Server Failover Cluster [11]. In the editions table,
availability groups are listed in Enterprise and basic availability groups in
Standard [2]. A basic availability group is limited to two replicas and one
database, with no read access, backups, or integrity checks on the secondary
[12]. SQL Server 2025 allows full and differential backups on any secondary
replica [1]. Transactional, merge, and snapshot replication, log shipping, and
change data capture are listed in Standard and Enterprise; peer-to-peer
replication in Enterprise only [2]. Table and index partitioning is listed in
all editions [2]; sharding across servers is not described in the cited pages.
Mirroring to Microsoft Fabric OneLake supports SQL Server 2016 to 2022 with
change data capture, and SQL Server 2025 on-premises only with Azure Arc, not
on an Azure VM or Linux [22].

### JSON

SQL Server has stored JSON in `varchar` or `nvarchar` columns since 2016,
with `ISJSON`, `JSON_VALUE`, `JSON_QUERY`, `JSON_MODIFY`, `OPENJSON`, and
`FOR JSON`, and requires database compatibility level 130 or higher [13]. SQL
Server 2025 adds a native `json` type stored in a binary format, `CREATE JSON
INDEX`, and `JSON_CONTAINS`, which the maker states are generally available
[13]. Text-stored JSON is indexed as plain text, with indexes added on
`JSON_VALUE` expressions [13].

### Vector and AI features

The `vector` data type and vector functions are generally available in SQL
Server 2025 [14]. A vector holds a single-precision (`float32`) value per
element, up to 1,998 dimensions; `float16` supports up to 3,996 dimensions
and is a preview in SQL Server 2025, requiring the `PREVIEW_FEATURES`
database scoped configuration [15]. Vector indexes (`CREATE VECTOR INDEX`,
DiskANN-based) and the `VECTOR_SEARCH` function are preview features in SQL
Server 2025 and require `PREVIEW_FEATURES`, while generally available in Azure
SQL Database [1][14]. The maker recommends exact search with `VECTOR_DISTANCE`
for fewer than 50,000 vectors after predicates [14]. Documented limits: no
`PRIMARY KEY`, `FOREIGN KEY`, `DEFAULT`, or `CHECK` constraints on vector
columns, no B-tree or columnstore index on them, and no use in memory-optimized
tables [15]. `AI_GENERATE_EMBEDDINGS`, `AI_GENERATE_CHUNKS`, and
`CREATE EXTERNAL MODEL` are listed for SQL Server 2025 [1]. A dbi services post
on a 2025 preview build reported a vector-indexed table as read-only, a
single integer primary key requirement, no partitioning support, and a
test where 8 of the top 10 approximate results matched the exact results [26].
That post predates general availability; the cited maker pages do not repeat
those restrictions.

### Other documented capabilities

| Capability | What the record says | Source |
|------------|----------------------|--------|
| Regular expressions | `REGEXP_LIKE`, `REGEXP_REPLACE`, `REGEXP_SUBSTR` and related functions added in SQL Server 2025 | [1] |
| Change event streaming | Publishes row-level changes to Azure Event Hubs or Fabric Eventstream; requires `PREVIEW_FEATURES` | [1] |
| Resource governor | Available in Standard and Standard Developer in 2025 | [1] |

**Applicability**: Well suited, on the record, to transactional applications
that need ACID transactions with row-versioning isolation [10], database-tier
row-level security [5], point-in-time restore [9], and JSON beside relational
data [13]. Poorly suited, on the record, to Standard-edition deployments that
need readable secondaries or several databases in one availability group [12],
to workloads needing the vector index as a generally available feature on
SQL Server 2025 [14], and to encrypted columns that must support range
comparison without secure enclaves [7].

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | Windows and Linux; availability groups use a Windows Server Failover Cluster or Pacemaker on Linux; managed offerings not researched here | [11] |
| Integrations | Microsoft Entra authentication via Azure Arc or Azure VM; Fabric mirroring; TDS 8.0 and TLS 1.3 | [2][21][22][18] |
| Data handling | TLS in transit [18]; TDE and Always Encrypted at rest [6][7]; point-in-time restore [9] | [18][6][7][9] |
| Edition limits | Standard: lesser of 4 sockets or 32 cores, 256 GB buffer pool; Express: 1 socket or 4 cores, 1,410 MB buffer pool, 50 GB database; Enterprise: operating system maximum | [1][2] |
| Certifications | SQL Server 2022: Common Criteria EAL4 completed, per a Microsoft Tech Community post of October 2023; SQL Server 2025 Not published (searched [2][3][23], 6 Nov 2026) | [23] |
| Maturity and cadence | SQL Server 2025 started 18 November 2025; mainstream support to 7 January 2031 | [3] |
| Governance | Single vendor, Microsoft | [2] |
| Security process | Not researched; the cited pages do not describe it | [1][2] |

## Pricing and Licensing

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Enterprise, per 2-core pack (2022 price page, open no-level, US estimated retail) | $15,123 | Published | [19] |
| Standard, per 2-core pack (2022 price page) | $3,945 | Published | [19] |
| Standard, server / CAL (2022 price page) | $989 / $230 | Published | [19] |
| Subscription, per 2-core pack per year (2022 price page) | Enterprise $5,434; Standard $1,418 | Published | [19] |
| Pay-as-you-go via Azure Arc (2022 price page) | Standard $73 per core per month; Enterprise $274 per core per month | Published | [19] |
| SQL Server 2025 list price | Not published on the maker page fetched; the 2025 pricing URL returned HTTP 404 and the 2022 page does not cover 2025 (searched [19], 6 Nov 2026) | Not published | [19] |
| SQL Server 2025 per core, as reported | Enterprise $7,562; Standard $1,973, citing the price list | Third-party estimate (Brent Ozar, 18 Nov 2025) | [25] |
| Core licensing minimum | Four licences per physical processor; four per virtual OSE; licensing a virtual OSE requires subscription or active Software Assurance; Enterprise Core with active Software Assurance allows any number of instances | Published | [20] |
| Server + CAL, Enterprise | Limited to 20 cores per instance; not available for new agreements | Published | [2] |
| Developer editions | Enterprise Developer and Standard Developer are free for development and test, not production | Published | [1][2] |
| Express | Free; 50 GB database limit in 2025 | Published | [1][2] |
| Web edition | Discontinued in SQL Server 2025 | Published | [1] |
| Evaluation | 180 days, Enterprise features | Published | [2] |
| Running cost | Not published by the maker (searched [2][19], 6 Nov 2026) | Not published | [2][19] |

## Confidence

| Grade | Means |
|-------|-------|
| **High** | Every design-defining claim is corroborated by the maker's material *and* at least one independent source, and no design-defining capability is Unknown. |
| **Medium** | Design-defining claims rest on the maker alone, or a design-defining capability is Unknown, or the independent coverage is older than two major versions. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: Medium. Adoption is independently corroborated [24], and edition
limits, licensing terms, support dates, and release status are stated by the
maker [1][2][3][20]. The claims behind transactions, row-level security, TDE,
Always Encrypted, point-in-time restore, availability groups, and JSON rest on
the maker's documentation alone [5][6][7][9][10][11][13]. The only independent
coverage of SQL Server 2025 pricing [25] and the vector index [26] is from
consultancies, and [26] covers a preview build. Weakest area: nothing in the
record measures vector-search recall at scale, restore duration, or replica
lag, and SQL Server 2025 list prices are not on a fetched maker page.

## Open Questions

| # | Question | Route |
|---|----------|-------|
| 1 | What are the SQL Server 2025 list prices for Enterprise and Standard? | Ask Microsoft or a licensing partner; no maker figure was fetched |
| 2 | When does the vector index become generally available in SQL Server 2025, and are the preview restrictions lifted? | Ask Microsoft; the cited pages state preview status without a date |
| 3 | How long does a point-in-time restore take for a given database size? | Measure in a [[tech-spike]]; the record carries the recovery point, not a duration |
| 4 | What is availability-group replica lag under a heavy write burst? | Measure in a [[tech-spike]]; no comparable measurement in the record |
| 5 | What throughput effect does row-level security have behind a connection pool? | Measure in a [[tech-spike]] if row-level security is adopted |
| 6 | What is the FIPS 140 and Common Criteria status of SQL Server 2025? | Ask Microsoft; only SQL Server 2022 Common Criteria is in the record |

## Sources

Classes: **maker** (the component's maker or governing body), **vendor** (a
company selling hosting or support for the component or a rival),
**independent** (no commercial interest; named author or organisation and a
date), **community** (a project or forum around the component).

1. [What's New in SQL Server 2025](https://learn.microsoft.com/en-us/sql/sql-server/what-s-new-in-sql-server-2025?view=sql-server-ver17), maker, Microsoft, ms.date 28 Sep 2026, accessed 6 Nov 2026
2. [Editions and Supported Features of SQL Server 2025](https://learn.microsoft.com/en-us/sql/sql-server/editions-and-components-of-sql-server-2025?view=sql-server-ver17), maker, Microsoft, ms.date 19 Nov 2025, accessed 6 Nov 2026
3. [SQL Server 2025 lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/sql-server-2025), maker, Microsoft, accessed 6 Nov 2026
4. [SQL Server 2022 lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/sql-server-2022), maker, Microsoft, accessed 6 Nov 2026
5. [Row-Level Security](https://learn.microsoft.com/en-us/sql/relational-databases/security/row-level-security?view=sql-server-ver17), maker, Microsoft, ms.date 11 Sep 2025, accessed 6 Nov 2026
6. [Transparent Data Encryption (TDE)](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/transparent-data-encryption?view=sql-server-ver17), maker, Microsoft, ms.date 7 Sep 2025, accessed 6 Nov 2026
7. [Always Encrypted](https://learn.microsoft.com/en-us/sql/relational-databases/security/encryption/always-encrypted-database-engine?view=sql-server-ver17), maker, Microsoft, ms.date 28 Jan 2026, accessed 6 Nov 2026
8. [SQL Server Audit (Database Engine)](https://learn.microsoft.com/en-us/sql/relational-databases/security/auditing/sql-server-audit-database-engine?view=sql-server-ver17), maker, Microsoft, ms.date 15 Apr 2026, accessed 6 Nov 2026
9. [Restore a SQL Server Database to a Point in Time (Full Recovery Model)](https://learn.microsoft.com/en-us/sql/relational-databases/backup-restore/restore-a-sql-server-database-to-a-point-in-time-full-recovery-model?view=sql-server-ver17), maker, Microsoft, accessed 6 Nov 2026
10. [Transaction locking and row versioning guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-locking-and-row-versioning-guide?view=sql-server-ver17), maker, Microsoft, accessed 6 Nov 2026
11. [What is an Always On Availability Group?](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/overview-of-always-on-availability-groups-sql-server?view=sql-server-ver17), maker, Microsoft, ms.date 26 Jan 2026, accessed 6 Nov 2026
12. [Basic Availability Groups for a Single Database](https://learn.microsoft.com/en-us/sql/database-engine/availability-groups/windows/basic-availability-groups-always-on-availability-groups?view=sql-server-ver17), maker, Microsoft, ms.date 23 Oct 2025, accessed 6 Nov 2026
13. [Work with JSON Data in SQL Server](https://learn.microsoft.com/en-us/sql/relational-databases/json/json-data-sql-server?view=sql-server-ver17), maker, Microsoft, ms.date 14 Oct 2026, accessed 6 Nov 2026
14. [Vector Search & Vector Index](https://learn.microsoft.com/en-us/sql/sql-server/ai/vectors?view=sql-server-ver17), maker, Microsoft, ms.date 15 Sep 2026, accessed 6 Nov 2026
15. [Vector Data Type](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type?view=sql-server-ver17), maker, Microsoft, ms.date 13 Oct 2026, accessed 6 Nov 2026
16. [Table Hints (Transact-SQL)](https://learn.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver17), maker, Microsoft, ms.date 12 Mar 2026, accessed 6 Nov 2026
17. [SQL Server Service Broker](https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/sql-server-service-broker?view=sql-server-ver17), maker, Microsoft, ms.date 23 Sep 2025, accessed 6 Nov 2026
18. [TDS 8.0](https://learn.microsoft.com/en-us/sql/relational-databases/security/networking/tds-8?view=sql-server-ver17), maker, Microsoft, ms.date 14 Jul 2026, accessed 6 Nov 2026
19. [SQL Server 2022 pricing](https://www.microsoft.com/en-us/sql-server/sql-server-2022-pricing), maker, Microsoft, accessed 6 Nov 2026
20. [SQL Server Product Terms, Per Core model](https://www.microsoft.com/licensing/terms/en-US/productoffering/SQLServer/OVOVS/Availability/351), maker, Microsoft, accessed 6 Nov 2026
21. [Set up Microsoft Entra Authentication with App Registration, SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/entra-authentication-setup-tutorial?view=sql-server-ver17), maker, Microsoft, ms.date 18 Nov 2025, accessed 6 Nov 2026
22. [Microsoft Fabric Mirrored Databases From SQL Server](https://learn.microsoft.com/en-us/fabric/mirroring/sql-server), maker, Microsoft, ms.date 5 Nov 2025, accessed 6 Nov 2026
23. [SQL Server 2022 Common Criteria EAL4 certification](https://techcommunity.microsoft.com/blog/sqlserver/sql-server-2022-common-criteria-eal4-certification/3954247), maker, Microsoft (Wolfgang-Peter), published 13 Oct 2023, updated 14 Oct 2023, accessed 6 Nov 2026
24. [Stack Overflow Developer Survey 2025: Technology](https://survey.stackoverflow.co/2025/technology), independent, Stack Overflow, published 2025, accessed 6 Nov 2026
25. [SQL Server 2025 Is Out, and Standard Goes Up to 256GB RAM, 32 Cores!](https://www.brentozar.com/?p=356251), vendor, Brent Ozar (a SQL Server consultancy), published 18 Nov 2025, accessed 6 Nov 2026
26. [SQL Server 2025 vector indexes semantic search performance](https://www.dbi-services.com/blog/sql-server-2025-vector-indexes-semantic-search-performance/), vendor, dbi services, Hocine Mechara, published 20 Aug 2025, accessed 6 Nov 2026

**Searched**: "SQL Server 2025 pricing Enterprise Standard per core 2 core pack price Microsoft" (found [25]; the maker 2025 pricing URL returned HTTP 404, hence SQL Server 2025 list price Not published on a maker page; reseller and datasheet-copy results were not cited); "SQL Server 2025 licensing guide per-core minimum four cores" (found [20]); "SQL Server 2025 vector index preview DiskANN independent review limitations" (found [26]; no independent review, hence Confidence Medium); "SQL Server compliance certifications Common Criteria FIPS 140" (found [23] for SQL Server 2022; nothing current for SQL Server 2025 or FIPS 140-3, hence Certifications Not published for 2025); the vulnerability disclosure process was not searched for, hence Security process Not researched.
