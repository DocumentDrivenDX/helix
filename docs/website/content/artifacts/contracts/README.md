---
title: "Contracts"
slug: README
weight: 250
activity: "Design"
source: "02-design/contracts/README.md"
generated: true
collection: contracts
---
# Contracts

`contracts` is restored as the canonical design-activity artifact for normative
interface and schema specifications that another team can implement against
directly.

## Decision

This artifact is restored rather than retired.

Current HELIX already depends on contract-shaped documents in live repo state:

- `CONTRACT-001` defines the DDx / HELIX ownership boundary
- `CONTRACT-002` defines HELIX execution-document conventions
- `API-001` defines the tracker mutation surface

Those documents carry a distinct responsibility that is not replaced cleanly by
ADRs, solution designs, or technical designs.

## Why It Exists

- ADRs record why an architectural decision was made.
- Solution designs explain the feature-level approach.
- Technical designs scope one bounded slice of implementation work.
- Contracts define the authoritative interface, schema, and error semantics
  that another team, tool, or service can implement against directly.

## Canonical Scope

Use a contract for normative specifications such as:

- CLI and library mutation surfaces
- HTTP or RPC request/response interfaces
- protocol or event payload schemas
- data exchange formats and validation rules
- precedence, ordering, and conflict semantics
- error codes, retry behavior, and recovery expectations

## Naming Guidance

`CONTRACT-XXX` is the canonical prefix for general interface, protocol, schema,
and boundary contracts.

`API-XXX` remains an allowed subtype when the contract is specifically centered
on an API surface. Both prefixes must meet the same completeness bar and live in
the same `docs/helix/02-design/contracts/` directory.

## Minimum Prompt Bar

- Start from the governing requirement, design, or ADR rather than inventing a
  parallel design narrative.
- Specify exact keys, fields, types, units, enums, ranges, and requiredness
  where relevant.
- Define precedence, ordering, versioning, and compatibility rules explicitly.
- Define error semantics, failure modes, and recovery expectations.
- Include concrete examples and validation hooks that tests can execute.
- Keep the document implementation-independent enough that another team could
  build against it without inheriting feature-level or code-level baggage.

## Minimum Template Bar

- purpose and scope
- related governing artifacts
- normative surface definitions
- precedence or compatibility rules
- error semantics
- worked examples
- validation checklist

## Canonical Replacement Status

`contracts` is not replaced by ADRs, solution designs, or technical designs.
Those artifacts govern why a contract exists and where it applies, but the
contract remains the canonical normative specification.
