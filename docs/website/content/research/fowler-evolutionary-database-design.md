---
title: "Fowler Evolutionary Database Design"
slug: fowler-evolutionary-database-design
generated: true
---
> **Source identity**:

```yaml
ddx:
  id: resource.fowler-evolutionary-database-design
```

# Fowler Evolutionary Database Design

## Source

- URL: https://martinfowler.com/articles/evodb.html
- Accessed: 2026-05-12

## Summary

Martin Fowler describes evolutionary database design as a set of practices for
changing databases safely as software evolves. The guidance emphasizes
version-controlled database artifacts, migration scripts, close collaboration
between developers and database specialists, automated migration tooling, and
frequent integration of database changes.

## Relevant Findings

- Database schemas and data both need managed evolution.
- All database changes should be captured as migrations.
- Database artifacts should be version controlled with application code.
- Migration practices need to account for legacy data and data movement, not
  only schema changes.
- Database design should evolve with the application while preserving data
  integrity and deployability.

## HELIX Usage

This resource informs the Data Design artifact. HELIX uses it to keep data
models explicit about schema evolution, data migration, rollback expectations,
and implementation/test consequences.

## Authority Boundary

This resource supports database evolution and migration discipline. It does
not replace project-specific data modeling, security classification,
performance testing, or datastore selection.
