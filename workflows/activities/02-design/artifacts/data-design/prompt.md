# Data Design Generation Prompt
Document the data model and access patterns needed to support the design.

## Reference Anchors

Use this local resource summary as grounding:

- `docs/resources/fowler-evolutionary-database-design.md` grounds schema
  evolution, versioned migrations, data movement, and rollback expectations.

## Focus
- Name the main entities, stores, and key fields.
- Make relationships, lifecycle, and integrity constraints explicit.
- Capture the main access patterns and their performance or consistency needs.
- Note privacy, classification, retention, and protection consequences where they
  materially shape the design.
- Define migration and rollback expectations for schema or storage changes.
- Avoid drifting into implementation-specific query or ORM code.

## Role Boundary

Data Design is not the full architecture or implementation plan. It explains
the data model, storage responsibilities, access patterns, integrity/security
constraints, and migration consequences that technical designs must honor.

## Completion Criteria
- The model is understandable to another engineer without reading code.
- Key data decisions and constraints are explicit.
- Access patterns and migration strategy are concrete enough to guide
  implementation and tests.

## UMF Schema Reuse

Apply `workflows/references/umf-schemas.md` for schema, structured-interface, or
domain-model work. Inspect applicable UMF core, extensions, and domain packs;
reuse or compose by default. Record pinned sources, local additions, specific
exceptions, and semantic/projection limits. Declare `ddx.schemas` references to
the authoritative local sources so publication can render them in the UMF
browser. Contracts own exact shared surfaces; designs reference them.

## Machine-readable relational tables (when applicable)

For relational designs, keep one upstream UMF TableSpec YAML per table under
`docs/helix/02-design/umf/tables/` (or name the project's chosen specs directory).
Use the upstream UMF project's TableSpec 1.0 format: `version: "1.0"`,
`table_name`, `columns`, primary/unique keys, and
`relationships.foreign_keys` (`column`, `references_table`, `references_column`).
The YAML owns exact columns, types, keys and foreign keys; this document owns
rationale, access patterns, transactions and migration decisions. Summaries link
the specs; change them in the same revision rather than maintaining a second
independent schema. Shared interfaces still follow the Contract ownership rule.

Declare local sources through `ddx.schemas` with `schemaFormat: tablespec`
(see `workflows/references/umf-schemas.md`), or select documentor's
`umf-tablespec` trait for automatic table discovery. Install the pinned
`@documentdrivendx/umf-schema-browser` version required by documentor in the
site's locked dependencies, then run `documentor build --root .` to generate
the table reference and publish the schema browser. The upstream UMF browser
is the tool named here; tablespec guidebook remains for tablespec pipelines.
Validate the YAML with the upstream validator supported by the project's pinned
UMF version, and check FK targets plus prose/spec agreement. Rendering a browser
is publication evidence, not schema validity or a database migration. Record the
exact validation and browser build commands and observed results in the design.
Skip this section with a reason when no relational model is in scope; a planned
relational application needs specs even before application code exists.
