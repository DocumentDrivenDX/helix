# Data Design Generation Prompt
Document the data model and access patterns needed to support the design.

## Focus
- Name the main entities, stores, and key fields.
- Make relationships, lifecycle, and integrity constraints explicit.
- Capture the main access patterns and their performance or consistency needs.
- Note privacy, classification, retention, and protection consequences where they
  materially shape the design.
- Define migration and rollback expectations for schema or storage changes.
- Avoid drifting into implementation-specific query or ORM code.

## Completion Criteria
- The model is understandable to another engineer without reading code.
- Key data decisions and constraints are explicit.
- Access patterns and migration strategy are concrete enough to guide
  implementation and tests.
