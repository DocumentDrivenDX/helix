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
