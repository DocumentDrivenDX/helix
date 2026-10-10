# Design Plan: {{scope}}

Use the sections needed to explain this plan. Omit irrelevant sections rather
than adding `N/A`; retain a section when its requirement applies.

**Date**: {{YYYY-MM-DD}}
**Decision state**: {{Draft|Approved}}

## Problem Statement

{{What problem does this solve? Who benefits?}}

## Requirements

### Functional

{{What the system must do}}

### Non-Functional

{{Performance, scalability, reliability targets}}

### Constraints

{{Technology, timeline, compliance constraints}}

## Architecture Decisions

### Decision 1: {{title}}

- **Question**: {{what needs to be decided}}
- **Alternatives**: {{list with pros/cons}}
- **Chosen**: {{selected option}}
- **Rationale**: {{why this was chosen}}

## Interface Contracts

{{APIs, CLIs, configuration surfaces, file formats}}

## Data Model

{{Entities, relationships, storage, migration strategy}}

## Error Handling

{{Error categories, retry policies, fallback behavior}}

## Security

{{Attack surfaces, auth, authz, data protection}}

## Test Strategy

- **Unit**: {{critical paths to test}}
- **Integration**: {{cross-component verification}}
- **E2E**: {{user-facing scenario coverage}}

## Implementation Plan

### Dependency Graph

{{Work slices and their ordering}}

### Work Breakdown (optional)

{{Ordered steps with acceptance criteria; tracker items only when explicitly selected}}

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| {{risk}} | {{H/M/L}} | {{H/M/L}} | {{strategy}} |

## Observability

{{Logging, metrics, alerting}}

## Governing Artifacts

{{Cross-references to vision, PRD, feature specs, architecture docs}}
Name the vision or requirements this plan advances when relevant.
