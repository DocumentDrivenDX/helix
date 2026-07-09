---
ddx:
  id: data-flow-analysis
---

# Data Flow Analysis

As-is documentation of one existing business process or data flow: what it
does today, who and what is involved, and what would need to change to
modernize it. Captured during Discover, before any future-state solution is
chosen — the target-state entity model for a system being built belongs in
[[data-design]] (Design phase). One instance covers one flow; a migration
effort typically produces several.

## Flow Summary

- Process name: [Name of the business process or flow]
- Frequency: [How often this runs — daily, weekly, on-demand, event-driven]
- Current state: [Manual / Automated / Hybrid]
- Business value: [Why this process exists — the outcome it produces or protects]

## Actors

| Actor | Type | Role in This Flow |
|-------|------|--------------------|
| [Name] | Person / Automated System | [What they do in this flow] |

## Sources and Sinks

| Direction | System or Location | What It Provides or Receives |
|-----------|---------------------|-------------------------------|
| Source | [System, portal, or export] | [Data provided] |
| Sink | [System, database, or report] | [Data received] |

## Data and Data Structures

| Name | Format | Direction | Key Fields / Schema Notes |
|------|--------|-----------|-----------------------------|
| [Table, file, API, or spreadsheet name] | Table / File / API / Spreadsheet / Other | Input / Output | [Fields, types, or notable structure] |

## Transformations

| Step | What Happens | Performed By |
|------|---------------|--------------|
| 1 | [Processing or business logic applied to the data] | [Actor] |

## Constraints

| Constraint | Detail |
|------------|--------|
| Format | [Expected shape of inputs or outputs, and how brittle it is] |
| Timing | [Deadlines, ordering, or freshness requirements] |
| Volume | [Typical and peak data volume] |
| Access | [What credentials, permissions, or network access this flow requires] |

## Scale and Complexity

| Dimension | Assessment |
|-----------|------------|
| Manual steps | [Count or description] |
| Systems touched | [Count or list] |
| Overall complexity | Low / Medium / High |

## Risks, Assumptions, and Modernization Notes

- **Risks**: [What's fragile, undocumented, error-prone, or likely to break]
- **Assumptions**: [What we're taking on faith about how this flow behaves]
- **Modernization Recommendations**: [What we'd do differently, and why]

## Notes

[Freeform — anything real about this flow that doesn't fit the sections above]

## Cross-References

- [[data-design]] — Design-phase target-state entity model this analysis may
  inform once a future solution is chosen.
