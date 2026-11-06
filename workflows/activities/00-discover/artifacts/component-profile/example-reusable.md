---
ddx:
  id: component-profile-postgresql-reusable
  type: component-profile
  scope: reusable
  authoring:
    home: repo
---

# Technology Brief: PostgreSQL

Desk research on PostgreSQL consolidated from the public record, independent
of any project. Other documents cite it by pinned revision; it carries no
verdict.

## Scope

- Component: PostgreSQL, community distribution, 16 release line
- Kind: Technology
- Researched: 22 September 2026
- Excluded: managed-hosting pricing, regions, and certifications; extensions;
  comparison with other databases

## Summary

PostgreSQL is a community-governed, open-source object-relational database
with ACID transactions, declarative constraints, built-in replication, and a
five-year support window per major version. The public record documents
strong transactional, access-control, recovery, and replication mechanisms,
with replica delay and row-security pooling as the caveats independent
coverage raises. Confidence is Medium: the design-defining claims rest mostly
on the maker's documentation.

## How to Read This Profile

| Word | Where | Means |
|------|-------|-------|
| **Published** | Figures | The maker states it, with source and date. |
| **Third-party estimate** | Figures | Someone other than the maker estimated it; the estimator is named. |
| **Not published** | Figures and claims | Searched and absent; the search is recorded. |
| **High / Medium / Low** | Confidence | Defined in the Confidence section. |
| **maker / vendor / independent / community** | Sources | Defined in the Sources section. |

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

## Capabilities and Limits

### Transactions and integrity

A PostgreSQL transaction is atomic: from the point of view of other
transactions it either happens completely or not at all, its updates are
logged to permanent storage before it is reported complete, and its
intermediate states are invisible to other transactions until it commits
[12]. Declarative constraints cover check, not-null, unique, primary key,
foreign key, and exclusion constraints [13].

### Auditing

Row-level trigger functions run before or after an insert, update, or delete
and see both the old and new row; the documentation's own example writes an
audit row carrying the operation, time, user, and changed row into a separate
table [14]. The audit design is the application's; the record shows the
mechanism exists.

### Access control

Privileges can be granted on specific columns, and only the object's owner or
a superuser can grant or revoke [15]. Row security policies, added in
PostgreSQL 9.5 [3], restrict per role which rows a query returns or a command
touches; superusers and roles with `BYPASSRLS` always bypass them, and table
owners bypass them unless the table is set to `FORCE ROW LEVEL SECURITY` [2].
A 2026 QueryPlane post names an application connecting as the owning role,
with policies silently ignored, as the most common production pitfall, and
reports that a tenant set with plain `SET` instead of `SET LOCAL` persists
across a pooled connection into the next request [21].

### Encryption in transit

Native SSL support encrypts client and server communication, enabled with the
`ssl` parameter and a server certificate and key, and client certificates can
be required through `clientcert=verify-ca` or `verify-full` [16]. The cited
pages do not describe encryption at rest as a server feature.

### Backup and recovery

Continuous archiving combines a file-system-level backup with archived
write-ahead log files; replay can stop at any point, so the database can be
restored to its state at any time since the base backup, and the technique
restores an entire cluster, never a subset [17].

### Queue-like workloads

`SELECT ... FOR UPDATE SKIP LOCKED` skips any selected row that cannot be
locked immediately; the documentation says the resulting view is inconsistent
and unsuitable for general work, and names its use as avoiding lock
contention with multiple consumers accessing a queue-like table [18].

### Replication and scale-out

Hot standby lets clients run read-only queries on a standby that replays the
primary's write-ahead log; data on the standby takes some time to arrive, so
the standby is eventually consistent with the primary [19]. Built-in logical
replication publishes selected tables in commit order, since version 10 [4][5].
A Percona post updated in April 2024 names long transactions, network
congestion, slow disk, and too few WAL senders under heavy transaction load as
causes of replication lag [22]. Declarative partitioning splits one table
within one server by range, list, or hash; no cross-server sharding is
described [10].

### Other documented capabilities

| Capability | What the record says | Source |
|------------|----------------------|--------|
| Semi-structured data | `jsonb` stores JSON in a decomposed binary form that is faster to process than `json`, supports indexing, and adds containment and existence operators | [9] |
| Security process | Coordinated disclosure through security@postgresql.org; the project assigns its own CVEs; fixes ship in minor releases | [7] |

**Applicability**: Well suited to general transactional applications that
need ACID transactions, declarative constraints, and mixed relational and
document data [11][9][12][13]. Poorly suited, on the record, to workloads that
need cross-server sharding from the database itself [10], or reads that
cannot tolerate replica delay [19].

## Technology and Operations

| Aspect | What the record says | Source |
|--------|----------------------|--------|
| Hosting model | Runs on all major operating systems; also offered as managed services by cloud providers (not researched here) | [11] |
| Integrations | SQL:2023 Core conformance to at least 170 of 177 mandatory features as of version 18 | [11] |
| Data handling | TLS in transit from the software [16]; at-rest encryption, backups, and retention are not described in the cited pages | [16] |
| Certifications | Not published for the software (searched [7][11], 22 Sep 2026) | [7][11] |
| Maturity and cadence | Origins 1986; one major release a year; each supported for five years; version 16 supported until 9 November 2028 | [6][11] |
| Governance | Community project under the PostgreSQL Global Development Group; committers and a core team; no company named as controlling the roadmap | [8] |
| Security process | Coordinated disclosure; the project is its own CVE Numbering Authority; fixes in minor releases | [7] |

## Pricing and Licensing

| Item | Figure | Label | Source |
|------|--------|-------|--------|
| Licence | PostgreSQL Licence: use, copy, modify, and distribute for any purpose, without fee | Published | [1] |
| Software cost | None | Published | [1] |
| Running cost | Not published by the maker (searched [1][11], 22 Sep 2026)| Not published | [1][11] |

## Confidence

| Grade | Means |
|-------|-------|
| **High** | Every design-defining claim is corroborated by the maker's material *and* at least one independent source, and no design-defining capability is Unknown. |
| **Medium** | Design-defining claims rest on the maker alone, or a design-defining capability is Unknown, or the independent coverage is older than two major versions. |
| **Low** | Thin public footprint; claims rest on one source or on none. |

**Grade**: Medium. Adoption [20] and row-security practice [21] are
independently corroborated, and licence, governance, and release policy are
stated by the maker [1][6][8]. The claims behind transactions, constraints,
triggers, continuous archiving, and `SKIP LOCKED` rest on the maker's
documentation alone [12][13][14][17][18], and the only independent replication
coverage [22] is a vendor post that predates version 17. Weakest area: nothing
in the record measures restore duration or replica lag under load.

## Open Questions

| # | Question | Route |
|---|----------|-------|
| 1 | How long does a point-in-time restore take for a given database size? | Measure in a [[tech-spike]]; the record carries the recovery point, not a duration |
| 2 | What replica lag appears under a heavy write burst? | Measure in a [[tech-spike]]; no comparable measurement in the record |
| 3 | Does row-security throughput hold behind a connection pool? | Measure in a [[tech-spike]] if row security is adopted |

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

**Searched**: "postgresql row level security performance multi-tenant connection pooling" (found [21]); "postgresql logical replication lag high write load" (found [22]); "postgresql certifications SOC 2" (nothing for the software, hence Certifications Not published); "postgresql running cost" (nothing from the maker, hence Running cost Not published).
