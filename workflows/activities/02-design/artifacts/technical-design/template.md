---
ddx:
  id: TD-XXX
  authoring:
    home: repo
---

# Technical Design: TD-XXX-[story-name]

**User Story**: [[US-XXX]] | **Feature**: [[FEAT-XXX]] | **Solution Design**: [[SD-XXX]]

## Scope

- Story-level design artifact
- Use for one vertical slice or one bounded implementation story
- Must inherit the broader approach from the parent solution design
- Do not redefine cross-component architecture here; that belongs in `SD-XXX`
- Governing artifacts: [User Story, Solution Design, Contracts, Concerns]

## Technical Approach

**Strategy**: [Brief description]

**Key Decisions**:
- [Decision]: [Rationale]

**Trade-offs**:
- [What we gain vs. lose]

## Component Changes

### Modified: [Component Name]
- **Current State**: [What exists]
- **Changes**: [What changes]
- **Files**: `[path]`

### New: [Component Name]
- **Purpose**: [Why needed]
- **Interfaces**: Input: [receives] / Output: [produces]
- **Files**: `[path]`

## API/Interface Design

Reference the governing Contract for any exact shared API, CLI, event, schema,
config, telemetry, or adapter surface. This TD may describe story-level usage
and local wiring, but it must not define endpoints, commands, flags, payload
fields, status codes, error semantics, or adapter signatures inline.

| Surface | Governing Contract | Story-Level Usage |
|---------|--------------------|-------------------|
| [API/CLI/event/schema] | [CONTRACT-XXX or API-XXX] | [How this story uses it] |

## Data Model Changes

```sql
-- New tables or schema modifications
CREATE TABLE [table_name] (
    id UUID PRIMARY KEY,
    [columns]
);
```

## Integration Points

| From | To | Method | Data |
|------|-----|--------|------|
| [Source] | [Target] | [REST/Event/Direct] | [What data] |

### External Dependencies
- **[Service]**: [Usage] | Fallback: [If unavailable]

## Security

- **Authentication**: [Required auth level]
- **Authorization**: [Required permissions]
- **Data Protection**: [Encryption/masking]
- **Threats**: [Specific threats and mitigations]

## Performance

- **Expected Load**: [Requests/sec, data volume]
- **Response Target**: [Milliseconds]
- **Optimizations**: [Caching, indexing, etc.]

## Testing

- [ ] **Unit**: [What to test]
- [ ] **Integration**: [What integrations to test]
- [ ] **Contract**: [CONTRACT/API IDs and story-specific cases to test]
- [ ] **Security**: [Security scenarios]

## Migration & Rollback

- **Backward Compatibility**: [Strategy]
- **Data Migration**: [Required migrations]
- **Feature Toggle**: [Enable/disable mechanism]
- **Rollback**: [Steps to reverse]

## Implementation Sequence

1. [What to build first] -- Files: `[paths]` -- Tests: `[paths]`
2. [What to build next]
3. [Integration and verification]

**Prerequisites**: [Dependencies that must be complete first]

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk] | H/M/L | H/M/L | [Strategy] |
