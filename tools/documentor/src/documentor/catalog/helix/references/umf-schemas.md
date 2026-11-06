# UMF schemas in design

Before introducing or changing a schema, structured interface, or domain model,
inspect applicable Unified Modeling Fabric (UMF) core definitions, extensions,
and domain packs. Reuse suitable definitions by default, then compose, then
extend locally. Propose generally useful additions upstream; use a documented
alternative when UMF does not fit. This is a core design practice, independent
of concern selection. Narrative-only work needs no schema artifact.

Record the inspected source and release, the reused concepts, local additions,
and the specific gaps behind an alternative. Package availability alone is not
evidence of semantic support. Preserve native meaning, opaque rules, unknown
metadata, and reported projection losses. Unsupported constraints need explicit
implementation/tests or a bounded spike. Adoption for design does not require
an application runtime dependency.

## One authority per shape

The machine-readable source owns its declared structure. A Contract references
that source and owns behavior, errors, compatibility, and any rules the schema
cannot express. Solution Designs explain domain choices; Technical Designs
explain application and implementation. Neither redefines the Contract's exact
shared fields. Generate supported types, validators, and reference views from
the same source; state which rules each actually enforces.

## Discoverable references

When a design introduces or consumes a schema, declare `ddx.schemas` in its
existing frontmatter. Paths are repository-relative local JSON/YAML sources;
pin upstream inputs in the repository rather than fetching floating content
during publishing. Each entry requires nonempty string `id`, `version`, `title`,
`path`, and `schemaFormat`. Quote versions. Supported browser formats are `umf`,
`json-schema`, `tablespec`, and `artifact-collection`. Other native formats may
be retained through an applicable UMF extension; do not relabel raw native
sources as UMF. An unsupported rendering format remains a documented gap.

```yaml
ddx:
  schemas:
    - id: example.customer
      version: "1.0.0"
      title: Customer
      path: schemas/customer.umf.yaml
      schemaFormat: umf
      definition: [customers, Customer]
```

`definition` is optional and selects an existing `[moduleId, elementId]` in a
UMF source. Catalog identity is `<id>@<version>`; references sharing that identity
must agree on source bytes, path, title, and format. Different versions coexist.
Declare each needed companion/resource as a reference too; publishing does not
discover external dependencies by following network links.

## Readiness and publication

For applicable work, review requires evidence of UMF reuse or a specific
exception, resolved reference identities, explicit authority and versioning,
and reproducible checks of supported semantics and examples. Schema syntax,
browser rendering, instance validation, and semantic compatibility are separate
claims. Historical documents without references need no bulk migration.

The guide publisher collects explicit references from the active HELIX root,
the guide output, and existing pages selected for publication,
publishes source bytes and provenance, and generates a UMF browser catalog.
Published designs link to the selected schema/definition. The schema index
embeds the pinned UMF schema browser and offers original-source downloads.
Missing sources, conflicting identities, bad definition selections, missing
browser assets, and stale generated output fail publication checks. See
`workflows/references/publishing.md` for installation and site commands.
