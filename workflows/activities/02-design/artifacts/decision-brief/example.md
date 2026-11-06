---
ddx:
  id: DB-001
  type: decision-brief
  authoring:
    home: repo
  links:
    - {id: component-profile-postgresql-reusable, kind: evaluates, rev: example}
---

# DB-001: Which database should the document-search service use?

## Context

A small team is building a document-search service that stores documents
and their metadata and serves interactive queries from a web application. The
team already runs a relational database for its other services and wants to
avoid operating a second kind of store unless the benefit is clear. This brief
covers the choice of database engine for the service. Where it is hosted is a
separate decision and out of scope.

| Bound | Source | Effect on the choice |
|-------|--------|----------------------|
| Transactions must be atomic across a document and its metadata | PRD, Data Integrity | Excludes options without multi-row transactions |
| Metadata varies by document type | PRD, Search | Favors options with a native semi-structured type |
| Team operates one relational engine today | Current state | Adds cost to a second engine |

## Decision

Choose the database engine for the document-search service. The service
owner decides.

## Options

- **Extend the existing relational engine.** Use the engine already in
  production for the service's tables. Evidence: the engine's technology brief.
- **PostgreSQL.** A separate relational engine with a native binary JSON type.
  Evidence: PostgreSQL technology brief (component-profile-postgresql-reusable).
- **Status quo plus a search index.** Keep the current engine and add a
  separate search service for metadata queries. Evidence: none yet.

## Evaluation

| Criterion | Existing engine | PostgreSQL | Existing engine plus search index |
|-----------|-----------------|------------|-----------------------------------|
| Atomic multi-row transactions | Unknown (not researched) | Documented transactions and constraints | Unknown (not researched) |
| Semi-structured metadata | Unknown (not researched) | `jsonb` with indexing and containment operators | Unknown (not researched) |
| Added operating cost | None | A second engine to run | A second service to run |

The only option with cited evidence here is PostgreSQL; the other two need
their own briefs before the comparison is complete.

## Recommendation

**Recommendation**: Do not decide yet. PostgreSQL meets the transaction and
metadata bounds on the public record, but the existing engine has not been
researched, and it carries no added operating cost. Write the existing
engine's technology brief, then re-evaluate.

What would change it: a brief showing the existing engine lacks a native
semi-structured type or multi-row transactions would make PostgreSQL the
recommendation.

## Risks and Unknowns

| Risk or unknown | Bears on | Route |
|-----------------|----------|-------|
| Existing engine not researched | All criteria | Write its technology brief |
| Search-index option has no evidence | All criteria | Write a brief if it stays in scope |

## Evidence

| Reference | Kind | Revision | Used for |
|-----------|------|----------|----------|
| PostgreSQL technology brief (component-profile-postgresql-reusable) | Technology brief | example | Transactions, semi-structured metadata |
