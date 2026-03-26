---
dun:
  id: TD-XXX
  depends_on:
    - US-XXX
    - ADR-XXX
---
# Technical Design: TD-XXX-[story-name]

**User Story**: [[US-XXX]] | **Feature**: [[FEAT-XXX]] | **Solution Design**: [[SD-XXX]]

## Acceptance Criteria

1. **Given** [precondition], **When** [action], **Then** [expected outcome]
2. **Given** [precondition], **When** [action], **Then** [expected outcome]

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

### New: [Component Name]
- **Purpose**: [Why needed]
- **Interfaces**: Input: [receives] / Output: [produces]

## API/Interface Design

```yaml
endpoint: /api/v1/[resource]
method: POST
request:
  type: object
  properties:
    field1: string
response:
  type: object
  properties:
    id: string
    status: string
```

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
- [ ] **API**: [Endpoints to test]
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
