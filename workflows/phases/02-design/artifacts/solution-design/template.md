---
dun:
  id: SD-XXX
  depends_on:
    - FEAT-XXX
---
# Solution Design

**Feature**: [[FEAT-XXX]] | **Artifact**: `docs/helix/02-design/solution-designs/SD-XXX-[name].md`

## Scope

- Feature-level design artifact
- Use for cross-component behavior, main alternatives, domain model, and
  decomposition
- Do not use for one-story implementation details; those belong in `TD-XXX`

## Requirements Mapping

### Functional Requirements

| Requirement | Technical Capability | Component | Priority |
|------------|---------------------|-----------|----------|
| [Business requirement] | [Technical implementation] | [Component] | P0/P1/P2 |

### NFR Impact on Architecture

| NFR | Requirement | Architectural Impact | Design Decision |
|-----|------------|---------------------|-----------------|
| Performance | [Metric] | [What this requires] | [How achieved] |
| Security | | | |
| Scalability | | | |

## Solution Approaches

### Approach 1: [Name]
**Description**: [Overview]
**Pros**: [Advantages]
**Cons**: [Disadvantages]
**Evaluation**: [Selected/Rejected: why]

### Approach 2: [Name]
[Same structure]

**Selected Approach**: [Which and why]

## Domain Model

```mermaid
erDiagram
    %% [Define entities with attributes and relationships]
```

### Business Rules
1. [Rule]: [Description and implementation impact]

## System Decomposition

### Component: [Name]
- **Purpose**: [What it does]
- **Responsibilities**: [List]
- **Requirements Addressed**: [Which requirements]
- **Interfaces**: [How it communicates]

### Component Interactions
```mermaid
graph TD
    %% [Show component relationships]
```

## Technology Rationale

| Layer | Choice | Why | Alternatives Rejected |
|-------|--------|-----|----------------------|
| Language | [Choice] | [Reason] | [Others] |
| Framework | [Choice] | [Reason] | [Others] |
| Database | [Choice] | [Reason] | [Others] |
| Infrastructure | [Choice] | [Reason] | [Others] |

## Traceability

| Requirement ID | Component | Design Element | Test Strategy |
|---------------|-----------|----------------|---------------|
| FR-001 | [Component] | [How addressed] | [How tested] |

### Gaps
- [ ] [Requirement not fully addressed]: [Mitigation]

## Constraints & Assumptions

- **Constraints**: [Technical constraints and their design impact]
- **Assumptions**: [What we assume, risk if wrong]
- **Dependencies**: [External systems, libraries]

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |
