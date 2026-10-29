---
ddx:
  id: helix.design.umf-schemas
  authoring:
    home: repo
  schemas:
    - id: helix.schema-reference
      version: "1.0.0"
      title: Design schema reference
      path: docs/helix/02-design/schemas/schema-reference.umf.yaml
      schemaFormat: umf
      definition: [publishing, SchemaReference]
---

# Design: UMF schemas and their published browser

## Scope and Authority

PRD R-14 and the operator's implementation request govern this change. The
in-tree catalog binds. Design mode applies UMF reuse by default; Contracts and
Data/Solution/Technical Designs retain their existing authority boundaries.
`workflows/references/umf-schemas.md` owns the reference and reuse contract;
`workflows/references/publishing.md` owns the publishing integration.

## Schema Basis

The worked model reuses UMF core 0.10.0 and `umf.ddd` 0.1.0 value-object fields
and equality, as defined by UMF's `spec/extensions/ddd/package.json`. No domain
pack supplies HELIX publication references; `SchemaReference` is a local concept.
It models the five required reference fields. The optional definition selector,
nonempty-string rules, path containment, format enum, source availability,
identity agreement and browser limits remain explicit publication checks in
`documentor.schemas`, not claims inferred from DDD field types. Runtime input
validation does not depend on the browser or UMF SDK. The model is explanatory;
the shared reference contract remains normative for publication behavior.

## Implementation Plan

1. Add the core reuse procedure, reference contract, artifact prompts/templates,
   and conditional blocking review criteria. Preserve historical prose and omit
   irrelevant modeling sections.
2. Add `documentor.schemas`: validate explicit references, retain source bytes,
   deduplicate identities, generate catalog/provenance and copy verified browser
   assets. Integrate Hugo/static/Hextra site assembly and published artifact links.
3. Pin browser 2.0.0 in the site's lockfile. Prepare schema output before local
   and CI Hugo builds. Include original licenses and source downloads.
4. Exercise this model end to end under `/helix/`, including definition selection,
   errors, reproducibility, stale output and source retirement.

## Verification and Completion

Focused Python tests cover discovery, byte preservation, conflicting identities,
invalid selections, paths outside the repository, missing inputs, stale output,
retired sources and browser package integrity. The browser test follows the
published design link and checks its selected definition and embedded index.
Run `just test`, `just test-documentor`, catalog synchronization, a production
Hugo build and the schema browser test. A renderer pass makes no instance or
native-semantic validation claim. No automatic upstream contribution, schema
migration, application runtime dependency or tracker work is in scope.
