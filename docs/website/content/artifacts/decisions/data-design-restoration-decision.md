---
title: "Data Design — Restoration Decision"
slug: data-design-restoration-decision
weight: 270
activity: "Design"
source: "02-design/decisions/data-design-restoration-decision.md"
generated: true
collection: decisions
---
# Data Design — Restoration Decision

> Historical decision; superseded by the worked example at `docs/helix/02-design/data-design.md`.

`data-design` is restored as the canonical design-activity artifact for schema,
storage, access-pattern, and migration design.

## Decision

This artifact is restored rather than retired.

Current HELIX still names `data-design` in the design README, state machine,
and design gate. That intent is also not replaced cleanly by architecture,
contracts, or security documents.

## Why It Exists

- Architecture explains the system shape and component boundaries.
- Contracts define external interface and schema obligations.
- Security architecture defines trust boundaries and controls.
- Data design defines the internal data model, storage strategy, lifecycle,
  access patterns, and migration consequences that implementation and tests
  must follow.

## Canonical Inputs

- `docs/helix/02-design/architecture.md`
- feature-level solution or technical designs when a slice owns specific data changes
- relevant contracts when external schemas constrain internal storage
- `docs/helix/01-frame/compliance-requirements.md` and `docs/helix/02-design/security-architecture.md` when retention, classification, or protection rules shape the model

## Minimum Prompt Bar

- Identify the entities, stores, and key fields that matter to the design.
- Make relationships, cardinality, and lifecycle consequences explicit.
- Document the main read/write access patterns and their performance needs.
- Record integrity, retention, privacy, and classification constraints that
  materially affect the model.
- Define migration and rollback expectations for schema or storage changes.
- Stay at the design level instead of drifting into ORM or query implementation details.

## Minimum Template Bar

- data summary
- entities and stores
- relationships
- access patterns and constraints
- validation and security consequences
- migration strategy

## Canonical Replacement Status

`data-design` is not replaced by `architecture`, `contracts`, or
`security-architecture`. Those artifacts provide context and constraints, but
`data-design` remains the canonical place for data-model structure and
evolution strategy.
