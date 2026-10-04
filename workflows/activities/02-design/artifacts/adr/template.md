---
ddx:
  id: ADR-XXX
  authoring:
    home: repo
---

# ADR-NNN: [Title]
<!-- Filename: ADR-NNN-<decision-name>.md — uppercase ADR, zero-padded 3-digit, one decision per file. -->


| Date | Status | Deciders | Related | Confidence |
|------|--------|----------|---------|------------|
| [YYYY-MM-DD] | [Proposed/Accepted/Deprecated/Superseded] | [Names] | [FEAT-XXX] | [High/Med/Low] |

Accepted records the chosen direction; it does not claim implementation is complete.

## Context

| Aspect | Description |
|--------|-------------|
| Problem | [Specific problem] |
| Current State | [Existing situation] |
| Requirements | [Key requirements driving this] |
| Decision Drivers | [Forces that make this architecture-significant] |

## Decision

We will [decision statement].

**Key Points**: [Point 1] | [Point 2] | [Point 3]

## Alternatives

| Option | Pros | Cons | Evaluation |
|--------|------|------|------------|
| [Option 1] | [Advantages] | [Disadvantages] | [Rejected: reason] |
| [Option 2] | [Advantages] | [Disadvantages] | [Rejected: reason] |
| **[Selected]** | [Advantages] | [Disadvantages + mitigations] | **Selected: reason** |

## Consequences

| Type | Impact |
|------|--------|
| Positive | [Good outcomes] |
| Negative | [Trade-offs, technical debt] |
| Neutral | [Side effects] |

## Risks

| Risk | Prob | Impact | Mitigation |
|------|------|--------|------------|
| [Risk 1] | H/M/L | H/M/L | [Strategy] |

## Validation

| Success Metric | Review Trigger |
|----------------|----------------|
| [Metric 1] | [Condition for reconsideration] |

## Concern Impact

If this decision affects the project's active concerns or overrides a
library practice, note the impact here:

- **Concern selection**: [Does this ADR select, change, or constrain a concern?]
- **Practice override**: [Does this ADR override a library concern practice? If so,
  update `docs/helix/01-frame/concerns.md` Project Overrides with this ADR ref.]
- **No concern impact**: [Delete this section if the ADR has no concern relevance.]

## References

- [PRD section link]
- [Related ADRs]
