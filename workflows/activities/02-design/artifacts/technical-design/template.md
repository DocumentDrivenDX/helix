---
ddx:
  id: TD-XXX
  review:
    self_hash: 081ac39c2360ed0034e2a9bc05b5932fbd2baa2930b605c2ab947bf4548a2015
    deps:
      FEAT-XXX: a685da86c4c18a509196cb163f264af507cc966f804db574070e108a555bdf02
      SD-XXX: ea6f092342409cc3f74e945b3ae421392eb4787113b828331c0fdfab359bf86d
      US-XXX: 48b416257cf7acd8b225b785edcb09a125fed67521af9c8f115ec7dc2fbf23a3
    reviewed_at: "2026-05-15T04:11:24Z"
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

## Review Checklist

Use this checklist when reviewing a technical design:

- [ ] Each governing-story AC-ID (US-{n}-AC{m}) is realized by the technical changes (AC text is not restated here — ADR-009)
- [ ] Technical approach inherits from the parent solution design — no contradictions
- [ ] Key decisions have documented rationale
- [ ] Trade-offs are explicit — what we gain and what we lose
- [ ] Component changes clearly describe current state vs. changes
- [ ] API/interface design references Contract IDs for exact shared surfaces instead of defining schemas inline
- [ ] Data model changes include migration SQL
- [ ] Integration points specify fallback behavior for external dependencies
- [ ] Security section addresses authentication, authorization, and data protection
- [ ] Performance targets are numeric with specific metrics
- [ ] Testing section covers unit, integration, API, and security scenarios
- [ ] Migration and rollback strategy is documented
- [ ] Implementation sequence is ordered with file paths and test paths
- [ ] Design is consistent with governing solution design and feature spec
