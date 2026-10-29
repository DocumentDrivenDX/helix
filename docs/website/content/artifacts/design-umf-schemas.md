---
title: "Design: UMF schemas and their published browser"
slug: design-umf-schemas
weight: 450
activity: "Design"
source: "02-design/design-umf-schemas.md"
generated: true
---

> **Example from HELIX's own docs.** This generated page comes from `docs/helix/`. Use it to see the method in practice; start with the [artifact-type catalog](/artifact-types/) for reusable templates. Historical plans and reports may describe retired architecture.

> **Source identity** (from `02-design/design-umf-schemas.md`):

```yaml
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
```


<ul class="design-schemas"><li><a href="../../schemas/explorer.html#schema=helix.schema-reference%401.0.0&amp;definition=%5B%22publishing%22%2C%22SchemaReference%22%5D">Explore schema: Design schema reference</a> (version 1.0.0)</li></ul>
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

Publication owns only its marked index and inventoried generated files. It
refuses unowned output collisions, preserves unrelated site files, and retires
only unchanged generated files. Discovery includes rendered guide references;
standalone and integrated commands share target-aware output resolution. Invalid
schema metadata must produce an actionable command error rather than a traceback.
Automatic table discovery applies browser limits only to identified TableSpecs.

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

The embedded browser follows the microsite’s resolved theme on load and live changes, preserving the selected schema and definition. The standalone explorer honors the saved site preference and otherwise follows the system theme. Trait delegation uses the same resolution during planning and rendering; adopted pages selected by mapping or glob contribute schema references. Invalid UMF collection shapes produce source-specific command errors.
